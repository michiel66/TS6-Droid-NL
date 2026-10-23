#!/usr/bin/env python3
"""Nederlandse lokalisatie voor YUAXI/TS6_Droid_CN.

Bron: https://github.com/YUAXI/TS6_Droid_CN (GPL-3.0).
Behoud de LICENSE en de vermeldingen van de oorspronkelijke makers.
Voer uit vanaf de hoofdmap van een fork van het project.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import re

ROOT = Path(__file__).resolve().parent.parent

# Sleutel | Nederlandse tekst. Android-placeholders zoals %1$s en %1$d moeten exact blijven.
TRANSLATIONS = r"""
app_name|TS6 Droid NL
channel_connection|Verbinding
channel_connection_desc|Melding voor serververbinding
accessibility_service_desc|TeamSpeak 6 spraakbediening
language_simplified_chinese|Vereenvoudigd Chinees
language_english|Engels
language_french|Frans
language_dutch|Nederlands
language_change_title|Taal wijzigen?
language_change_message|De app moet opnieuw worden gestart om %1$s toe te passen.
restart|Opnieuw starten
mute_user|Gebruiker dempen
unmute_user|Gebruiker weer hoorbaar maken
user_muted|Gedempt
server_address|Serveradres
server_address_placeholder|localhost:9987
nickname|Gebruikersnaam
password_optional|Wachtwoord (optioneel)
channel_optional|Kanaal (optioneel)
default_channel|Standaardkanaal
channel_password_title|Kanaalwachtwoord: %1$s
channel_password_label|Wachtwoord
channel_join|Deelnemen
channel_password_required|Voor dit kanaal is een wachtwoord nodig
browse_channels|Kanalen bekijken
connecting|Verbinden\u2026
connect|Verbinden
add_bookmark|Favoriet toevoegen
edit_bookmark|Favoriet bewerken
save|Opslaan
bookmarks|Favorieten
no_bookmarks|Geen favorieten
manual_connection|Handmatig verbinden
auto_reconnect|Automatisch opnieuw verbinden
remove|Verwijderen
edit|Bewerken
select_channel|Kanaal kiezen
cancel|Annuleren
server|Server
disconnect|Verbinding verbreken
settings|Instellingen
audio_gain|Geluidsversterking
audio_gain_value|×%1$.1f
mic_gain|Microfoonversterking
gain_percent|%1$d%%
show_link_thumbnails|Videovoorbeelden bij links
auto_load_images|Afbeeldingen automatisch laden
enable_floating_window|Zwevend venster inschakelen
error_overlay_permission_required|Geef toestemming voor Weergeven over andere apps om het zwevende venster te gebruiken.
chat|Chat
push_to_talk|Druk om te praten
ptt|PTT
mute_mic|Microfoon dempen
mute|Dempen
unmute_mic|Microfoon inschakelen
tab_channel|Kanaal
tab_private|Privé
tab_home|Start
tab_settings|Instellingen
no_connection|Geen verbindingen
wallpaper_cache_size|Achtergrondcache: %1$s MB (%2$d afbeeldingen)
wallpaper_max_cache|Maximale cache: %1$d MB
wallpaper_view_cache|Achtergrondcache bekijken
wallpaper_cache_images|afbeeldingen
wallpaper_clear_cache|Achtergrondcache wissen
wallpaper_clear_cache_confirm|Weet je zeker dat je alle opgeslagen achtergronden wilt wissen? Dit kan niet ongedaan worden gemaakt.
wallpaper_cache_empty|Geen opgeslagen achtergronden
wallpaper_export|Opslaan in galerij
wallpaper_export_all|Alles opslaan
wallpaper_export_done|%1$d afbeelding(en) opgeslagen in de galerij
wallpaper_export_failed|Opslaan in galerij mislukt
session_running|Sessie actief
session_running_desc|De sessie blijft op de achtergrond actief
back_to_session|Terug naar sessie
back_to_home|Terug naar start
floating_overlay_offline|Niet verbonden
floating_overlay_no_channel|Niet in een kanaal
floating_overlay_members|%1$d aanwezig
floating_overlay_channels|Kanalen
floating_overlay_alone|Je bent alleen in dit kanaal
floating_overlay_no_channels|Geen andere kanalen beschikbaar
floating_overlay_open_app|App openen
floating_overlay_collapse|Inklappen
floating_overlay_push_to_talk|Ingedrukt houden om te praten
floating_overlay_muted|Gedempt
floating_overlay_talking|Microfoon aan: je praat
floating_overlay_mic_not_working|De microfoon werkt niet
floating_overlay_deafened|Geluid uit
overlay_permission_needed|Voor het zwevende venster is de toestemming Weergeven over andere apps nodig
confirm|Bevestigen
custom_bg_title|Eigen achtergrond
custom_bg_upload|Kiezen uit galerij
custom_bg_delete|Eigen achtergrond verwijderen
custom_bg_delete_confirm|Eigen achtergrond verwijderen? Daarna wordt de online achtergrond gebruikt.
custom_bg_active|Eigen achtergrond ingesteld
custom_bg_inactive|Geen eigen achtergrond
custom_bg_saved|Achtergrond opgeslagen
custom_bg_load_error|Achtergrond laden mislukt
crop_title|Achtergrond bijsnijden
crop_hint|Versleep het witte kader om een gebied te kiezen
section_appearance|Uiterlijk
section_audio|Audio
identity_section|Identiteit
identity_uid|Identiteits-UID: %1$s
identity_uid_none|Nog niet aangemaakt (wordt bij eerste verbinding gemaakt)
identity_export|Exporteren
identity_import|Importeren
identity_export_success|Identiteit geëxporteerd
identity_export_failed|Export mislukt: er is nog geen identiteit
identity_import_success|Geïmporteerd; actief bij de volgende verbinding
identity_import_failed|Import mislukt: ongeldig identiteitsbestand
identity_warning|Je identiteit bevat je aanmeldgegevens. Door te importeren wissel je van serveridentiteit. Bewaar het geëxporteerde bestand veilig.
mic_mode|Microfoonmodus
mic_mode_vad|Spraakactivatie
mic_mode_open|Open microfoon
vad_threshold|Activeringsdrempel: %1$d dB
vad_threshold_hint|Geluid boven de drempel wordt uitgezonden. -45 dB is geschikt voor de meeste omgevingen.
user_uid|Unieke ID
user_platform|Platform
user_version|Versie
user_country|Land
user_talkpower|Spreekrechten
user_server_groups|Servergroepen
user_channel_group|Kanaalgroep
user_channel_group_unknown|Kanaalgroep #%1$d
user_server_group_unknown|Groep #%1$d
user_server_groups_none|Geen groepsinformatie
user_panel_self|Jij
self_change_nickname|Tijdelijke gebruikersnaam wijzigen
nickname_temporary_hint|Geldt tot je de verbinding verbreekt; bij opnieuw verbinden wordt je eerdere naam hersteld
user_volume|Volume:
volume_default|standaard
volume_reset|Volume herstellen
private_message|Privébericht
section_chat|Chat
section_more|Meer
update_check|Controleren op updates
update_found|Nieuwe versie beschikbaar
update_already_latest|Je hebt de nieuwste versie
update_available|Nieuwe versie %1$s beschikbaar
update_download|Nu bijwerken
update_downloading|Downloaden
update_later|Later
update_no_changelog|Geen wijzigingsoverzicht beschikbaar
close|Sluiten
filter_all|Alles
message_channel_placeholder|Kanaalbericht\u2026
message_private_placeholder|Bericht aan %1$s\u2026
send|Verzenden
user_fallback|Gebruiker #%1$d
status_recording|Opnemen
status_talking|Aan het praten
status_muted|Gedempt
status_output_muted|Geluid gedempt
status_away|Afwezig
image|Afbeelding
file_attachment_info|%1$s \u00B7 Gedeeld bestand
file_attachment_server|%1$s \u00B7 Serverbestand
tap_to_download|Tik om te downloaden
tap_to_view|Tik om te bekijken
tap_to_load_images|Tik om afbeeldingen te laden
retry|Opnieuw proberen
file_too_large|Bestand is groter dan 10 MB — upload geannuleerd
tap_to_open|Tik om te openen
download_not_supported|Downloaden niet ondersteund
downloading|Downloaden\u2026
download|Downloaden
file_saved_label|Opgeslagen in Downloads
file_saved|%1$s opgeslagen
attach_file|Bestand toevoegen
file_size_bytes|%1$d B
file_size_kb|%1$.1f KB
file_size_mb|%1$.1f MB
file_size_gb|%1$.1f GB
file_manager|Bestanden
no_files|Geen bestanden
new_folder|Nieuwe map
rename|Naam wijzigen
delete_file|Verwijderen
confirm_delete|%1$s verwijderen?
enter_folder_name|Mapnaam
enter_new_name|Nieuwe naam
refresh|Vernieuwen
create|Aanmaken
folder|Map
upload|Uploaden
share_in_channel|Huidig kanaal
share_file_title|%1$s delen
notif_unmute|Dempen opheffen
notif_mute|Dempen
unknown_sender|Onbekend
me_sender|Ik
error_address_nickname_required|Serveradres en gebruikersnaam zijn verplicht
error_nickname_too_short|Gebruikersnaam moet minstens 3 tekens bevatten
connection_failed|Verbinding mislukt
browse_failed|Kanalen ophalen mislukt
error_service_start_failed|Achtergrondservice starten mislukt
error_not_connected|Niet verbonden met de server
download_failed|Download mislukt
crash_report_title|Vorige keer is de app onverwacht afgesloten
common_copy|Kopiëren
common_copied|Gekopieerd
about_software|Over deze app
about_back|← Terug
about_credits_title|Met dank aan en herkomst
about_credits_desc|Dit project is gebaseerd op de opensourcesoftware van Grégory D, met vertalingen en extra functies van yuaxi. Dank aan de oorspronkelijke auteur voor zijn bijdrage aan open spraakcommunicatie!
about_enhancement_title|Vertalingen en uitbreidingen
about_enhancement_desc|Deze editie is gebaseerd op de lokalisatie en verbeteringen van yuaxi. De Nederlandse vertaling is een afzonderlijke aanpassing van de open broncode. De applicatie bevat functies voor mobiele spraakcommunicatie, zwevende bediening en microfooninstellingen.
about_license_title|Opensourcelicentie (GPLv3)
about_license_desc|Deze software wordt verspreid onder de GNU GPL versie 3. Bij verspreiding van aangepaste versies moet de broncode onder de GPL beschikbaar blijven en moeten auteursvermeldingen en licentietekst behouden blijven.
about_repo_title|Broncode en updates
about_repo_desc|De oorspronkelijke broncode en de officiële wijzigingen zijn beschikbaar via GitHub. Deze Nederlandse versie is een afgeleide op basis van die broncode.
about_repo_link|🔗 Open de broncode van yuaxi op GitHub
about_warning_title|Let op: gratis opensourcesoftware
about_warning_desc|Deze applicatie is vrije opensourcesoftware. Download alleen uit vertrouwde bronnen. Je hoeft niet te betalen voor een onofficiële activeringscode.
anime_background|Animeachtergrond
noise_suppression|Ruisonderdrukking microfoon
about_contributors_title|Bijdragers
about_contributions_count|%1$d bijdragen
contributors_load_error|Laden mislukt
reconnect_in_progress|Opnieuw verbinden… (poging %1$d)
reconnect_notification|Verbinding verbroken — opnieuw verbinden (poging %1$d)
mic_unavailable_warning|De microfoon is momenteel niet beschikbaar. De app probeert dit automatisch te herstellen. Controleer of opnemen op de achtergrond is toegestaan als dit probleem aanhoudt.
mic_unavailable_short|Microfoon niet beschikbaar
battery_optimization|Uitzondering voor batterijoptimalisatie
battery_optimization_desc|Met deze uitzondering blijven opnemen en netwerkverbindingen op de achtergrond actief, ook in de energiebesparingsstand.
battery_optimization_allowed|Toegestaan
battery_optimization_action|Instellen
app_details_settings|Apprechten en automatisch starten
app_details_settings_desc|Sta op Xiaomi/Huawei/OPPO/vivo automatisch starten, achtergrondactiviteit en pop-upvensters toe

