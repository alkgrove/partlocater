
@echo off

setlocal EnableDelayedExpansion
echo Partlocater setup and removal
echo To remove partlocater, first execute setup.bat and select remove
echo Then delete the partlocater directory manually
set batdir=%~dp0
set xampp_root=C:\xampp
REM First we check that python 3 with pip is installed
where /q python.exe || echo Python must be installed first && exit /b
where /q pip.exe || echo Python with pip must be installed first && exit /b
for /f "tokens=*" %%i in ('python -V') do set _var=%%i
set _var=%_var:* =%
set _var=%_var:~0,1%
if  %_var% neq 3 echo Python 3 must be installed first && exit /b
echo Python 3 found
:ask_xampp
echo Will you be setting up XAMPP as a local server for apache/mariadb
echo or will you be using another server on your local intranet
echo yes (y) - Using XAMPP locally for apache/mariadb
echo no (n) - Using remote intranet server and manually setting up
echo remove (r) - Remove the files this script has copied and the environment variable
echo              Does not remove the partlocater scripts
echo exit (e) - Abort setup
set /P _entry=">"
set _entry=%_entry:~0,1%
echo.
if "%_entry%"=="n" goto setup_intranet
if "%_entry%"=="y" goto check_xampp
if "%_entry%"=="r" goto remove_partlocater
if "%_entry%"=="e" exit /b
goto ask_xampp
:check_xampp
if exist %xampp_root% goto install_web
echo xampp directory not found in the default location C:\xampp
echo either it is in a different location or not installed. 
echo If it is installed but the path is not C:\xampp, then
echo type the path at the prompt ie D:\foo\xampp
echo If it is not installed, hit return to exit and install XAMPP
echo and retry the script.
set /P _entry="XAMPP root directory> " || set _entry=None
if "%_entry%"=="None" echo Please install XAMPP and retry && pause && exit /b
set xampp_root=%_entry%
goto check_xampp
:install_web
if not exist %xampp_root%\htdocs goto exit_for_bad_dirs
if not exist %xampp_root%\apache\conf goto exit_for_bad_dirs
echo Found XAMPP, copying files
set t=%xampp_root%\htdocs\digikey
set digikey_web=%t:\\=\%
set t=%xampp_root%\apache\conf
set apache_conf=%t:\\=\%
if not exist %digikey_web% mkdir %digikey_web%
echo Setting Environment Variable PARTLOCATER_CFG
setx PARTLOCATER_CFG "%apache_conf%\partlocater.cfg" 1>nul
if exist "%apache_conf%\partlocater.cfg" (
echo partlocater.cfg already exists, not copied
) else (
copy "%batdir%\assets\partlocater.cfg" "%apache_conf%\partlocater.cfg" 
echo Copy default partlocater.cfg to apache\conf directory
)
copy web %digikey_web% 1>nul
echo Copy web files to %digikey_web%

:skip_xampp
echo Creating shortcut - Drag to start menu or taskbar
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('Partlocater.lnk');$p=(Get-Item -Path '.\').FullName;$s.TargetPath=Join-Path (Join-Path $p 'scripts') 'partlocater.pyw';$s.WorkingDirectory=Join-Path $p 'scripts';$s.IconLocation=Join-Path (Join-Path $p 'assets') 'pl.ico';$s.Save()"
python -m pip install --upgrade pip
python -m pip install requests mysql-connector openpyxl

exit /b

:setup_intranet
echo setting up partlocater for remote intranet server
setx PARTLOCATER_CFG "%batdir%partlocater.cfg"
if exist "%batdir%partlocater.cfg" (
echo partlocater.cfg already exists, not copied
) else (
copy "%batdir%assets\partlocater.cfg" "%batdir%partlocater.cfg" 
echo Copy default partlocater.cfg to local directory
echo A copy may be needed on the server and must be manually copied
)
goto skip_xampp
:exit_for_bad_dirs
echo XAMPP should have htdocs and apache/conf directory and were not found in xampp.
echo either the wrong directory was entered or the web directory or were changed in XAMPP
pause
exit /b
:remove_partlocater
set filepath=
set _dkpath=
echo This removes the web files and config scripts written to the xampp folder
echo This removes the environment variable PARTLOCATER_CFG
echo It does not remove the partlocater script folder
if not defined PARTLOCATER_CFG echo "Done" && exit /b
for /F "delims=" %%a in ("%PARTLOCATER_CFG%") do set filepath=%%~dpa
set filepath=%filepath:~0,-1%
for /F "delims=" %%a in ("%filepath%") do set filepath=%%~dpa
set filepath=%filepath:~0,-1%
for /F "delims=" %%a in ("%filepath%") do set filepath=%%~dpa
set filepath=%filepath:~0,-1%
for /F "delims=" %%a in ("%filepath%\htdocs\digikey") do  set _dkpath=%%~fa
if not exist "%_dkpath%" goto skip_web_removal
echo Removing Digi-Key webpage from htdocs
del /s/f/q "%_dkpath%"
rmdir /s/q "%_dkpath%"
:skip_web_removal
if not exist %PARTLOCATER_CFG% goto skip_cfg_del
echo Removing partlocater.cfg
DEL /F/Q "%PARTLOCATER_CFG%" 1>nul
:skip_cfg_del
echo Deleting PARTLOCATER_CFG
REG delete HKCU\Environment /F /V PARTLOCATER_CFG 1>nul
set PARTLOCATER_CFG=
echo To finish the uninstall, delete the folder %batdir%
pause 
exit /b

