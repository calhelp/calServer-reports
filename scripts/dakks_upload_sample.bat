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

:: Ziel-Report-ID für den Upload
set REPORT_ID=cd5797da-e7a9-0bc6-fc73-dedc595bd59b

:: Name der ZIP-Datei (ohne Pfad)
set ZIP_NAME=dakks-sample.zip

:: Pfade der zu packenden Ordner relativ zum Skript
set SOURCE_FOLDER=DAKKS-SAMPLE
set SUBFOLDERS=main_reports, subreports

:: ==============================================
:: === Verarbeitung ==============================
:: ==============================================

:: ZIP-Ausgabeordner vorbereiten
mkdir zip_output 2>nul

:: ZIP erstellen (ohne Oberordner)
cd %SOURCE_FOLDER%
powershell -Command "Compress-Archive -Path %SUBFOLDERS% -DestinationPath ../zip_output/%ZIP_NAME%"
cd ..

:: Optional: ZIP-Inhalte anzeigen
echo === Inhalt von %ZIP_NAME% ===
powershell -Command "Expand-Archive -Path zip_output/%ZIP_NAME% -DestinationPath tmp_dakks -Force; Get-ChildItem -Recurse tmp_dakks"
echo.

:: Upload mit curl
curl -X POST "https://%DOMAIN%/api/report/%REPORT_ID%?HTTP_X_REST_USERNAME=%HTTP_X_REST_USERNAME%&HTTP_X_REST_PASSWORD=%HTTP_X_REST_PASSWORD%&HTTP_X_REST_API_KEY=%HTTP_X_REST_API_KEY%" ^
  -F "file=@zip_output/%ZIP_NAME%"

echo.
echo ✅ Upload abgeschlossen für Report-ID: %REPORT_ID%
pause
