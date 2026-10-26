
#!/usr/bin/env python3
"""
TS6 Droid NL
PTT Connect-achtige ontvangst + 3-tonige rogerpiep.

Volgorde:
1. maak_nederlands.py
2. maak_32_64_bit.py
3. maak_ptt_zijknop.py
4. maak_rogerpiep.py
5. Dit script

PTT-knoppen en aan/uit-instelling blijven behouden.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AUDIO = ROOT / (
    "app/src/main/kotlin/dev/tsdroid/"
    "bridge/AudioBridge.kt"
)

GRADLE = ROOT / "app/build.gradle.kts"

if not AUDIO.is_file():
    raise SystemExit("FOUT: AudioBridge.kt niet gevonden")

if not GRADLE.is_file():
    raise SystemExit("FOUT: build.gradle.kts niet gevonden")

source = AUDIO.read_text(encoding="utf-8")
gradle = GRADLE.read_text(encoding="utf-8")


def vervang(oud, nieuw):
    global source

    aantal = source.count(oud)

    if aantal != 1:
        raise SystemExit(
            f"FOUT: verwacht 1 overeenkomst, vond {aantal}: "
            f"{oud[:90]!r}"
        )

    source = source.replace(oud, nieuw, 1)


# ==========================================
# 1. Stabielere ontvangstbuffers
# ==========================================

vervang(
    "private const val MAX_QUEUE_FRAMES = 10",
    "private const val MAX_QUEUE_FRAMES = 16"
)

vervang(
    "private const val TRACK_BUFFER_FRAMES = 8",
    "private const val TRACK_BUFFER_FRAMES = 12"
)


# ==========================================
# 2. PTT Connect-audio-instellingen
# ==========================================

vervang(
    ".setUsage(AudioAttributes.USAGE_GAME)",
    ".setUsage(AudioAttributes.USAGE_VOICE_COMMUNICATION)"
)

vervang(
    ".setBufferSizeInBytes(maxOf(minBuf, FRAME_SIZE_BYTES * TRACK_BUFFER_FRAMES))",
    """.setTransferMode(AudioTrack.MODE_STREAM)
            .setBufferSizeInBytes(
                maxOf(
                    minBuf * 2,
                    FRAME_SIZE_BYTES * TRACK_BUFFER_FRAMES
                )
            )"""
)

vervang(
    """        audioTrack = buildAudioTrack(minBuf, lowLatency = true)
        if (audioTrack?.state != AudioTrack.STATE_INITIALIZED) {
            // Some devices reject PERFORMANCE_MODE_LOW_LATENCY for voice-usage
            // tracks — fall back to a plain track rather than going silent
            Log.w(TAG, "Low-latency voice track not initialized; retrying without performance mode")
            audioTrack?.release()
            audioTrack = buildAudioTrack(minBuf, lowLatency = false)
        }""",
    """        audioTrack = buildAudioTrack(
            minBuf,
            lowLatency = false
        )

        if (audioTrack?.state != AudioTrack.STATE_INITIALIZED) {
            Log.w(TAG, "Standaard audiomodus mislukt")
            audioTrack?.release()
            audioTrack = buildAudioTrack(
                minBuf,
                lowLatency = true
            )
        }"""
)


# ==========================================
# 3. Stabielere spraakontvangst
# ==========================================

begin = source.find(
    "    private fun startPlaybackLoop() {"
)

einde = source.find(
    "    /**\n"
    "     * Queue an opus packet for a specific user.",
    begin
)

if begin < 0 or einde < 0:
    raise SystemExit(
        "FOUT: ontvangstaudio niet gevonden"
    )

nieuwe_audio = r'''
    private fun startPlaybackLoop() {
        playbackJob = playbackScope.launch {

            runCatching {
                android.os.Process.setThreadPriority(
                    android.os.Process.THREAD_PRIORITY_AUDIO
                )
            }

            val mixed = FloatArray(FRAME_SIZE_SAMPLES)
            val decoded = ShortArray(FRAME_SIZE_SAMPLES)
            val output = ShortArray(FRAME_SIZE_SAMPLES)

            // Korte buffer tegen netwerkvariatie.
            val started = HashSet<Int>()
            val waitingSince = HashMap<Int, Long>()
            val lastFrame = HashMap<Int, Long>()

            while (isActive) {

                mixed.fill(0f)

                var receivedAudio = false

                val now =
                    android.os.SystemClock.elapsedRealtime()

                for ((userId, queue) in userQueues) {

                    val packet = synchronized(queue) {

                        if (queue.isEmpty()) {

                            val last =
                                lastFrame[userId] ?: 0L

                            if (now - last > 180L) {
                                started.remove(userId)
                                waitingSince.remove(userId)
                            }

                            null

                        } else if (userId !in started) {

                            val since =
                                waitingSince.getOrPut(userId) {
                                    now
                                }

                            if (
                                queue.size >= 3 ||
                                now - since >= 100L
                            ) {
                                started.add(userId)
                                waitingSince.remove(userId)
                                lastFrame[userId] = now
                                queue.pollFirst()
                            } else {
                                null
                            }

                        } else {

                            lastFrame[userId] = now
                            queue.pollFirst()
                        }

                    } ?: continue

                    val decoder =
                        userDecoders.getOrPut(userId) {
                            OpusCodec(audioConfig)
                        }

                    try {

                        val pcm = decoder.decode(packet)

                        bytesToShorts(pcm, decoded)

                        val volume =
                            userGainsDb[userId]?.let {
                                VadGate.dbToGain(it)
                            } ?: 1f

                        for (i in mixed.indices) {
                            mixed[i] +=
                                decoded[i].toFloat() *
                                volume
                        }

                        receivedAudio = true

                    } catch (e: Exception) {
                        Log.w(
                            TAG,
                            "Audio decodeerfout",
                            e
                        )
                    }
                }

                // Ruststand: geen onnodige audiowerkzaamheden
                // wanneer er niemand spreekt.
                if (!receivedAudio && started.isEmpty()) {
                    playbackWake.poll(
                        20,
                        java.util.concurrent.TimeUnit.MILLISECONDS
                    )
                    continue
                }

                val gain =
                    if (
                        outputSuspendedByFocus ||
                        _isOutputMuted.value
                    ) {
                        0f
                    } else {
                        gainFactor *
                            if (duckedByFocus) {
                                DUCK_FACTOR
                            } else {
                                1f
                            }
                    }

                // Alle stemmen eerst mengen.
                // Pas daarna zacht begrenzen.
                for (i in mixed.indices) {
                    output[i] = limitReceivedAudio(
                        mixed[i] * gain
                    )
                }

                val track = audioTrack

                if (
                    track == null ||
                    track.state != AudioTrack.STATE_INITIALIZED
                ) {
                    delay(FRAME_SIZE_MS.toLong())
                    continue
                }

                // Blokkerend afspelen zoals PTT Connect.
                var offset = 0

                while (
                    offset < output.size &&
                    isActive
                ) {

                    val written = track.write(
                        output,
                        offset,
                        output.size - offset,
                        AudioTrack.WRITE_BLOCKING
                    )

                    if (written <= 0) {
                        Log.w(
                            TAG,
                            "AudioTrack schrijfprobleem: $written"
                        )
                        break
                    }

                    offset += written
                }

                if (offset < output.size) {
                    delay(FRAME_SIZE_MS.toLong())
                }
            }
        }
    }

    private fun limitReceivedAudio(value: Float): Short {

        val magnitude = kotlin.math.abs(value)
        val knee = 24576f
        val headroom = 8191f

        val result = if (magnitude <= knee) {
            magnitude
        } else {
            val excess = magnitude - knee

            knee + (
                headroom * excess /
                (headroom + excess)
            )
        }

        val signed =
            if (value < 0f) -result else result

        return signed.toInt()
            .coerceIn(
                Short.MIN_VALUE.toInt(),
                Short.MAX_VALUE.toInt()
            )
            .toShort()
    }

'''

source = source[:begin] + nieuwe_audio + source[einde:]


# ==========================================
# 4. Rogerpiep verlengen tot drie tonen
# ==========================================

# 18 frames x 20 ms = 360 milliseconden.
vervang(
    "private val rogerTotalFrames = 9",
    "private val rogerTotalFrames = 18"
)


# ==========================================
# 5. Frequenties voor drie tonen
# ==========================================

vervang(
    """                // Rogerpiep van 880 Hz.
                val wave = kotlin.math.sin(
                    2.0 * Math.PI * 880.0 *
                        index.toDouble() / SAMPLE_RATE
                )""",
    """                // Drie oplopende rogerpiep-tonen.
                // Elke toon duurt 120 milliseconden.
                val framesPerTone = rogerTotalFrames / 3

                val toneNumber =
                    (frameNumber / framesPerTone)
                        .coerceIn(0, 2)

                val frequency = when (toneNumber) {
                    0 -> 700.0
                    1 -> 950.0
                    else -> 1200.0
                }

                val sampleInTone =
                    (frameNumber % framesPerTone) *
                    FRAME_SIZE_SAMPLES + i

                val toneSamples =
                    framesPerTone * FRAME_SIZE_SAMPLES

                // Zachte overgang voorkomt tikken
                // tussen de drie tonen.
                val toneFade = minOf(
                    1.0,
                    sampleInTone.toDouble() / 240.0,
                    (toneSamples - 1 - sampleInTone)
                        .toDouble() / 240.0
                ).coerceAtLeast(0.0)

                val wave = kotlin.math.sin(
                    2.0 * Math.PI * frequency *
                        sampleInTone.toDouble() /
                        SAMPLE_RATE
                )"""
)

vervang(
    "wave * 6500.0 * fade",
    "wave * 6500.0 * fade * toneFade"
)


# ==========================================
# 6. Versienummer verhogen
# ==========================================

if gradle.count("versionCode = 16") != 1:
    raise SystemExit(
        "FOUT: verwacht rogerpiep-versie met versionCode 16"
    )

if gradle.count('versionName = "2.2.1-NL"') != 1:
    raise SystemExit(
        "FOUT: verwacht versie 2.2.1-NL"
    )

gradle = gradle.replace(
    "versionCode = 16",
    "versionCode = 17",
    1
)

gradle = gradle.replace(
    'versionName = "2.2.1-NL"',
    'versionName = "2.2.2-NL"',
    1
)


# ==========================================
# 7. Bestanden opslaan
# ==========================================

AUDIO.write_text(
    source,
    encoding="utf-8"
)

GRADLE.write_text(
    gradle,
    encoding="utf-8"
)

print("================================")
print("TS6 DROID NL - NIEUWE AUDIO")
print("================================")
print("PTT Connect-achtige ontvangst")
print("Grotere audiobuffers")
print("Zachtere menging van stemmen")
print("Rogerpiep: DRIE TONEN")
print("Toon 1: 700 Hz")
print("Toon 2: 950 Hz")
print("Toon 3: 1200 Hz")
print("Rogerpiep aan/uit behouden")
print("Fysieke PTT behouden")
print("Scherm-PTT behouden")
print("32-bit en 64-bit behouden")
print("Versie 2.2.2-NL")
print("================================")
