#!/usr/bin/env bash
# ==============================================================================
# Gentleman Mosaic Next - Linux & macOS Launch Script
# ==============================================================================

# Ensure script runs from project root directory
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

CFG="config/launch.ini"
mkdir -p config

# Defaults
HOST="127.0.0.1"
PORT="7400"
UI_LANG="zh"
UI_THEME="system"

# Read basic settings from config/launch.ini if present
if [ -f "$CFG" ]; then
    while IFS='=' read -r key val; do
        # Strip comments and spaces
        key=$(echo "$key" | tr -d ' ' | tr -d '\r')
        val=$(echo "$val" | tr -d ' ' | tr -d '\r')
        case "$key" in
            host) HOST="$val" ;;
            port) PORT="$val" ;;
            language) UI_LANG="$val" ;;
            theme) UI_THEME="$val" ;;
        esac
    done < "$CFG"
fi

# Generate runtime config for standalone.html
cat <<EOF > config/runtime-config.js
window.APP_CONFIG = {
  backend_host: "${HOST}",
  backend_port: ${PORT},
  backend_url: "http://${HOST}:${PORT}",
  ui_lang: "${UI_LANG}",
  ui_theme: "${UI_THEME}"
};
EOF

# Verify backend/main.py exists
if [ ! -f "backend/main.py" ]; then
    echo "[ERROR] backend/main.py not found."
    exit 1
fi

# 1. Virtual Environment Setup
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] 未偵測到虛擬環境，正在為您建立 ${VENV_DIR}..."
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_BOOT="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_BOOT="python"
    else
        echo "[ERROR] 系統未安裝 Python，請先安裝 Python 3.10+。"
        exit 1
    fi

    "$PYTHON_BOOT" -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "[ERROR] 建立虛擬環境失敗。"
        exit 1
    fi

    echo "[INFO] 安裝輕量 CPU 版 PyTorch (約 180 MB，避免下載數 GB 冗餘套件)..."
    "$VENV_DIR/bin/pip" install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    if [ $? -ne 0 ]; then
        echo "[ERROR] PyTorch 安裝失敗。"
        exit 1
    fi

    echo "[INFO] 安裝後端相依套件 (backend/requirements.txt)..."
    "$VENV_DIR/bin/pip" install -r backend/requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] 套件安裝失敗。"
        exit 1
    fi
fi

PYTHON_EXE="$VENV_DIR/bin/python"

# 2. Check and free port if already occupied
if command -v lsof >/dev/null 2>&1; then
    PID=$(lsof -ti :$PORT)
    if [ -n "$PID" ]; then
        echo "[WARN] 偵測到 Port $PORT 已被 PID $PID 佔用，正在終止舊行程..."
        kill -9 $PID 2>/dev/null
        sleep 1
    fi
fi

# 3. Start Uvicorn Backend
echo "[INFO] 正在啟動後端服務: http://${HOST}:${PORT}"
"$PYTHON_EXE" -m uvicorn backend.main:app --host "$HOST" --port "$PORT" &
SERVER_PID=$!

# Trap signals to cleanly shutdown background uvicorn on script exit
trap "kill $SERVER_PID 2>/dev/null; exit 0" SIGINT SIGTERM EXIT

sleep 1

# 4. Open standalone.html in default browser
if [ -f "standalone.html" ]; then
    echo "[INFO] 正在開啟操作介面 standalone.html..."
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "standalone.html" >/dev/null 2>&1 &
    elif command -v open >/dev/null 2>&1; then
        open "standalone.html" >/dev/null 2>&1 &
    else
        echo "[提示] 請於瀏覽器中開啟專案目錄下的 standalone.html"
    fi
else
    echo "[WARN] standalone.html 不存在。"
fi

echo "[INFO] 後端服務運行中 (PID: $SERVER_PID)。按下 Ctrl+C 可停止服務。"
wait $SERVER_PID
