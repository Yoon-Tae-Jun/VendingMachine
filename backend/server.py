import csv
import json
import os
import socket
import threading
import time
from datetime import datetime

from common.sales_bst import SalesBST

SALES_FIELDS = ["date", "machine_id", "drink_id", "drink_name", "price", "stock_alert"]
STOCK_FIELDS = ["drink_id", "drink_name", "count", "updated_time"]
MONEY_FIELDS = ["denomination", "count", "updated_time"]

PORT_DATA_MAP = {
    9000: "data/server1",
    9001: "data/server2",
    9002: "data/backup",
}

# 서버 맵(full-mesh)
PEER_MAP = {
    9000: [("127.0.0.1", 9001), ("127.0.0.1", 9002)],
    9001: [("127.0.0.1", 9000), ("127.0.0.1", 9002)],
    9002: [("127.0.0.1", 9000), ("127.0.0.1", 9001)],
}

BUFFER_SIZE = 4096
BACKLOG = 10
REPLICATE_TIMEOUT = 2  # 피어 전송 타임아웃 (초)


class Server:
    def __init__(self, host="0.0.0.0", port=9000):
        # 서버 설정, 쓰레드 락 및 데이터 초기화
        self.host = host
        self.port = port
        self.data_lock = threading.Lock()
        self.clients_lock = threading.Lock()
        self.sales_bst = SalesBST()
        self.clients: dict = {}
        self.stocks: dict = {}
        self.money: dict = {}
        self.thresholds: dict = {}  # machine_id → low_stock_threshold

        # 사바 정보 및 상태 초기화
        self.peers = PEER_MAP.get(port, [])
        self.peer_status: dict = {(h, p): True for h, p in self.peers}

        # 폴더 경로 설정
        self.data_dir = PORT_DATA_MAP.get(port, f"data/server_{port}")
        self.stock_dir = os.path.join(self.data_dir, "stock")
        self.money_dir = os.path.join(self.data_dir, "money")
        self.sales_file = os.path.join(self.data_dir, "sales.csv")

        #폴더 생성
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.stock_dir, exist_ok=True)
        os.makedirs(self.money_dir, exist_ok=True)
        self.init_sales_file()
        self.load_sales_to_bst()
        self.load_stock_to_memory()

    @staticmethod
    def encode(msg_type: str, data: dict) -> bytes:
        # 개행 구분 JSON 직렬화
        msg = {"type": msg_type, "data": data}
        return (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")

    # 파일 없을 때만 헤더 생성 (DictReader 오동작 방지)
    def init_sales_file(self):
        if not os.path.exists(self.sales_file):
            with open(self.sales_file, "w", encoding="utf-8", newline="") as f:
                csv.DictWriter(f, fieldnames=SALES_FIELDS).writeheader()

    # 기동 시 sales.csv → BST 인메모리 복원
    def load_sales_to_bst(self):
        if not os.path.exists(self.sales_file):
            return
        with open(self.sales_file, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                self.sales_bst.insert(row)
        print(f"[BST] {self.sales_file} 복원 완료 — {len(self.sales_bst.inorder())}건")
    
    # 기동 시 머신별 stock CSV → self.stocks 복원
    def load_stock_to_memory(self):
        for fname in os.listdir(self.stock_dir):
            if not fname.startswith("machine_"):
                continue
            try:
                mid = int(fname.replace("machine_", "").replace(".csv", ""))
            except ValueError:
                continue
            path = os.path.join(self.stock_dir, fname)
            self.stocks[mid] = {}
            with open(path, encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    self.stocks[mid][row["drink_id"]] = {
                        "name": row["drink_name"],
                        "count": int(row["count"]),
                    }
        print(f"[Stock] {self.stock_dir} 로드 완료 — {len(self.stocks)}대")

    # accept 루프, 연결마다 데몬 스레드 분기
    def start(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen(BACKLOG)
        print(f"[Server] {self.host}:{self.port}  data={self.data_dir}")
        if self.peers:
            peers = ", ".join(f"{h}:{p}" for h, p in self.peers)
            print(f"[Replication] 피어: {peers}")
            threading.Thread(target=self.health_check_loop, daemon=True).start()

        while True:
            conn, addr = server_sock.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    # 10초 주기 피어 연결 확인, peer_status 갱신
    def health_check_loop(self):
        while True:
            time.sleep(10)
            for (host, port) in self.peers:
                try:
                    with socket.create_connection((host, port), timeout=2):
                        pass
                    alive = True
                except OSError:
                    alive = False
                prev = self.peer_status.get((host, port), True)
                self.peer_status[(host, port)] = alive
                if prev and not alive:
                    print(f"[HealthCheck] {host}:{port} 장애 감지")
                elif not prev and alive:
                    print(f"[HealthCheck] {host}:{port} 복구 감지")

    # 연결별 수신 루프, 첫 비-REPLICATE 메시지의 machine_id로 clients 등록
    def handle_client(self, conn, addr):
        print(f"[+] 연결: {addr}")
        machine_id = None
        buffer = ""
        try:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    msg = self.parse_message(line)
                    if msg is None:
                        continue
                    mid = msg.get("machine_id", 0)
                    # 피어 복제 연결은 클라이언트로 등록 X
                    if machine_id is None and mid and msg.get("type") != "REPLICATE":
                        machine_id = mid
                        with self.clients_lock:
                            self.clients[machine_id] = conn
                        print(f"[등록] machine={machine_id} ← {addr}")
                    self.dispatch_message(msg)
        except (ConnectionResetError, OSError):
            pass
        finally:
            conn.close()
            if machine_id is not None:
                with self.clients_lock:
                    self.clients.pop(machine_id, None)
            print(f"[-] 연결 종료: {addr}  machine={machine_id}")

    # JSON 파싱
    def parse_message(self, line: str):
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            print(f"[파싱 오류] {line}")
            return None

    # 타입별 핸들러 라우팅 (HEARTBEAT는 소켓 생존 확인용, 별도 처리 없음)
    def dispatch_message(self, msg: dict):
        msg_type = msg.get("type")
        machine_id = msg.get("machine_id", 0)
        data = msg.get("data", {})

        if msg_type == "SYNC":
            self.on_sync(machine_id, data)
        elif msg_type == "PURCHASE":
            self.on_purchase(machine_id, data)
        elif msg_type == "STOCK_UPDATE":
            self.on_stock_update(machine_id, data)
        elif msg_type == "MONEY_UPDATE":
            self.on_money_update(machine_id, data)
        elif msg_type == "REPLICATE":
            self.on_replicate(machine_id, data)
        elif msg_type == "CONFIG_UPDATE":
            self.on_config_update(machine_id, data)
        elif msg_type == "HEARTBEAT":
            pass

    # 접속·재연결 시 전체 재고·시재 등록 (replicate=False면 피어 전파 생략)
    def on_sync(self, machine_id: int, data: dict, replicate: bool = True):
        updated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for stock in data.get("stocks", []):
            self.on_stock_update(machine_id, {**stock, "updated_time": updated_time}, replicate=False)
        self.on_money_update(machine_id, {"denominations": data.get("denominations")}, replicate=False)
        if replicate:
            self.replicate("SYNC", machine_id, data)
        print(f"[SYNC] machine={machine_id} 초기 동기화 완료")

    # 매출 기록 → 재고·시재 갱신 → 피어 복제 → ALERT push
    def on_purchase(self, machine_id: int, data: dict, replicate: bool = True):
        row = {
            "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "machine_id": machine_id,
            "drink_id": data.get("drink_id"),
            "drink_name": data.get("drink_name"),
            "price": data.get("price"),
            "stock_alert": data.get("stock_alert", 0),
        }
        with self.data_lock:
            with open(self.sales_file, "a", encoding="utf-8", newline="") as f:
                csv.DictWriter(f, fieldnames=SALES_FIELDS).writerow(row)
            self.sales_bst.insert(row)
        print(f"[PURCHASE] machine={machine_id} {row['drink_name']} {row['price']}원")

        self.on_stock_update(machine_id, {
            "drink_id": data.get("drink_id"),
            "drink_name": data.get("drink_name"),
            "count": data.get("stock_count"),
            "updated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }, replicate=False)
        self.on_money_update(machine_id, {"denominations": data.get("denominations")}, replicate=False)

        if replicate:
            self.replicate("PURCHASE", machine_id, data)
            # ALERT push는 구매가 발생한 원본 서버에서만 (피어는 클라이언트 미연결).
            stock_alert = int(data.get("stock_alert", 0))
            if stock_alert >= 1:
                self.send_to_client(machine_id, "ALERT", {
                    "drink_name": data.get("drink_name"),
                    "stock_count": data.get("stock_count"),
                    "stock_alert": stock_alert,
                })

    # 머신별 재고 파일 upsert (전체 재작성)
    def on_stock_update(self, machine_id: int, data: dict, replicate: bool = True):
        stock_file = os.path.join(self.stock_dir, f"machine_{machine_id}.csv")
        drink_id = str(data.get("drink_id"))
        count = data.get("count")
        new_row = {
            "drink_id": drink_id,
            "drink_name": data.get("drink_name"),
            "count": count,
            "updated_time": data.get("updated_time"),
        }
        with self.data_lock:
            rows = {}
            if os.path.exists(stock_file):
                with open(stock_file, encoding="utf-8", newline="") as f:
                    for row in csv.DictReader(f):
                        rows[row["drink_id"]] = row
            rows[drink_id] = new_row
            with open(stock_file, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=STOCK_FIELDS)
                w.writeheader()
                w.writerows(rows.values())

        if machine_id not in self.stocks:
            self.stocks[machine_id] = {}
        self.stocks[machine_id][drink_id] = {
            "name": data.get("drink_name"),
            "count": int(count) if count is not None else 0,
        }
        if replicate:
            self.replicate("STOCK_UPDATE", machine_id, data)
        print(f"[STOCK] machine={machine_id} {data.get('drink_name')} {count}개")

    # 시재 전체 스냅샷 저장 (증분 방식은 미전송 시 불일치 발생)
    def on_money_update(self, machine_id: int, data: dict, replicate: bool = True):
        money_file = os.path.join(self.money_dir, f"machine_{machine_id}.csv")
        denominations = data.get("denominations", {})
        updated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.data_lock:
            with open(money_file, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=MONEY_FIELDS)
                w.writeheader()
                for denom, count in denominations.items():
                    w.writerow({"denomination": denom, "count": count, "updated_time": updated_time})

        self.money[machine_id] = {str(k): int(v) for k, v in denominations.items()}
        if replicate:
            self.replicate("MONEY_UPDATE", machine_id, data)
        print(f"[MONEY] machine={machine_id} 시재 업데이트")

    # 머신별 임계값 갱신, 피어 복제
    def on_config_update(self, machine_id: int, data: dict, replicate: bool = True):
        threshold = data.get("low_stock_threshold")
        if threshold is not None:
            self.thresholds[machine_id] = int(threshold)
        if replicate:
            self.replicate("CONFIG_UPDATE", machine_id, data)
        print(f"[CONFIG] machine={machine_id} low_stock_threshold={threshold}")

    # 서버 간 데이터 복제
    def on_replicate(self, machine_id: int, data: dict):
        inner_type = data.get("inner_type")
        inner_data = data.get("inner_data", {})
        if inner_type == "SYNC":
            self.on_sync(machine_id, inner_data, replicate=False)
        elif inner_type == "PURCHASE":
            self.on_purchase(machine_id, inner_data, replicate=False)
        elif inner_type == "STOCK_UPDATE":
            self.on_stock_update(machine_id, inner_data, replicate=False)
        elif inner_type == "MONEY_UPDATE":
            self.on_money_update(machine_id, inner_data, replicate=False)
        elif inner_type == "CONFIG_UPDATE":
            self.on_config_update(machine_id, inner_data, replicate=False)
        else:
            return
        print(f"[REPLICATE←] machine={machine_id} {inner_type} 반영")

    #  데이터 변경
    def replicate(self, inner_type: str, machine_id: int, data: dict):
        if not self.peers:
            return
        msg = {
            "type": "REPLICATE",
            "machine_id": machine_id,
            "data": {"inner_type": inner_type, "inner_data": data},
        }
        payload = (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")
        for host, port in self.peers:
            threading.Thread(
                target=self.send_replication,
                args=(host, port, payload, inner_type),
                daemon=True,
            ).start()

    # 단일 피어에 복제 메시지 전송
    def send_replication(self, host: str, port: int, payload: bytes, inner_type: str):
        try:
            with socket.create_connection((host, port), timeout=REPLICATE_TIMEOUT) as sock:
                sock.sendall(payload)
            print(f"[REPLICATE→] {host}:{port} {inner_type}")
        except OSError:
            pass

    # 클라이언트 push 전송, 실패 시 clients에서 제거
    def send_to_client(self, machine_id: int, msg_type: str, data: dict) -> bool:
        with self.clients_lock:
            conn = self.clients.get(machine_id)
        if conn is None:
            print(f"[PUSH] machine={machine_id} 미연결 — {msg_type} 전송 불가")
            return False
        try:
            conn.sendall(self.encode(msg_type, data))
            print(f"[PUSH] machine={machine_id} ← {msg_type}")
            return True
        except OSError as e:
            print(f"[PUSH] machine={machine_id} 전송 실패: {e}")
            with self.clients_lock:
                self.clients.pop(machine_id, None)
            return False
