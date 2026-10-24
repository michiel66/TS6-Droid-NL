#!/usr/bin/env python3
"""Voegt 32-bit ARM toe aan dezelfde Nederlandstalige TS6 Droid APK.

Gebruikt de bestaande 64-bit native library en bouwt een nieuwe 32-bit
library apart via de GitHub Actions workflow. Voer uit nadat
scripts/maak_nederlands.py is uitgevoerd op de YUAXI broncode.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
build_file = ROOT / 'app' / 'build.gradle.kts'
if not build_file.is_file():
    raise SystemExit('FOUT: voer het script uit in de uitgepakte TS6 Droid broncode')

src = build_file.read_text(encoding='utf-8')

# De oorspronkelijke arm64-v8a .so blijft bewaard voor de Samsung.
old = 'abiFilters += listOf("arm64-v8a")'
new = 'abiFilters += listOf("armeabi-v7a", "arm64-v8a")'
if src.count(old) != 1:
    raise SystemExit(f'FOUT: oorspronkelijke ABI-regel niet precies eenmaal gevonden: {old}')
src = src.replace(old, new, 1)

# De optionele, lokale Rust-Gradle taak (buildRustLibs) gebruikt nu ook beide
# Android ARM-targets. In CI bouwen we bewust alleen de ontbrekende 32-bit .so
# en slaan we die Gradle taak over.
old_targets = '''        "-t", "arm64-v8a",
        "-t", "x86_64",'''
new_targets = '''        "-t", "arm64-v8a",
        "-t", "armeabi-v7a",'''
if src.count(old_targets) != 1:
    raise SystemExit('FOUT: originele Rust ABI-targets zijn gewijzigd')
src = src.replace(old_targets, new_targets, 1)

# Herkenbare opvolgversie (pakketnaam nl.ts6droid.client blijft hetzelfde).
if src.count('versionCode = 13') != 1:
    raise SystemExit('FOUT: verwachte versiecode 13 ontbreekt')
src = src.replace('versionCode = 13', 'versionCode = 14', 1)
if src.count('versionName = "2.1.8-NL"') != 1:
    raise SystemExit('FOUT: voer eerst maak_nederlands.py uit (versie 2.1.8-NL ontbreekt)')
src = src.replace('versionName = "2.1.8-NL"', 'versionName = "2.1.9-NL"', 1)

# Update commentaar zodat een volgende bouwer niet onbedoeld armv7 wist.
src = re.sub(
    r'(?m)^\s*// arm64-v8a is the only ABI whose libtslib_jni.so is current:.*?\n\s*// because TsDroidApp loads libtslib_jni during class initialisation\.\n',
    '            // Both armeabi-v7a and arm64-v8a have matching libtslib_jni.so.\n'
    '            // Keep both native architectures when creating the APK.\n',
    src,
    count=1,
    flags=re.DOTALL,
)
build_file.write_text(src, encoding='utf-8')
print('OK: dezelfde TS6 Droid NL-app accepteert nu arm32 en arm64.')
print('Belangrijk: de 32-bit .so moet apart met Cargo/NDK worden gebouwd.')