diag_log_title|Diagnoselogboek
diag_log_hint|Toont alleen logberichten van deze app. Tik op Vernieuwen om opnieuw te laden.
diag_log_refresh|Vernieuwen
diag_log_clear|Wissen
diag_log_empty|Geen logberichten
diag_log_loading|Laden\u2026
back|Terug
server_info|Serverinformatie
server_platform_version|Platform / versie
server_clients|Gebruikers online
server_clients_format|%1$d / %2$d
server_channels|Kanalen
server_uptime|Actief sinds
server_welcome|Welkomstbericht
whisper_clear_list|Lijst wissen
whisper_hold_mic|Ingedrukt houden om te fluisteren
whisper_need_targets|De fluisterlijst is leeg. Voeg eerst ontvangers toe.
whisper_banner|Fluisterlijst: %1$s
whisper_placeholder|Fluisterbericht aan %1$s\u2026
whisper_add_target|Toevoegen aan fluisterlijst
whisper_switch_label|Fluisteren (spraak alleen voor deze gebruiker)
whisper_remove_target|Verwijderen uit fluisterlijst
whisper_channel_target|Kanaal staat in de fluisterlijst
whisper_member_added|Fluisteren naar %1$s
whisper_member_removed|Fluisteren naar %1$s gestopt
whisper_channel_added|Fluisteren naar kanaal %1$s
whisper_channel_removed|Fluisteren naar kanaal %1$s gestopt
whisper_list_full|De fluisterlijst kan maximaal %1$d ontvangers bevatten
whisper_target_offline|(offline)
whisper_talk_toast|%1$s fluistert tegen je
whisper_list_title|Fluisterlijst
whisper_list_hint|Houd de oranje fluisterknop naast de microfoon ingedrukt om alleen met deze ontvangers te praten. Getypte berichten gaan ook naar hen. Laat los om terug te keren naar het kanaal.
whisper_section_groups|Servergroepen
whisper_section_channels|Kanalen
whisper_section_members|Gebruikers
whisper_group_members|%1$d online
whisper_group_fallback|Groep #%1$d
whisper_groups_unavailable|De server heeft de groepenlijst nog niet verzonden
whisper_no_members|Nog geen afzonderlijke gebruikers toegevoegd. Gebruik de fluisterknop bij een gebruiker.
away_status_title|Status
away_status_hint|Anderen kunnen je status zien. Niet storen schakelt ook je microfoon uit totdat je weer online bent.
away_status_online|Online
away_status_online_desc|Ontvangt en spreekt zoals gewoonlijk
away_status_away|Afwezig
away_status_away_desc|Toont afwezigheidsstatus; de microfoon blijft werken
away_status_dnd|Niet storen
away_status_dnd_desc|Toont de status en schakelt de microfoon uit
away_message_label|Afwezigheidsbericht
away_message_save|Opslaan
away_marker|Afwezig
away_status_change|Status wijzigen
"""

translations: dict[str, str] = {}
for line in TRANSLATIONS.strip().splitlines():
    if not line.strip():
        continue
    key, sep, value = line.partition('|')
    if not sep or key in translations:
        raise ValueError(f'Ongeldige of dubbele vertaalregel: {line!r}')
    translations[key] = value

res = ROOT / 'app/src/main/res'
english_file = res / 'values-en/strings.xml'
default_file = res / 'values/strings.xml'
settings_file = ROOT / 'app/src/main/kotlin/dev/tsdroid/data/SettingsStore.kt'
ui_file = ROOT / 'app/src/main/kotlin/dev/tsdroid/ui/screen/SettingsPage.kt'
gradle_file = ROOT / 'app/build.gradle.kts'

for path in [english_file, default_file, settings_file, ui_file, gradle_file]:
    if not path.is_file():
        raise SystemExit(f'Bestand niet gevonden: {path}')

# Nederlandse resource bevat alle Engelse teksten, waar mogelijk vertaald.
# Zo vallen ontbrekende vertalingen tenminste niet terug op Chinees.
english = ET.parse(english_file)
root = english.getroot()
original_keys = set()
for el in root.findall('string'):
    name = el.attrib.get('name')
    original_keys.add(name)
    if name in translations:
        el.text = translations[name]

# Bronteksten die alleen in values/strings.xml bestaan eveneens meenemen.
vanilla = ET.parse(default_file)
for el in vanilla.getroot().findall('string'):
    name = el.attrib.get('name')
    if name not in original_keys:
        new_el = ET.SubElement(root, 'string', {'name': name})
        new_el.text = translations.get(name, el.text)
        original_keys.add(name)
if 'language_dutch' not in original_keys:
    ET.SubElement(root, 'string', {'name':'language_dutch'}).text = 'Nederlands'

# Android AAPT: apostrof in stringresource moet worden ge-escaped.
for el in root.findall('string'):
    if el.text and el.attrib.get('name') in translations:
        el.text = el.text.replace("'", r"\'")

nldir = res / 'values-nl'
nldir.mkdir(exist_ok=True)
outfile = nldir / 'strings.xml'
ET.indent(english, space='    ')
english.write(outfile, encoding='utf-8', xml_declaration=True)

# Voeg een resource toe voor de taalkeuze. Id moet in standaard values bestaan.
base = default_file.read_text(encoding='utf-8')
if 'name="language_dutch"' not in base:
    assert '</resources>' in base
    base = base.replace('</resources>', '    <string name="language_dutch">Nederlands</string>\n</resources>')
    default_file.write_text(base, encoding='utf-8')

# Maak Nederlands de taal bij eerste opstart.
def replace_exact(filename: Path, old: str, new: str) -> None:
    src = filename.read_text(encoding='utf-8')
    if new in src:
        return
    if old not in src:
        raise RuntimeError(f'Onverwachte upstreamwijziging in {filename}; patch niet toegepast: {old}')
    filename.write_text(src.replace(old,new,1), encoding='utf-8')

replace_exact(settings_file, 'it[KEY_LANGUAGE] ?: "zh"', 'it[KEY_LANGUAGE] ?: "nl"')
replace_exact(ui_file,
    '"fr" to stringResource(R.string.language_french),',
    '"fr" to stringResource(R.string.language_french),\n        "nl" to stringResource(R.string.language_dutch),')
replace_exact(ui_file,
    'collectAsStateWithLifecycle(initialValue = "zh")',
    'collectAsStateWithLifecycle(initialValue = "nl")')
replace_exact(ui_file,
    '?: stringResource(R.string.language_simplified_chinese)',
    '?: stringResource(R.string.language_dutch)')

# Eigen Android-app-id: kan naast de Chinese versie worden geïnstalleerd.
replace_exact(gradle_file,
    'applicationId = "com.yuaxi.ts6droid.cn"',
    'applicationId = "nl.ts6droid.client"')
replace_exact(gradle_file,
    'versionName = "2.1.8-Han"',
    'versionName = "2.1.8-NL"')

# Deze vertaalde app heeft een eigen pakketnaam en testsignatuur.
# De Chinese update-APK past daar niet bij: schakel de ingebouwde updater
# uit tot een releasekanaal met vaste ondertekening voor NL is ingesteld.
updater = ROOT / 'app/src/main/kotlin/dev/tsdroid/update/UpdateChecker.kt'
updater_src = updater.read_text(encoding='utf-8')
start = updater_src.find('    suspend fun checkForUpdate(')
end = updater_src.find('    // internal so the unit tests', start)
if start < 0 or end < 0:
    raise RuntimeError('Kan UpdateChecker niet veilig aanpassen; upstream gewijzigd')
new_function = (
    '    suspend fun checkForUpdate(currentVersionName: String): CheckResult = withContext(Dispatchers.IO) {\n'
    '        CheckResult(\n'
    '            update = null,\n'
    '            error = "Nederlandse updates zijn beschikbaar via GitHub Actions. De Chinese APK is niet compatibel.",\n'
    '        )\n'
    '    }\n\n'
)
updater_src = updater_src[:start] + new_function + updater_src[end:]
updater.write_text(updater_src, encoding='utf-8')

missing = sorted(set(original_keys) - set(translations))
print(f'Nederlandse teksten: {len(translations)}')
print(f'Bronteksten: {len(original_keys)}')
print(f'Nog zonder Nederlandse vertaling: {len(missing)} ({", ".join(missing)})')
print(f'Nederlandse taal toegevoegd: {outfile}')
