[Setup]
AppName=HoiCompiler
AppVersion=1.0
DefaultDirName={autopf}\HoiCompiler
OutputBaseFilename=HoiCompiler-setup
PrivilegesRequired=admin

[Files]
Source: "hoic.dist\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Hoi Compiler"; Filename: "{app}\hoic.exe"

[Registry]
Root: HKCR; Subkey: ".hoic"; ValueType: string; ValueName: ""; ValueData: "HoiCompiler.File"; Flags: uninsdeletekey

Root: HKCR; Subkey: "HoiCompiler.File"; ValueType: string; ValueName: ""; ValueData: "Hearts of Iron Compiler File"; Flags: uninsdeletekey

Root: HKCR; Subkey: "HoiCompiler.File\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\hoic.exe"" ""%1"""

Root: HKCR; Subkey: "HoiCompiler.File\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\hoic.exe,0"