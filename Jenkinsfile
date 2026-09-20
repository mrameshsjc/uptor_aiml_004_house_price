pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {

        // ============================================================
        // 1. Checkout Source Code
        // ============================================================
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // ============================================================
        // 2. Verify Windows Commands
        // ============================================================
        stage('Test Windows Commands') {
            steps {
                bat '''
                    echo Checking required Windows commands...

                    where powershell
                    where timeout

                    echo.
                    echo PowerShell Version:
                    powershell -NoProfile -Command "$PSVersionTable.PSVersion"
                '''
            }
        }

        // ============================================================
        // 3. Set Up Python Virtual Environment
        // ============================================================
        stage('Set Up Python Environment') {
            steps {
                bat '''
                    echo Creating Python virtual environment...

                    python -m venv %VENV_DIR%

                    echo Activating virtual environment...
                    call %VENV_DIR%\\Scripts\\activate.bat

                    echo Upgrading pip...
                    python -m pip install --upgrade pip

                    echo Installing project dependencies...
                    python -m pip install -r requirements.txt

                    echo Installing requests...
                    python -m pip install requests
                '''
            }
        }

        // ============================================================
        // 4. Train Machine Learning Model
        // ============================================================
        stage('Train Model') {
            steps {
                bat '''
                    echo Activating virtual environment...
                    call %VENV_DIR%\\Scripts\\activate.bat

                    echo Training model...
                    python train_model.py
                '''
            }
        }

        // ============================================================
        // 5. Start Flask API and Run Smoke Test
        // ============================================================
        stage('Start API & Smoke Test') {
            steps {
                bat '''
                    echo Activating virtual environment...
                    call %VENV_DIR%\\Scripts\\activate.bat

                    echo Starting Flask API...

                    start /B "" python app.py > app.log 2>&1

                    echo.
                    echo Waiting for API to become ready...

                    set READY=0

                    for /L %%i in (1,1,30) do (

                        powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri http://127.0.0.1:5000/ -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"

                        if not errorlevel 1 (
                            set READY=1
                            echo API is up and responding.
                            goto :api_ready
                        )

                        echo API not ready yet... attempt %%i of 30
                        timeout /t 1 /nobreak >nul
                    )

                    :api_ready

                    if "%READY%"=="0" (
                        echo.
                        echo ERROR: API did not start within the expected time.
                        echo.
                        echo ===== app.log =====
                        type app.log
                        echo ===================
                        exit /b 1
                    )

                    echo.
                    echo Running prediction smoke test...
                    python test_prediction.py
                '''
            }
        }
    }

    // ================================================================
    // Post-Build Actions
    // ================================================================
    post {

        // ------------------------------------------------------------
        // Always execute - API cleanup + artifacts
        // ------------------------------------------------------------
        always {
            bat '''
                echo.
                echo Cleaning up API process...

                powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*app.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"

                powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
            '''

            archiveArtifacts(
                artifacts: 'house_model.pkl, app.log',
                allowEmptyArchive: true
            )
        }

        // ------------------------------------------------------------
        // Success
        // ------------------------------------------------------------
        success {
            echo 'Build, train, and smoke test succeeded.'
        }

        // ------------------------------------------------------------
        // Failure
        // ------------------------------------------------------------
        failure {
            echo 'Pipeline failed — check app.log and the console output above for details.'
        }

        // ------------------------------------------------------------
        // Cleanup Virtual Environment
        // ------------------------------------------------------------
        cleanup {
            bat '''
                echo Cleaning virtual environment...

                if exist "%VENV_DIR%" (
                    rmdir /S /Q "%VENV_DIR%"
                )

                echo Virtual environment cleanup completed.
            '''
        }
    }
}