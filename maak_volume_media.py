
#!/usr/bin/env python3
"""TS6 Droid NL - luidspreker en volumeknoppen corrigeren.

Draait NA:
  maak_nederlands.py
  maak_32_64_bit.py
  maak_ptt_zijknop.py
  maak_rogerpiep.py
  maak_audio_pttconnect_3toon.py

Laat stabiele ontvangst, PTT en 3-tonige rogerpiep intact.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AUDIO = ROOT / "app/src/main/kotlin/dev/tsdroid/bridge/AudioBridge.kt"
ACTIVITY = ROOT / "app/src/main/kotlin/dev/tsdroid/MainActivity.kt"
GRADLE = ROOT / "app/build.gradle.kts"

for path in (AUDIO, ACTIVITY, GRADLE):
    if not path.is_file():
        raise SystemExit(f"FOUT: bestand ontbreekt: {path}")

audio = AUDIO.read_text(encoding="utf-8")
activity = ACTIVITY.read_text(encoding="utf-8")
gradle = GRADLE.read_text(encoding="utf-8")


def vervang_een(bron: str, oud: str, nieuw: str, naam: str) -> str:
    aantal = bron.count(oud)
    if aantal != 1:
        raise SystemExit(
            f"FOUT in {naam}: verwacht 1 overeenkomst, vond {aantal}: "
            f"{oud[:85]!r}"
        )
    return bron.replace(oud, nieuw, 1)


# De ontvangst stond op de belvolume-route. USAGE_MEDIA gebruikt
# de normale media-luidspreker met regelbare mediavolume-instelling.
audio = vervang_een(
    audio,
    "                    .setUsage(AudioAttributes.USAGE_VOICE_COMMUNICATION)",
    "                    .setUsage(AudioAttributes.USAGE_MEDIA)",
    "AudioBridge.kt",
)

# Volumetoetsen bedienen het mediavolume als de app open staat.
activity = vervang_een(
    activity,
    "    override fun onCreate(savedInstanceState: Bundle?) {\n"
    "        super.onCreate(savedInstanceState)\n",
    "    override fun onCreate(savedInstanceState: Bundle?) {\n"
    "        super.onCreate(savedInstanceState)\n"
    "\n"
    "        // Volumeknoppen bedienen de media-luidspreker.\n"
    "        setVolumeControlStream(android.media.AudioManager.STREAM_MUSIC)\n",
    "MainActivity.kt",
)

# Versie verhogen na de 3-tonige rogerpiep.
gradle = vervang_een(
    gradle,
    "versionCode = 17",
    "versionCode = 18",
    "build.gradle.kts",
)

gradle = vervang_een(
    gradle,
    'versionName = "2.2.2-NL"',
    'versionName = "2.2.3-NL"',
    "build.gradle.kts",
)

# Bestanden alleen opslaan als alle zoekteksten kloppen.
AUDIO.write_text(audio, encoding="utf-8")
ACTIVITY.write_text(activity, encoding="utf-8")
GRADLE.write_text(gradle, encoding="utf-8")

print("KLAAR: ontvangen geluid via media-luidspreker")
print("KLAAR: volumeknoppen regelen mediavolume")
print("BEHOUDEN: PTT, 3-tonige rogerpiep, stabiele audio, 32/64-bit")
print("Nieuwe versie: 2.2.3-NL")
