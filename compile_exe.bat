@echo off

#call full_install.bat

#python -m nuitka --standalone --windows-console-mode=force --windows-icon-from-ico=icon.png hoic.py

echo Press enter to create the installer . . .
pause

"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "%CURDIR%create_installer.iss"

set "FILENAME=HoiCompiler-setup.exe"

del /f /q "%CURDIR%%FILENAME%"
move /y "%CURDIR%Output\%FILENAME%" "%CURDIR%"
rmdir /s /q "%CURDIR%Output"

pause