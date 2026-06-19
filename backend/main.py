"""서버 진입점.

TCP 소켓 서버와 PyQt6 GUI를 통합 실행한다.

사용법:
    python main.py [--port 9000]
"""

import argparse
import sys
import threading

from PyQt6.QtWidgets import QApplication

from server import Server
from ui.ServerWindow import ServerWindow


def parse_args():
    p = argparse.ArgumentParser(description="자판기 관리 서버")
    p.add_argument("--port", type=int, default=9000, help="TCP 포트 (기본: 9000)")
    return p.parse_args()


def main():
    args = parse_args()

    # Server 인스턴스
    server = Server(host="0.0.0.0", port=args.port)

    # TCP 서버(daemon 스레드)
    tcp_thread = threading.Thread(target=server.start, daemon=True)
    tcp_thread.start()
    print(f"[TCP] 서버 시작 → 0.0.0.0:{args.port}")

    # PyQt6 GUI
    app    = QApplication(sys.argv)
    window = ServerWindow(server)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
