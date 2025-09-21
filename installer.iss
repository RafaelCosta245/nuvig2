; ==== Inno Setup script para Nuvig (build sai em build\windows) ====
#define MyAppName "Gestão Nuvig"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Rafael Costa"
#define MyAppExeName "Gestao_Nuvig.exe"   ; <-- troque para o nome real do seu .exe
#define BuildDir "build\\windows"  ; <-- pasta que o Flet gerou no seu caso

[Setup]
AppId={{A1B2C3D4-E5F6-47A8-9ABC-1234567890AB}}   ; gere um GUID seu (qualquer)
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=yes
OutputBaseFilename=Setup_{#MyAppName}_{#MyAppVersion}
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern

; [Languages]
; Name: "portugues"; MessagesFile: "compiler:Languages\PortugueseBrazil.isl"


[Files]
; Copia TUDO que está em build\windows para a pasta de instalação
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
; Atalho no menu iniciar
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Atalho na área de trabalho (opcional)
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Executar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; (opcional) remover dados do usuário ao desinstalar
; Type: filesandordirs; Name: "{localappdata}\Nuvig"
