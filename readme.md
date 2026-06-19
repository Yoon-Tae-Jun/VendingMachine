# 실행 가이드 (macOS)

## 0. 개발 환경

- **macOS** (스크립트가 `osascript`로 터미널 창을 띄우므로 macOS 전용)
- **Python 3.10 이상** 설치 확인


디렉터리 구조:

```
네트워크프로그래밍/
├── backend/         # 서버 소스 + server_venv
├── client/          # 클라이언트 소스 + client_venv
├── run_servers.sh   # 서버 3대 실행
└── run_clients.sh   # 클라이언트 4대 실행
```

---

## 1. 가상환경 설정 (최초 1회)


| 구분 | 가상환경 경로 | 의존성 파일 |
|------|---------------|-------------|
| 서버 | `backend/server_venv` | `backend/requirements.txt` |
| 클라이언트 | `client/client_venv` | `client/requirements.txt` |

### 1-1. 서버 가상환경

```bash
python3 -m venv backend/server_venv
source backend/server_venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
deactivate
```

### 1-2. 클라이언트 가상환경

```bash
python3 -m venv client/client_venv
source client/client_venv/bin/activate
pip install --upgrade pip
pip install -r client/requirements.txt
deactivate
```



---

## 2. 가상환경 진입 / 종료 (수동 실행 시)
```bash
cd backend
source server_venv/bin/activate
```

```bash
cd client
source client_venv/bin/activate
```

---

## 3. 셸 스크립트로 일괄 실행

### 3-1. 실행 권한 부여 (최초 1회)

```bash
chmod +x run_servers.sh run_clients.sh
```

### 3-2. 서버 먼저 실행

```bash
./run_servers.sh
```


| 서버 | 포트 | 데이터 디렉터리 |
|------|------|-----------------|
| Server1 | 9000 | `backend/data/server1` |
| Server2 | 9001 | `backend/data/server2` |
| Backup  | 9002 | `backend/data/backup`  |


### 3-3. 클라이언트 실행

```bash
./run_clients.sh
```

| 클라이언트 | machine_id | 접속 서버 | 작업 디렉터리 |
|-----------|-----------|-----------|----------------|
| Client1 | 1 | 127.0.0.1:9000 | `client_instances/client1/data/` |
| Client2 | 2 | 127.0.0.1:9000 | `client_instances/client2/data/` |
| Client3 | 3 | 127.0.0.1:9001 | `client_instances/client3/data/` |
| Client4 | 4 | 127.0.0.1:9001 | `client_instances/client4/data/` |

---