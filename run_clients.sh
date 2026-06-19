
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLIENT_DIR="${SCRIPT_DIR}/client"
INSTANCES_DIR="${SCRIPT_DIR}/client_instances"

# 클라이언트별 격리 디렉토리 준비
setup_instance() {
    local machine_id=$1
    local inst_dir="${INSTANCES_DIR}/client${machine_id}"

    mkdir -p "${inst_dir}/data"

    # data/ 가 없는 경우 원본 CSV를 복사
    for csv in drink.csv money.csv sales.csv config.csv; do
        if [ ! -f "${inst_dir}/data/${csv}" ] && [ -f "${CLIENT_DIR}/data/${csv}" ]; then
            cp "${CLIENT_DIR}/data/${csv}" "${inst_dir}/data/${csv}"
        fi
    done
}

run_client() {
    local machine_id=$1
    local inst_dir="${INSTANCES_DIR}/client${machine_id}"

    # 원본 소스를 PYTHONPATH로 잡고, 작업 디렉토리만 인스턴스 디렉토리로 설정
    # machine_id는 위치 인자로 전달 (config.py 참고)
    local cmd="cd '${inst_dir}' && \
source '${CLIENT_DIR}/client_venv/bin/activate' && \
PYTHONPATH='${CLIENT_DIR}' \
python3 '${CLIENT_DIR}/main.py' ${machine_id}"

    osascript -e "tell application \"Terminal\" to do script \"${cmd}\""
}

echo "클라이언트 인스턴스 디렉토리 준비..."
for i in 1 2 3 4; do
    setup_instance $i
done

echo "클라이언트 4대 시작..."
echo "  Client1 (machine_id=1) → 127.0.0.1:9000"
echo "  Client2 (machine_id=2) → 127.0.0.1:9000"
echo "  Client3 (machine_id=3) → 127.0.0.1:9001"
echo "  Client4 (machine_id=4) → 127.0.0.1:9001"

run_client 1
sleep 0.5
run_client 2
sleep 0.5
run_client 3
sleep 0.5
run_client 4

echo "완료. 각 클라이언트 데이터: ${INSTANCES_DIR}/client{N}/data/"
