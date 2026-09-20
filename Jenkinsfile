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

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set Up Python Environment') {
            steps {
                bat '''
                    python -m venv %VENV_DIR%
                    call %VENV_DIR%\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                    python -m pip install -r requirements.txt
                    python -m pip install requests
                '''
            }
        }

        stage('Train Model') {
            steps {
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    python train_model.py
                '''
            }
        }

        stage('Start API & Smoke Test') {
            steps {
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat

                    start /B "" python app.py > app.log 2>&1

                    echo Waiting for API to become ready...

                    set READY=0

                    for /L %%i in (1,1,30) do (
                        powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri http://127.0.0.1:5000/ -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"

                        if not errorlevel 1 (
                            set READY=1
                            echo API is up
                            goto :api_ready
                        )

                        timeout /t 1 /nobreak >nul
                    )

                    :api_ready

                    if "%READY%"=="0" (
                        echo API did not start in time
                        type app.log
                        exit /b 1
                    )

                    python test_prediction.py
                '''
            }
        }
    }

    post {
        always {
            bat '''
                echo Cleaning up API process...

                powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*app.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"

                powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
            '''

            archiveArtifacts artifacts: 'house_model.pkl, app.log', allowEmptyArchive: true
        }

        success {
            echo 'Build, train, and smoke test succeeded.'
        }

        failure {
            echo 'Pipeline failed — check app.log and the console output above for details.'
        }

        cleanup {
            bat '''
                if exist "%VENV_DIR%" rmdir /S /Q "%VENV_DIR%"
            '''
        }
    }
}