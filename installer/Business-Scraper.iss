; Business-Scraper Inno Setup installer
#define MyAppName "Business-Scraper"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Ali Valizadeh"
#define MyAppExeName "Business-Scraper.exe"

[Setup]
AppId={{B6A7E3E5-4C0C-4B38-9E43-2F7D7F1A9C11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Business-Scraper
DefaultGroupName={#MyAppName}
OutputDir=dist\installer
OutputBaseFilename=Business-Scraper-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}

[Files]
Source: "..\dist\Business-Scraper.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
