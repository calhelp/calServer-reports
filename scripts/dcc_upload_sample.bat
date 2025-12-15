@echo off
setlocal enabledelayedexpansion

:: ==============================================
:: === Konfiguration =============================
:: ==============================================

:: Ziel-API-Domain (ohne https://)
set DOMAIN=deine.domain.tld

:: Authentifizierungsparameter
set HTTP_X_REST_USERNAME=deinUser
set HTTP_X_REST_PASSWORD=deinPasswort
set HTTP_X_REST_API_KEY=deinApiKey

:: Ziel-Report-ID für den Upload (DCC)
set REPORT_ID=517d5a02-281b-4564-95c0-bdaf3cab5604

:: Name der ZIP-Datei (ohne Pfad)
set ZIP_NAME=dcc-sample.zip

:: Pfade der zu packenden Ordner relativ zum Skript
set SOURCE_FOLDER=DCC
:: Mehrere Ordner mit Leerzeichen trennen (z. B. "main_reports subreports")
set SUBFOLDERS=main_reports subreports
set TEMP_STAGE=_dcc_stage

:: ==============================================
:: === Verarbeitung ==============================
:: ==============================================

:: ZIP-Ausgabeordner vorbereiten
mkdir zip_output 2>nul

:: ZIP erstellen (JRXML + XSD/MD/JSON für DCC)
pushd %SOURCE_FOLDER% >nul

if exist "%TEMP_STAGE%" rd /s /q "%TEMP_STAGE%"
mkdir "%TEMP_STAGE%" >nul

for %%F in (%SUBFOLDERS%) do (
  if exist "%%F" (
    robocopy "%%F" "%TEMP_STAGE%\%%F" *.jrxml *.xsd *.md *.json /S >nul
    if ERRORLEVEL 8 (
      echo ❌ Fehler beim Kopieren der Reportdateien aus %%F.
      if exist "%TEMP_STAGE%" rd /s /q "%TEMP_STAGE%"
      popd >nul
      exit /b 1
    )
  ) else (
    echo ⚠️ Ordner %%F wurde nicht gefunden und wird uebersprungen.
  )
)

set COPIED_FILES=0
for /f %%# in ('powershell -NoProfile -Command "(Get-ChildItem ''%TEMP_STAGE%'' -Recurse -Include *.jrxml,*.xsd,*.md,*.json).Count"') do set COPIED_FILES=%%#

if "%COPIED_FILES%"=="0" (
  echo ❌ Es wurden keine Reportdateien gefunden. ZIP wird nicht erstellt.
  rd /s /q "%TEMP_STAGE%"
  popd >nul
  exit /b 1
)

del /q "..\zip_output\%ZIP_NAME%" 2>nul
powershell -Command "Compress-Archive -Path %TEMP_STAGE%\* -DestinationPath ..\zip_output\%ZIP_NAME% -Force"

rd /s /q "%TEMP_STAGE%"
popd >nul

echo === Inhalt von %ZIP_NAME% ===
rmdir /s /q tmp_dcc 2>nul
powershell -Command "Expand-Archive -Path zip_output/%ZIP_NAME% -DestinationPath tmp_dcc -Force; Get-ChildItem -Recurse tmp_dcc"
echo.

curl -X POST "https://%DOMAIN%/api/report/%REPORT_ID%?HTTP_X_REST_USERNAME=%HTTP_X_REST_USERNAME%&HTTP_X_REST_PASSWORD=%HTTP_X_REST_PASSWORD%&HTTP_X_REST_API_KEY=%HTTP_X_REST_API_KEY%" ^
  -F "file=@zip_output/%ZIP_NAME%"

echo.
echo ✅ Upload abgeschlossen für DCC-Report-ID: %REPORT_ID%
pause
