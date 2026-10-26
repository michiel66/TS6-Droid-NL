
#!/usr/bin/env python3
"""TS6 Droid NL - fysieke PTT-zijknop en scherm-PTT.

Ingedrukt = microfoon AAN.
Losgelaten = microfoon DIRECT UIT.

Uitvoeren na:
1. maak_nederlands.py
2. maak_32_64_bit.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def vervang(bestand, oud, nieuw):
    pad = ROOT / bestand

    if not pad.exists():
        raise SystemExit(
            f"FOUT: ontbrekend bestand: {bestand}"
        )

    tekst = pad.read_text(encoding="utf-8")

    if tekst.count(oud) != 1:
        raise SystemExit(
            f"FOUT: broncode gewijzigd in {bestand}: "
            f"{oud[:80]!r}"
        )

    pad.write_text(
        tekst.replace(oud, nieuw, 1),
        encoding="utf-8"
    )


# ==========================================
# 1. PTT-instellingen opslaan
# ==========================================

s = "app/src/main/kotlin/dev/tsdroid/data/SettingsStore.kt"

vervang(
    s,
    "import androidx.datastore.preferences.core.floatPreferencesKey\n",
    "import androidx.datastore.preferences.core.floatPreferencesKey\n"
    "import androidx.datastore.preferences.core.intPreferencesKey\n"
)

vervang(
    s,
    'private val KEY_VAD_THRESHOLD_DB = floatPreferencesKey("vad_threshold_db")\n',
    'private val KEY_VAD_THRESHOLD_DB = floatPreferencesKey("vad_threshold_db")\n'
    'private val KEY_HARDWARE_PTT_ENABLED = booleanPreferencesKey("hardware_ptt_enabled")\n'
    'private val KEY_HARDWARE_PTT_KEY = intPreferencesKey("hardware_ptt_key")\n'
)

vervang(
    s,
    "class SettingsStore(private val context: Context) {\n",
    '''class SettingsStore(private val context: Context) {

    // Standaard UIT: Samsung blijft ongewijzigd.
    val hardwarePttEnabled: Flow<Boolean> =
        context.settingsDataStore.data
            .map { it[KEY_HARDWARE_PTT_ENABLED] ?: false }

    val hardwarePttKey: Flow<Int> =
        context.settingsDataStore.data
            .map { it[KEY_HARDWARE_PTT_KEY] ?: 0 }

    suspend fun setHardwarePttEnabled(aan: Boolean) {
        context.settingsDataStore.edit {
            it[KEY_HARDWARE_PTT_ENABLED] = aan
        }
    }

    suspend fun setHardwarePttKey(code: Int) {
        context.settingsDataStore.edit {
            it[KEY_HARDWARE_PTT_KEY] = code
        }
    }
'''
)


# ==========================================
# 2. Fysieke PTT-controller maken
# ==========================================

p = ROOT / (
    "app/src/main/kotlin/dev/tsdroid/"
    "ptt/HardwarePttController.kt"
)

p.parent.mkdir(parents=True, exist_ok=True)

p.write_text(
    '''package dev.tsdroid.ptt

import android.content.Context
import android.view.KeyEvent
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import dev.tsdroid.bridge.AudioBridge
import dev.tsdroid.bridge.MicMode
import dev.tsdroid.data.SettingsStore
import dev.tsdroid.service.TsConnectionService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.launch

object HardwarePttController {

    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.Main.immediate
    )

    private var store: SettingsStore? = null

    private var enabled = false
    private var mappedKey = 0
    private var micMode = MicMode.PTT

    private var screenHeld = false
    private var sideHeld = false
    private var pairingPressedKey = 0

    var pairing by mutableStateOf(false)
        private set

    fun start(context: Context) {
        if (store != null) return

        val settings = SettingsStore(
            context.applicationContext
        )

        store = settings

        scope.launch {
            combine(
                settings.hardwarePttEnabled,
                settings.hardwarePttKey,
                settings.micMode
            ) { on, key, mode ->
                Triple(on, key, mode)
            }.collect { (on, key, mode) ->

                val wasHeld = screenHeld || sideHeld

                enabled = on

                if (!on ||
                    key != mappedKey ||
                    mode != MicMode.PTT
                ) {
                    sideHeld = false
                }

                if (mode != MicMode.PTT) {
                    screenHeld = false
                }

                mappedKey = key
                micMode = mode

                if (
                    mode == MicMode.PTT &&
                    wasHeld &&
                    !screenHeld &&
                    !sideHeld
                ) {
                    TsConnectionService.instance
                        ?.audioBridge
                        ?.setMuted(true)
                }
            }
        }
    }

    fun startPairing() {
        pairing = true
    }

    fun cancelPairing() {
        pairing = false
        pairingPressedKey = 0
    }

    // Ondersteunt Android keyCode en scanCode.
    private fun key(event: KeyEvent): Int =
        if (event.keyCode != KeyEvent.KEYCODE_UNKNOWN) {
            event.keyCode
        } else if (event.scanCode > 0) {
            -event.scanCode
        } else {
            0
        }

    fun onKey(event: KeyEvent): Boolean {

        val code = key(event)

        // Loslaten na het koppelen verwerken.
        if (
            event.action == KeyEvent.ACTION_UP &&
            code == pairingPressedKey &&
            code != 0
        ) {
            pairingPressedKey = 0
            return true
        }

        // Nieuwe fysieke knop koppelen.
        if (pairing) {
            if (
                event.action == KeyEvent.ACTION_DOWN &&
                event.repeatCount == 0 &&
                code != 0 &&
                event.keyCode !in setOf(
                    KeyEvent.KEYCODE_BACK,
                    KeyEvent.KEYCODE_HOME,
                    KeyEvent.KEYCODE_POWER,
                    KeyEvent.KEYCODE_MENU
                )
            ) {
                pairing = false
                pairingPressedKey = code

                scope.launch {
                    store?.setHardwarePttKey(code)
                    store?.setHardwarePttEnabled(true)
                }

                return true
            }

            return false
        }

        // Samsung of uitgeschakelde PTT:
        // gewone toetsen blijven normaal werken.
        if (
            !enabled ||
            code == 0 ||
            code != mappedKey ||
            micMode != MicMode.PTT
        ) {
            return false
        }

        return when (event.action) {

            KeyEvent.ACTION_DOWN -> {
                if (
                    event.repeatCount == 0 &&
                    TsConnectionService.instance
                        ?.tsClient
                        ?.isConnected == true
                ) {
                    sideHeld = true
                    updateMicrophone()
                }

                true
            }

            KeyEvent.ACTION_UP -> {
                sideHeld = false
                updateMicrophone()
                true
            }

            else -> false
        }
    }

    // De PTT-knop op het scherm.
    fun screenPtt(
        pressed: Boolean,
        bridge: AudioBridge?
    ) {
        if (
            micMode != MicMode.PTT ||
            bridge == null
        ) {
            return
        }

        screenHeld = pressed
        updateMicrophone(bridge)
    }

    private fun updateMicrophone(
        bridge: AudioBridge? =
            TsConnectionService.instance?.audioBridge
    ) {
        if (
            micMode != MicMode.PTT ||
            bridge == null
        ) {
            return
        }

        // Minstens één knop vast = zenden.
        // Beide knoppen los = direct stoppen.
        bridge.setMuted(
            !(screenHeld || sideHeld)
        )
    }

    // Veilig stoppen als de app naar
    // de achtergrond verdwijnt.
    fun releaseOnBackground() {
        pairing = false
        pairingPressedKey = 0

        val wasHeld = screenHeld || sideHeld

        screenHeld = false
        sideHeld = false

        if (
            wasHeld &&
            micMode == MicMode.PTT
        ) {
            TsConnectionService.instance
                ?.audioBridge
                ?.setMuted(true)
        }
    }
}
''',
    encoding="utf-8"
)


# ==========================================
# 3. Zijknop koppelen aan Android
# ==========================================

act = "app/src/main/kotlin/dev/tsdroid/MainActivity.kt"

vervang(
    act,
    "import android.os.Bundle\n",
    "import android.os.Bundle\n"
    "import android.view.KeyEvent\n"
    "import dev.tsdroid.ptt.HardwarePttController\n"
)

vervang(
    act,
    "        enableEdgeToEdge()\n        setContent {\n",
    "        enableEdgeToEdge()\n"
    "        HardwarePttController.start(applicationContext)\n"
    "        setContent {\n"
)

vervang(
    act,
    "    override fun onStop() {\n",
    '''    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        if (HardwarePttController.onKey(event)) {
            return true
        }

        return super.dispatchKeyEvent(event)
    }

    override fun onStop() {
        HardwarePttController.releaseOnBackground()
'''
)


# ==========================================
# 4. Scherm-PTT en zijknop samenwerken
# ==========================================

vm = (
    "app/src/main/kotlin/dev/tsdroid/"
    "viewmodel/ServerViewModel.kt"
)

vervang(
    vm,
    "import dev.tsdroid.data.SettingsStore\n",
    "import dev.tsdroid.data.SettingsStore\n"
    "import dev.tsdroid.ptt.HardwarePttController\n"
)

vervang(
    vm,
    '''    fun setPushToTalk(pressed: Boolean) {
        // Only changes mute state, NOT isPttMode — avoids UI recomposition swap
        audioBridge?.setMuted(!pressed)
    }
''',
    '''    fun setPushToTalk(pressed: Boolean) {
        // Scherm en zijknop: vasthouden = aan.
        // Laatste knop los = direct microfoon uit.
        HardwarePttController.screenPtt(
            pressed,
            audioBridge
        )
    }
'''
)


# ==========================================
# 5. Instellingenpagina uitbreiden
# ==========================================

pagina = (
    "app/src/main/kotlin/dev/tsdroid/"
    "ui/screen/SettingsPage.kt"
)

vervang(
    pagina,
    "import dev.tsdroid.data.SettingsStore\n",
    "import dev.tsdroid.data.SettingsStore\n"
    "import dev.tsdroid.ptt.HardwarePttController\n"
)

vervang(
    pagina,
    "    val micMode by settingsStore.micMode.collectAsStateWithLifecycle(initialValue = MicMode.PTT)\n",
    '''    val micMode by settingsStore.micMode.collectAsStateWithLifecycle(initialValue = MicMode.PTT)

    val hardwarePttEnabled by
        settingsStore.hardwarePttEnabled
            .collectAsStateWithLifecycle(initialValue = false)

    val hardwarePttKey by
        settingsStore.hardwarePttKey
            .collectAsStateWithLifecycle(initialValue = 0)
'''
)

vervang(
    pagina,
    "                // ── 麦克风模式：按住说话 / 语音激活 / 开放麦克风 ──\n",
    '''                // Fysieke PTT optioneel inschakelen.
                SettingsSwitchRow(
                    label = stringResource(
                        R.string.hardware_ptt_setting
                    ),
                    checked = hardwarePttEnabled,
                    onCheckedChange = { enabled ->
                        scope.launch {
                            settingsStore.setHardwarePttEnabled(
                                enabled
                            )
                        }
                    }
                )

                Column(
                    modifier = Modifier.padding(
                        horizontal = 16.dp,
                        vertical = 8.dp
                    )
                ) {
                    Text(
                        text = stringResource(
                            R.string.hardware_ptt_hint
                        ),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )

                    Spacer(Modifier.height(6.dp))

                    Button(
                        onClick = {
                            if (HardwarePttController.pairing) {
                                HardwarePttController.cancelPairing()
                            } else {
                                HardwarePttController.startPairing()
                            }
                        }
                    ) {
                        Text(
                            stringResource(
                                if (HardwarePttController.pairing)
                                    R.string.hardware_ptt_waiting
                                else
                                    R.string.hardware_ptt_pair
                            )
                        )
                    }

                    Text(
                        text = stringResource(
                            R.string.hardware_ptt_code,
                            hardwarePttKey
                        ),
                        style = MaterialTheme.typography.labelSmall
                    )
                }

                // ── 麦克风模式：按住说话 / 语音激活 / 开放麦克风 ──
'''
)


# ==========================================
# 6. Nederlandse teksten toevoegen
# ==========================================

strings = ROOT / "app/src/main/res/values/strings.xml"

res = strings.read_text(encoding="utf-8")

if '<string name="hardware_ptt_setting"' in res:
    raise SystemExit(
        "FOUT: PTT-wijziging is al toegepast"
    )

regels = '''    <string name="hardware_ptt_setting">Fysieke PTT-zijknop inschakelen</string>
    <string name="hardware_ptt_hint">Voor TeloX inschakelen en de zijknop koppelen. Op Samsung uit laten. Alleen als Android de toets doorgeeft.</string>
    <string name="hardware_ptt_pair">Koppel zijknop</string>
    <string name="hardware_ptt_waiting">Druk op de zijknop (tik om te annuleren)</string>
    <string name="hardware_ptt_code">Gekoppelde toets: %1$d</string>
'''

if res.count("</resources>") != 1:
    raise SystemExit(
        "FOUT: strings.xml niet herkenbaar"
    )

strings.write_text(
    res.replace(
        "</resources>",
        regels + "</resources>",
        1
    ),
    encoding="utf-8"
)


# ==========================================
# 7. Versienummer verhogen
# ==========================================

gradle = ROOT / "app/build.gradle.kts"

g = gradle.read_text(encoding="utf-8")

if (
    g.count("versionCode = 14") != 1 or
    g.count('versionName = "2.1.9-NL"') != 1
):
    raise SystemExit(
        "FOUT: voer eerst het bestaande "
        "32/64-bit script uit"
    )

g = g.replace(
    "versionCode = 14",
    "versionCode = 15",
    1
)

g = g.replace(
    'versionName = "2.1.9-NL"',
    'versionName = "2.2.0-NL"',
    1
)

gradle.write_text(
    g,
    encoding="utf-8"
)

print("OK: fysieke PTT optioneel ingeschakeld.")
print("OK: scherm-PTT blijft werken.")
print("OK: indrukken = zenden.")
print("OK: loslaten = direct stoppen.")
print("OK: 32-bit en 64-bit blijven behouden.")
