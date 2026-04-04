@echo off
REM LabGuard Edge Agent 설치 스크립트 (Windows)
REM 실행: cd edge_agent && setup.bat

echo === LabGuard Edge Agent 설치 ===

REM 1. Python 버전 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo Python3이 필요합니다.
    pause
    exit /b 1
)

REM 2. 가상환경 생성
if not exist ".venv" (
    echo [1/3] 가상환경 생성...
    python -m venv .venv
) else (
    echo [1/3] 가상환경 이미 존재, 건너뜁니다.
)

REM 3. 패키지 설치
echo [2/3] 패키지 설치...
.venv\Scripts\pip install --quiet --upgrade pip
.venv\Scripts\pip install --quiet -r requirements.txt

REM 4. .env 파일 생성
if not exist ".env" (
    echo [3/3] .env 파일 생성...
    copy .env.example .env >nul
    echo.
    echo 주의: .env 파일이 생성됐습니다.
    echo       DEVICE_ID를 설정해야 합니다:
    echo.
    echo       1. LabGuard 웹 열기 -^> 장비 관리 -^> 장비 추가
    echo       2. 등록 후 장비 클릭 -^> URL의 UUID 복사
    echo       3. .env 파일에서 DEVICE_ID=여기에_장비_UUID_입력 수정
    echo.
) else (
    echo [3/3] .env 파일 이미 존재, 건너뜁니다.
)

echo.
echo === 설치 완료 ===
echo.
echo 실행 방법:
echo   .venv\Scripts\python main.py
echo.
echo Arduino 연결 확인:
echo   Arduino를 USB로 연결하면 SERIAL_PORT=auto 로 자동 감지됩니다.
echo.
pause
