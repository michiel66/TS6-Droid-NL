
#!/usr/bin/env python3
"""TS6 Droid NL: meerdere serverfavorieten met eigen namen.

Draait NA de bestaande scripts voor Nederlands, 32/64-bit, PTT,
rogerpiep, verbeterde audio en volume. Bestaande favorieten blijven bewaard.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VM = ROOT / 'app/src/main/kotlin/dev/tsdroid/viewmodel/ConnectionViewModel.kt'
SCREEN = ROOT / 'app/src/main/kotlin/dev/tsdroid/ui/screen/ConnectionScreen.kt'
STRINGS = ROOT / 'app/src/main/res/values/strings.xml'
GRADLE = ROOT / 'app/build.gradle.kts'

sources = {}
for path in (VM, SCREEN, STRINGS, GRADLE):
    if not path.is_file():
        raise SystemExit(f'FOUT: bestand ontbreekt: {path}')
    sources[path] = path.read_text(encoding='utf-8')


def replace(path, old, new):
    src = sources[path]
    found = src.count(old)
    if found != 1:
        raise SystemExit(
            f'FOUT in {path.name}: verwacht 1 overeenkomst, vond {found}: '
            f'{old[:90]!r}'
        )
    sources[path] = src.replace(old, new, 1)


# Elk opgeslagen adres blijft een zelfstandig record in BookmarkStore.
# Favorietnaam is nieuw, het bestaande JSON-formaat blijft ongewijzigd.
replace(
    VM,
    '    val address = MutableStateFlow("")\n',
    '    val address = MutableStateFlow("")\n'
    '    val favoriteName = MutableStateFlow("")\n',
)

replace(
    VM,
    '''    fun saveBookmark() {
        val addr = address.value.trim()
        val nick = nickname.value.trim()
        if (addr.isEmpty()) return
        val bookmark = ServerBookmark(
            name = addr.substringBefore(":"),
            address = addr,
            nickname = nick,
            password = password.value.trim().takeIf { it.isNotEmpty() },
            channel = channel.value.trim().takeIf { it.isNotEmpty() },
        )
        viewModelScope.launch {
            val idx = _editingIndex.value
            if (idx >= 0) {
                bookmarkStore.replace(idx, bookmark)
            } else {
                bookmarkStore.add(bookmark)
            }
            clearFields()
        }
    }
''',
    '''    fun saveBookmark(): Boolean {
        val addr = address.value.trim()
        if (addr.isEmpty()) {
            _error.value = getApplication<Application>()
                .getString(R.string.nl_favorite_address_required)
            return false
        }
        val bookmark = ServerBookmark(
            name = favoriteName.value.trim().ifBlank { addr.substringBefore(":") },
            address = addr,
            nickname = nickname.value.trim(),
            password = password.value.trim().takeIf { it.isNotEmpty() },
            channel = channel.value.trim().takeIf { it.isNotEmpty() },
        )
        // Lees de bewerkingskeuze VOOR de asynchrone opslag. Bij een
        // nieuwe favoriet wordt altijd toegevoegd, nooit de vorige vervangen.
        val idx = _editingIndex.value
        clearFields()
        viewModelScope.launch {
            if (idx >= 0) {
                bookmarkStore.replace(idx, bookmark)
            } else {
                bookmarkStore.add(bookmark)
            }
        }
        return true
    }
''',
)

replace(
    VM,
    '    fun editBookmark(bookmark: ServerBookmark, index: Int) {\n'
    '        address.value = bookmark.address\n',
    '    fun editBookmark(bookmark: ServerBookmark, index: Int) {\n'
    '        favoriteName.value = bookmark.name\n'
    '        address.value = bookmark.address\n',
)

replace(
    VM,
    '    fun cancelEdit() {\n',
    '    /** Nieuwe favoriet: nooit een bestaande server overschrijven. */\n'
    '    fun startNewBookmark() {\n'
    '        clearFields()\n'
    '    }\n\n'
    '    fun cancelEdit() {\n',
)

replace(
    VM,
    '    private fun clearFields() {\n'
    '        _editingIndex.value = -1\n',
    '    private fun clearFields() {\n'
    '        _editingIndex.value = -1\n'
    '        favoriteName.value = ""\n',
)

# Scherm toont altijd een duidelijke knop om een extra favoriet toe te voegen.
replace(
    SCREEN,
    '    val address by viewModel.address.collectAsStateWithLifecycle()\n',
    '    val address by viewModel.address.collectAsStateWithLifecycle()\n'
    '    val favoriteName by viewModel.favoriteName.collectAsStateWithLifecycle()\n',
)

replace(
    SCREEN,
    '                            .size(56.dp)\n'
    '                            .clickable { showBottomSheet = true },',
    '                            .size(56.dp)\n'
    '                            .clickable {\n'
    '                                viewModel.startNewBookmark()\n'
    '                                showBottomSheet = true\n'
    '                            },',
)

replace(
    SCREEN,
    '                            bookmarks.forEachIndexed { index, bookmark ->',
    '''                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.SpaceBetween,
                            ) {
                                Text(
                                    text = stringResource(
                                        R.string.nl_favorites_count,
                                        bookmarks.size
                                    ),
                                    style = MaterialTheme.typography.titleMedium,
                                    modifier = Modifier.weight(1f),
                                )
                                FilledTonalButton(
                                    onClick = {
                                        viewModel.startNewBookmark()
                                        showBottomSheet = true
                                    },
                                ) {
                                    Icon(Icons.Default.Add, contentDescription = null)
                                    Spacer(Modifier.width(4.dp))
                                    Text(stringResource(R.string.nl_favorite_new))
                                }
                            }
                            bookmarks.forEachIndexed { index, bookmark ->''',
)

replace(
    SCREEN,
    '                                                text = bookmark.serverName ?: bookmark.name,',
    '''                                                text = if (
                                                    bookmark.name.isNotBlank() &&
                                                    bookmark.name != bookmark.address.substringBefore(":")
                                                ) bookmark.name else (bookmark.serverName ?: bookmark.name),''',
)

replace(
    SCREEN,
    '''                                    OutlinedTextField(
                                    value = address,''',
    '''                                    // Optionele herkenbare naam voor iedere server.
                                    OutlinedTextField(
                                        value = favoriteName,
                                        onValueChange = { viewModel.favoriteName.value = it },
                                        label = { Text(stringResource(R.string.nl_favorite_name)) },
                                        placeholder = { Text(stringResource(R.string.nl_favorite_name_hint)) },
                                        modifier = Modifier.fillMaxWidth(),
                                        singleLine = true,
                                        enabled = !isConnecting,
                                        colors = glassTextFieldColors,
                                    )

                                    OutlinedTextField(
                                    value = address,''',
)

replace(
    SCREEN,
    '                                        viewModel.saveBookmark()\n'
    '                                        showBottomSheet = false',
    '                                        if (viewModel.saveBookmark()) {\n'
    '                                            showBottomSheet = false\n'
    '                                        }',
)

# Meer favorieten verschijnen vanzelf in de bestaande scrollende lijst.
# BookmarkStore.save/add/remove/replace en de opgeslagen JSON blijven intact.
replace(
    STRINGS,
    '</resources>',
    '''    <string name="nl_favorites_count">Mijn favorieten (%1$d)</string>
    <string name="nl_favorite_new">Nieuwe favoriet</string>
    <string name="nl_favorite_name">Naam favoriet (optioneel)</string>
    <string name="nl_favorite_name_hint">Bijvoorbeeld: Heerlen</string>
    <string name="nl_favorite_address_required">Vul eerst een serveradres in.</string>
</resources>''',
)

replace(GRADLE, 'versionCode = 18', 'versionCode = 19')
replace(GRADLE, 'versionName = "2.2.3-NL"', 'versionName = "2.2.4-NL"')

# Voorkom gedeeltelijk geschreven patches bij broncodewijzigingen.
for path, new_text in sources.items():
    path.write_text(new_text, encoding='utf-8')

print('KLAAR: meerdere serveradressen als aparte favorieten')
print('KLAAR: nieuwe favoriet, eigen naam, bewerken en verwijderen')
print('KLAAR: bestaande favorieten en instellingen blijven bewaard')
print('BEHOUDEN: audio, volume, PTT, 3-tonige rogerpiep en 32/64-bit')
print('Versie 2.2.4-NL')
