[Setup]
AppName=TaskTrackr
AppVersion=1.0
AppPublisher=TaskTrackr
DefaultDirName={autopf}\TaskTrackr
DefaultGroupName=TaskTrackr
OutputDir=dist
OutputBaseFilename=TaskTrackr-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\TaskTrackr.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\TaskTrackr\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\TaskTrackr"; Filename: "{app}\TaskTrackr.exe"
Name: "{group}\Uninstall TaskTrackr"; Filename: "{uninstallexe}"
Name: "{commondesktop}\TaskTrackr"; Filename: "{app}\TaskTrackr.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TaskTrackr.exe"; Description: "{cm:LaunchProgram,TaskTrackr}"; Flags: nowait postinstall skipifsilent
