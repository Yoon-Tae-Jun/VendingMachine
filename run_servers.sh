
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend"
VENV_ACTIVATE="${BACKEND_DIR}/server_venv/bin/activate"

run_server() {
    local tcp_port=$1

    local cmd="cd '${BACKEND_DIR}' && \
source '${VENV_ACTIVATE}' && \
python3 main.py --port ${tcp_port}"

    osascript -e "tell application \"Terminal\" to do script \"${cmd}\""
}

echo "서버 3대 시작..."
echo "  Server1 → TCP 9000"
echo "  Server2 → TCP 9001"
echo "  Backup  → TCP 9002"

run_server 9000
sleep 0.5
run_server 9001
sleep 0.5
run_server 9002

echo "완료."
