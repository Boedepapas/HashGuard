@echo off
REM HashGuard Build Script - Creates both backend service and frontend GUI executables

echo ============================================
echo HashGuard Build System
echo Building Backend Service + Frontend GUI
echo ============================================
echo.

REM Check PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo [1/2] Building Backend Service (HashGuardBackend.exe)...
echo.
pyinstaller --clean backend_service.spec

if errorlevel 1 (
    echo ERROR: Backend build failed
    pause
    exit /b 1
)

echo.
echo [2/2] Building Frontend GUI (HashGuard.exe)...
echo.
pyinstaller --clean frontend_gui.spec

if errorlevel 1 (
    echo ERROR: Frontend build failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo BUILD SUCCESSFUL!
echo ============================================
echo.
echo Creating distribution package...

REM Clean and create package structure
if exist "dist\HashGuard_Package" rmdir /s /q "dist\HashGuard_Package"
mkdir "dist\HashGuard_Package"
mkdir "dist\HashGuard_Package\logs" 2>nul
mkdir "dist\HashGuard_Package\quarantine" 2>nul

REM Copy executables
copy "dist\HashGuardBackend.exe" "dist\HashGuard_Package\"
copy "dist\HashGuard.exe" "dist\HashGuard_Package\"

REM Copy configuration files (user-editable)
copy "backend\config.yaml" "dist\HashGuard_Package\config.yaml"
if exist ".env.example" copy ".env.example" "dist\HashGuard_Package\.env"

REM Create service installation batch file
echo @echo off > "dist\HashGuard_Package\install_service.bat"
echo REM Install HashGuard Backend Service >> "dist\HashGuard_Package\install_service.bat"
echo REM Must be run as Administrator >> "dist\HashGuard_Package\install_service.bat"
echo echo Installing HashGuard Backend Service... >> "dist\HashGuard_Package\install_service.bat"
echo echo. >> "dist\HashGuard_Package\install_service.bat"
echo "%%~dp0HashGuardBackend.exe" install >> "dist\HashGuard_Package\install_service.bat"
echo if errorlevel 1 ^( >> "dist\HashGuard_Package\install_service.bat"
echo     echo ERROR: Service installation failed >> "dist\HashGuard_Package\install_service.bat"
echo     echo Make sure to run as Administrator >> "dist\HashGuard_Package\install_service.bat"
echo     echo. >> "dist\HashGuard_Package\install_service.bat"
echo     pause >> "dist\HashGuard_Package\install_service.bat"
echo     exit /b 1 >> "dist\HashGuard_Package\install_service.bat"
echo ^) >> "dist\HashGuard_Package\install_service.bat"
echo echo. >> "dist\HashGuard_Package\install_service.bat"
echo echo Service installed successfully! >> "dist\HashGuard_Package\install_service.bat"
echo echo Starting service... >> "dist\HashGuard_Package\install_service.bat"
echo echo. >> "dist\HashGuard_Package\install_service.bat"
echo net start HashGuardService >> "dist\HashGuard_Package\install_service.bat"
echo if errorlevel 1 ^( >> "dist\HashGuard_Package\install_service.bat"
echo     echo WARNING: Service start failed >> "dist\HashGuard_Package\install_service.bat"
echo     echo Try: net start HashGuardService >> "dist\HashGuard_Package\install_service.bat"
echo     pause >> "dist\HashGuard_Package\install_service.bat"
echo     exit /b 1 >> "dist\HashGuard_Package\install_service.bat"
echo ^) >> "dist\HashGuard_Package\install_service.bat"
echo echo. >> "dist\HashGuard_Package\install_service.bat"
echo echo Service is now running! >> "dist\HashGuard_Package\install_service.bat"
echo echo You can now launch HashGuard.exe >> "dist\HashGuard_Package\install_service.bat"
echo echo. >> "dist\HashGuard_Package\install_service.bat"
echo pause >> "dist\HashGuard_Package\install_service.bat"

REM Create service uninstall batch file
echo @echo off > "dist\HashGuard_Package\uninstall_service.bat"
echo REM Uninstall HashGuard Backend Service >> "dist\HashGuard_Package\uninstall_service.bat"
echo REM Must be run as Administrator >> "dist\HashGuard_Package\uninstall_service.bat"
echo echo Uninstalling HashGuard Backend Service... >> "dist\HashGuard_Package\uninstall_service.bat"
echo echo. >> "dist\HashGuard_Package\uninstall_service.bat"
echo echo Stopping service... >> "dist\HashGuard_Package\uninstall_service.bat"
echo net stop HashGuardService 2^>nul >> "dist\HashGuard_Package\uninstall_service.bat"
echo echo. >> "dist\HashGuard_Package\uninstall_service.bat"
echo echo Removing service... >> "dist\HashGuard_Package\uninstall_service.bat"
echo "%%~dp0HashGuardBackend.exe" remove >> "dist\HashGuard_Package\uninstall_service.bat"
echo if errorlevel 1 ^( >> "dist\HashGuard_Package\uninstall_service.bat"
echo     echo ERROR: Service removal failed >> "dist\HashGuard_Package\uninstall_service.bat"
echo     echo Make sure to run as Administrator >> "dist\HashGuard_Package\uninstall_service.bat"
echo     echo. >> "dist\HashGuard_Package\uninstall_service.bat"
echo     pause >> "dist\HashGuard_Package\uninstall_service.bat"
echo     exit /b 1 >> "dist\HashGuard_Package\uninstall_service.bat"
echo ^) >> "dist\HashGuard_Package\uninstall_service.bat"
echo echo. >> "dist\HashGuard_Package\uninstall_service.bat"
echo echo Service uninstalled successfully! >> "dist\HashGuard_Package\uninstall_service.bat"
echo echo. >> "dist\HashGuard_Package\uninstall_service.bat"
echo pause >> "dist\HashGuard_Package\uninstall_service.bat"

REM Create README
echo HashGuard - Malware Hash Checker > "dist\HashGuard_Package\README.txt"
echo. >> "dist\HashGuard_Package\README.txt"
echo SETUP INSTRUCTIONS: >> "dist\HashGuard_Package\README.txt"
echo. >> "dist\HashGuard_Package\README.txt"
echo 1. Right-click install_service.bat >> "dist\HashGuard_Package\README.txt"
echo 2. Select "Run as Administrator" >> "dist\HashGuard_Package\README.txt"
echo 3. Wait for service to install and start >> "dist\HashGuard_Package\README.txt"
echo 4. Double-click HashGuard.exe to launch GUI >> "dist\HashGuard_Package\README.txt"
echo. >> "dist\HashGuard_Package\README.txt"
echo CONFIGURATION: >> "dist\HashGuard_Package\README.txt"
echo - Edit config.yaml to change settings >> "dist\HashGuard_Package\README.txt"
echo - Edit .env to add API keys (optional) >> "dist\HashGuard_Package\README.txt"
echo - Restart service after changes: net stop/start HashGuardService >> "dist\HashGuard_Package\README.txt"
echo. >> "dist\HashGuard_Package\README.txt"
echo TO UNINSTALL: >> "dist\HashGuard_Package\README.txt"
echo Run: HashGuardBackend.exe remove >> "dist\HashGuard_Package\README.txt"

echo.
echo ============================================
echo Package created: dist\HashGuard_Package\
echo ============================================
echo.
echo Contents:
echo   HashGuardBackend.exe  - Backend service
echo   HashGuard.exe         - Frontend GUI
echo   install_service.bat   - Service installer
echo   README.txt            - Instructions
echo.
echo To test:
echo 1. cd dist\HashGuard_Package
echo 2. Right-click install_service.bat, Run as Administrator
echo 3. Run HashGuard.exe
echo.
pause
