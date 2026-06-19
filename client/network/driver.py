"""소켓 클라이언트 — 서버로 데이터를 송신한다.

환경변수(config.py)로 서버 주소와 MACHINE_ID를 주입받는다.
"""
import json
import socket
import threading
import time
from datetime import datetime

from common.exception import ServerConnectionError
from network.config import SERVER_HOST, SERVER_PORT, BACKUP_HOST, BACKUP_PORT, MACHINE_ID
from utils.structure import Queue


# ── 프로토콜 메시지 타입 ───────────────────────────────────
class MsgType:
    SYNC          = "SYNC"
    PURCHASE      = "PURCHASE"
    STOCK_UPDATE  = "STOCK_UPDATE"
    MONEY_UPDATE  = "MONEY_UPDATE"
    HEARTBEAT     = "HEARTBEAT"
    CONFIG_UPDATE = "CONFIG_UPDATE"


def encode(msg_type: str, data: dict) -> bytes:
    """메시지를 JSON + 개행으로 직렬화한다."""
    msg = {"type": msg_type, "machine_id": MACHINE_ID, "data": data}
    return (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")


# ── SocketClient (싱글턴) ────────────────────────────────
class SocketClient:
    """서버와의 TCP 연결을 관리하는 싱글턴 클라이언트.

    - 연결 실패 시 Backup 서버로 자동 전환
    - 연결이 끊어지면 다음 송신 시 자동 재연결
    """

    CONNECT_TIMEOUT = 5  # 연결 타임아웃 (초)

    def __init__(self):
        self.conn = None
        self.lock = threading.Lock()
        self.primary = (SERVER_HOST, SERVER_PORT)
        self.backup  = (BACKUP_HOST, BACKUP_PORT)
        self.current = self.primary

    def send(self, msg_type, data):
        with self.lock:
            payload = encode(msg_type, data)
            try:
                conn = self.ensure_connected()
                if conn is None:
                    return False
                conn.sendall(payload)
                return True
            except OSError:
                self.close()
                return False

    def ensure_connected(self):
        if self.conn is not None:
            return self.conn

        conn = self.try_connect(*self.current)
        if conn:
            self.conn = conn
            return conn

        if self.current != self.backup:
            print(f"기본 서버 연결 실패 → Backup({self.backup[0]}:{self.backup[1]}) 시도")
            conn = self.try_connect(*self.backup)
            if conn:
                self.current = self.backup
                self.conn = conn
                return conn

        print("서버 연결 실패 — 오프라인 모드")
        return None

    def try_connect(self, host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.CONNECT_TIMEOUT)
            sock.connect((host, port))
            sock.settimeout(None)
            print(f"[Driver] 서버 연결 성공 → {host}:{port}  (machine_id={MACHINE_ID})")
            return sock
        except OSError as e:
            print(f"[Driver] 연결 시도 실패 {host}:{port} — {e}")
            return None

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except OSError:
                pass
            self.conn = None


# ── 수신 스레드 ──────────────────────────────────────────
class ReceiverThread(threading.Thread):
    """서버에서 push된 메시지를 수신하는 백그라운드 스레드."""

    def __init__(self, client, on_alert, on_drink_update, on_message_log=None):
        super().__init__(daemon=True)
        self.client          = client
        self.on_alert        = on_alert
        self.on_drink_update = on_drink_update
        self.on_message_log  = on_message_log
        self.running         = True
        self.msg_queue       = Queue()   # 수신 버퍼 (처리 후 비워짐)
        self.msg_queue_log   = Queue()   # 표시용 로그 (최대 3개 유지)
        self.MAX_LOG         = 3

    def run(self):
        buffer = ""
        while self.running:
            # 1단계: 수신 후 큐에 적재
            try:
                conn = self.client.conn
                if conn is None:
                    time.sleep(1)
                    continue
                data = conn.recv(4096)
                if not data:
                    time.sleep(1)
                    continue
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        self.msg_queue.enqueue(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            except OSError:
                time.sleep(1)
                continue

            # 2단계: 큐에서 꺼내 콜백 처리 + 로그 갱신
            while not self.msg_queue.is_empty():
                msg      = self.msg_queue.dequeue()
                msg_type = msg.get("type")
                payload  = msg.get("data", {})
                log_text = self._format_log(msg_type, payload)
                if log_text:
                    self.msg_queue_log.enqueue(log_text)
                    if self.msg_queue_log.size() > self.MAX_LOG:
                        self.msg_queue_log.dequeue()
                    if self.on_message_log:
                        self.on_message_log(self.msg_queue_log.to_list())
                if msg_type == "ALERT" and self.on_alert:
                    self.on_alert(payload)
                elif msg_type == "DRINK_UPDATE" and self.on_drink_update:
                    self.on_drink_update(payload)

    @staticmethod
    def _format_log(msg_type, payload):
        if msg_type == "ALERT":
            name  = payload.get("drink_name", "")
            level = "품절" if int(payload.get("stock_alert", 1)) == 2 else "재고 부족"
            return f"[알림] {name} {level}"
        if msg_type == "DRINK_UPDATE":
            return f"[변경] {payload.get('drink_name', '')} {payload.get('price', '')}원"
        return None

    def stop(self):
        self.running = False


# ── 헬스체크 스레드 ──────────────────────────────────────
class HeartbeatThread(threading.Thread):
    INTERVAL = 10  # 헬스체크 주기 (초)

    def __init__(self, client, get_sync_data):
        super().__init__(daemon=True)
        self.client = client
        self.get_sync_data = get_sync_data
        self.running = True


    def run(self):
        while self.running:
            time.sleep(self.INTERVAL)

            # 프라이머리 복구 감지 (백업 연결 중일 때)
            if self.try_return_to_primary():
                continue

            was_connected = self.client.conn is not None
            ok = self.client.send(MsgType.HEARTBEAT, {})
            # 서버 연결 실패 시
            if not ok:
                print("[Heartbeat] 서버 미연결 — 재연결 시도 중")
            # 서버 재연결 시
            elif not was_connected:
                send_sync(self.get_sync_data)

    def try_return_to_primary(self) -> bool:
        # 백업 연결 중일 때만 프라이머리 재시도
        with self.client.lock:
            if self.client.current != self.client.backup or self.client.conn is None:
                return False
            primary_conn = self.client.try_connect(*self.client.primary)
            if not primary_conn:
                return False
            self.client.close()
            self.client.conn = primary_conn
            self.client.current = self.client.primary
            host, port = self.client.primary
            print(f"[Heartbeat] 프라이머리 복구 → {host}:{port} 재연결")
        send_sync(self.get_sync_data)
        return True

    def stop(self):
        self.running = False


# 모듈 수준 싱글턴
client   = SocketClient()
heartbeat = None
receiver  = None


def is_connected():
    return client.conn is not None


def start_health_check(get_sync_data, on_alert=None, on_drink_update=None, on_message_log=None):
    """초기 서버 연결을 시도하고 헬스체크/수신 스레드를 시작한다. 연결 성공 시 True."""
    global heartbeat, receiver
    with client.lock:
        connected = client.ensure_connected() is not None
    # 최초 연결 시 동기화 데이터 전송
    if connected:
        send_sync(get_sync_data)
    # 헬스체크 스레드
    if heartbeat is None or not heartbeat.is_alive():
        heartbeat = HeartbeatThread(client, get_sync_data)
        heartbeat.start()
        print(f"[Heartbeat] 시작 (주기: {HeartbeatThread.INTERVAL}초)")
    # 수신 스레드
    if (on_alert or on_drink_update or on_message_log) and (receiver is None or not receiver.is_alive()):
        receiver = ReceiverThread(client, on_alert, on_drink_update, on_message_log)
        receiver.start()
        print("[Receiver] 수신 스레드 시작")
    return connected


# ── 공개 API ─────────────────────────────────────────────
def send_sync(get_sync_data) -> None:
    drinks, money_data = get_sync_data()
    data = {
        "stocks": [
            {"drink_id": d.id, "drink_name": d.name, "count": d.count}
            for d in drinks
        ],
        "denominations": {m.name: m.count for m in money_data.get_datas()},
    }
    client.send(MsgType.SYNC, data)


def send_purchase(drink_id, drink_name, price, stock_alert, stock_count, money_data) -> None:
    """구매 완료 이벤트를 서버로 전송한다. 실패 시 ServerConnectionError 발생."""
    data = {
        "drink_id"     : drink_id,
        "drink_name"   : drink_name,
        "price"        : price,
        "stock_alert"  : stock_alert,
        "stock_count"  : stock_count,
        "denominations": {m.name: m.count for m in money_data.get_datas()},
        "date"         : datetime.now().strftime("%Y-%m-%d"),
    }
    if not client.send(MsgType.PURCHASE, data):
        raise ServerConnectionError()


def send_stock(drink_id, drink_name, count) -> bool:
    data = {
        "drink_id"    : drink_id,
        "drink_name"  : drink_name,
        "count"       : count,
        "updated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return client.send(MsgType.STOCK_UPDATE, data)


def send_money(money_data) -> bool:
    denominations = {m.name: m.count for m in money_data.get_datas()}
    return client.send(MsgType.MONEY_UPDATE, {"denominations": denominations})


def send_config_update(low_stock_threshold: int) -> bool:
    return client.send(MsgType.CONFIG_UPDATE, {"low_stock_threshold": low_stock_threshold})
