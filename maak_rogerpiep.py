
#!/usr/bin/env python3
"""Rogerpiep voor TS6 Droid NL.

Uitvoeren na:
1. maak_nederlands.py
2. maak_32_64_bit.py
3. maak_ptt_zijknop.py

Rogerpiep staat standaard UIT.
Beide PTT-knoppen blijven werken.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
changes = {}


def vervang(rel, oud, nieuw):
    path = ROOT / rel

    if not path.is_file():
        raise SystemExit(
            f"FOUT: bestand ontbreekt: {rel}"
        )

    tekst = changes.get(path)

    if tekst is None:
        tekst = path.read_text(encoding="utf-8")

    aantal = tekst.count(oud)

    if aantal != 1:
        raise SystemExit(
            f"FOUT: broncode gewijzigd in {rel}. "
            f"Verwacht 1 overeenkomst, vond {aantal}. "
            f"Zoektekst: {oud[:100]!r}"
        )

    changes[path] = tekst.replace(oud, nieuw, 1)


# ==========================================
# 1. Instelling voor Rogerpiep opslaan
# ==========================================

settings = (
    "app/src/main/kotlin/dev/tsdroid/"
    "data/SettingsStore.kt"
)

vervang(
    settings,
    'private val KEY_HARDWARE_PTT_KEY = intPreferencesKey("hardware_ptt_key")\n',
    'private val KEY_HARDWARE_PTT_KEY = intPreferencesKey("hardware_ptt_key")\n'
    'private val KEY_ROGER_BEEP = booleanPreferencesKey("roger_beep")\n'
)

vervang(
    settings,
    "class SettingsStore(private val context: Context) {\n",
    '''class SettingsStore(private val context: Context) {

    // Rogerpiep staat standaard UIT.
    val rogerBeep: Flow<Boolean> =
        context.settingsDataStore.data
            .map { it[KEY_ROGER_BEEP] ?: false }

    suspend fun setRogerBeep(enabled: Boolean) {
        context.settingsDataStore.edit {
            it[KEY_ROGER_BEEP] = enabled
        }
    }
'''
)


# ==========================================
# 2. Schakelaar bij Instellingen toevoegen
# ==========================================

page = (
    "app/src/main/kotlin/dev/tsdroid/"
    "ui/screen/SettingsPage.kt"
)

vervang(
    page,
    "    val micMode by settingsStore.micMode.collectAsStateWithLifecycle(initialValue = MicMode.PTT)\n",
    "    val micMode by settingsStore.micMode.collectAsStateWithLifecycle(initialValue = MicMode.PTT)\n"
    "    val rogerBeep by settingsStore.rogerBeep.collectAsStateWithLifecycle(initialValue = false)\n"
)

vervang(
    page,
    '''                SettingsSwitchRow(
                    label = stringResource(R.string.noise_suppression),
                    checked = noiseSuppression,
                    onCheckedChange = { scope.launch { settingsStore.setNoiseSuppression(it) } },
                )
''',
    '''                SettingsSwitchRow(
                    label = stringResource(R.string.noise_suppression),
                    checked = noiseSuppression,
                    onCheckedChange = { scope.launch { settingsStore.setNoiseSuppression(it) } },
                )

                SettingsSwitchRow(
                    label = stringResource(
                        R.string.roger_beep_setting
                    ),
                    checked = rogerBeep,
                    onCheckedChange = {
                        scope.launch {
                            settingsStore.setRogerBeep(it)
                        }
                    },
                )
'''
)


# ==========================================
# 3. Instelling aan de audioservice koppelen
# ==========================================

service = (
    "app/src/main/kotlin/dev/tsdroid/"
    "service/TsConnectionService.kt"
)

vervang(
    service,
    '''        audioBridge = AudioBridge(applicationContext, tsClient)
        audioBridge.initialize()
''',
    '''        audioBridge = AudioBridge(applicationContext, tsClient)
        audioBridge.initialize()

        SettingsStore(this).rogerBeep.onEach { enabled ->
            audioBridge.rogerBeepEnabled = enabled
            if (!enabled) {
                audioBridge.cancelRogerBeep()
            }
        }.launchIn(serviceScope)
'''
)


# ==========================================
# 4. PTT-zijknop en schermknop aanpassen
# ==========================================

controller = (
    "app/src/main/kotlin/dev/tsdroid/"
    "ptt/HardwarePttController.kt"
)

vervang(
    controller,
    '''        // Minstens één knop vast = zenden.
        // Beide knoppen los = direct stoppen.
        bridge.setMuted(
            !(screenHeld || sideHeld)
        )
''',
    '''        // Zolang een PTT-knop vastzit, blijft de microfoon aan.
        // Bij loslaten stopt de stem direct.
        if (screenHeld || sideHeld) {
            bridge.setMuted(false)
        } else {
            bridge.finishPttTransmission()
        }
'''
)


# ==========================================
# 5. Rogerpiep in AudioBridge toevoegen
# ==========================================

bridge = (
    "app/src/main/kotlin/dev/tsdroid/"
    "bridge/AudioBridge.kt"
)

vervang(
    bridge,
    '''    private val _isMuted = MutableStateFlow(true) // Start muted (PTT default)
''',
    '''    // Rogerpiep: alleen een kunstmatig audiotoontje.
    // Na loslaten gaan er geen microfoonsamples meer uit.
    @Volatile
    var rogerBeepEnabled = false

    private val rogerLock = Any()

    // 9 frames van 20 ms = 180 ms.
    private val rogerTotalFrames = 9
    private var rogerFramesLeft = 0

    fun cancelRogerBeep() {
        synchronized(rogerLock) {
            if (rogerFramesLeft != 0) {
                rogerFramesLeft = 0

                if (_isMuted.value) {
                    tsClient.setInputMuted(true)
                }
            }
        }
    }

    // Laatste PTT-knop los.
    fun finishPttTransmission() {
        synchronized(rogerLock) {

            if (_isMuted.value) return

            // Stem stopt onmiddellijk.
            _isMuted.value = true

            if (
                rogerBeepEnabled &&
                micMode == MicMode.PTT &&
                !forcedMuted &&
                _isCapturing.value &&
                tsClient.isConnected
            ) {
                // Alleen piep verzenden.
                rogerFramesLeft = rogerTotalFrames
            } else {
                rogerFramesLeft = 0
                tsClient.setInputMuted(true)
            }
        }
    }

    // Verzend 20 ms rogerpiep via Opus.
    // De microfoon zelf blijft dicht.
    private fun sendRogerFrame(
        codec: OpusCodec
    ): Boolean {
        synchronized(rogerLock) {

            if (rogerFramesLeft <= 0) {
                return false
            }

            if (
                !rogerBeepEnabled ||
                forcedMuted ||
                !tsClient.isConnected ||
                !_isMuted.value
            ) {
                rogerFramesLeft = 0

                if (_isMuted.value) {
                    tsClient.setInputMuted(true)
                }

                return true
            }

            val frameNumber =
                rogerTotalFrames - rogerFramesLeft

            val totalSamples =
                rogerTotalFrames * FRAME_SIZE_SAMPLES

            val samples =
                ShortArray(FRAME_SIZE_SAMPLES)

            for (i in samples.indices) {

                val index =
                    frameNumber * FRAME_SIZE_SAMPLES + i

                // Korte fade voorkomt klikgeluiden.
                val fade = minOf(
                    1.0,
                    index.toDouble() / 240.0,
                    (totalSamples - 1 - index)
                        .toDouble() / 240.0
                ).coerceAtLeast(0.0)

                // Rogerpiep van 880 Hz.
                val wave = kotlin.math.sin(
                    2.0 * Math.PI * 880.0 *
                        index.toDouble() / SAMPLE_RATE
                )

                samples[i] = (
                    wave * 6500.0 * fade
                ).toInt().toShort()
            }

            try {
                val encoded = codec.encode(
                    shortsToBytes(samples)
                )

                tsClient.sendAudio(
                    encoded,
                    CODEC_OPUS_VOICE
                )
            } catch (t: Exception) {
                Log.w(
                    TAG,
                    "Rogerpiep verzenden mislukt",
                    t
                )
            }

            rogerFramesLeft--

            if (rogerFramesLeft == 0) {
                tsClient.setInputMuted(true)
            }

            return true
        }
    }

    private val _isMuted = MutableStateFlow(true) // Start muted (PTT default)
'''
)

# ==========================================
# 6. Rogerpiep in audioverwerking invoegen
# ==========================================

vervang(
    bridge,
    '''            if (!_isMuted.value && !forcedMuted && micGainFactor != 0f) {
''',
    '''            // Rogerpiep krijgt voorrang.
            // Geen microfoongeluid meer na PTT-release.
            if (sendRogerFrame(codec)) {
                silentFrames = 0
                vadGate.reset()
                _isLocalVoiceActive.value = false
                resetInputLevel()
                continue
            }

            if (!_isMuted.value && !forcedMuted && micGainFactor != 0f) {
'''
)


# ==========================================
# 7. Rogerpiep stoppen bij nieuwe PTT-druk
# ==========================================

vervang(
    bridge,
    '''    fun setMuted(muted: Boolean) {
        _isMuted.value = muted
        tsClient.setInputMuted(muted)
    }
''',
    '''    fun setMuted(muted: Boolean) {
        synchronized(rogerLock) {

            // Een nieuwe PTT-druk stopt een
            // eventueel vorig rogerpiepje.
            rogerFramesLeft = 0

            _isMuted.value = muted
            tsClient.setInputMuted(muted)
        }
    }
'''
)

# Stop eventueel overgebleven Rogerpiep
# bij verbreken van de verbinding.

vervang(
    bridge,
    '''    fun stopCapture() {
''',
    '''    fun stopCapture() {
        cancelRogerBeep()
'''
)


# ==========================================
# 8. Nederlandse tekst toevoegen
# ==========================================

strings = "app/src/main/res/values/strings.xml"

vervang(
    strings,
    "</resources>",
    '''    <string name="roger_beep_setting">Rogerpiep bij loslaten PTT</string>
</resources>'''
)


# ==========================================
# 9. Nieuw versienummer
# ==========================================

gradle = "app/build.gradle.kts"

vervang(
    gradle,
    "versionCode = 15",
    "versionCode = 16"
)

vervang(
    gradle,
    'versionName = "2.2.0-NL"',
    'versionName = "2.2.1-NL"'
)


# ==========================================
# 10. Alle aanpassingen opslaan
# ==========================================

for path, new_source in changes.items():
    path.write_text(
        new_source,
        encoding="utf-8"
    )

print("KLAAR: Rogerpiep toegevoegd.")
print("Rogerpiep staat standaard UIT.")
print("Instellingen > Audio > Rogerpiep.")
print("PTT vast = microfoon aan.")
print("PTT los = microfoon direct uit.")
print("Rogerpiep aan = kort toontje naar kanaal.")
print("32-bit en 64-bit blijven behouden.")
