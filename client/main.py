import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QMetaObject, Qt, Q_ARG

from core.vendingMachine import VendingMachine
from core.salesManager import SalesManager
from ui.main import MainUI
from network.driver import start_health_check
from network.config import MACHINE_ID


def main():
    app = QApplication(sys.argv)

    vending_machine = VendingMachine(MACHINE_ID)
    sales_manager   = SalesManager()

    window = MainUI(vending_machine, sales_manager)
    window.show()

    # ── 서버 push 콜백 ─────────────────────────────────
    def on_alert(data):
        """재고 부족 알림 — 백그라운드 스레드에서 호출되므로 메인 스레드로 위임."""
        drink_name  = data.get("drink_name", "")
        stock_count = data.get("stock_count", 0)
        stock_alert = int(data.get("stock_alert", 1))
        level       = "품절" if stock_alert == 2 else "재고 부족"
        msg         = f"[{level}] {drink_name}  (잔여: {stock_count}개)"
        QMetaObject.invokeMethod(
            window, "show_alert",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, msg),
        )

    def on_drink_update(data):
        """음료 이름/가격 변경 push — 메인 스레드로 위임."""
        drink_id = int(data.get("drink_id", 0))
        name     = data.get("drink_name", "")
        price    = int(data.get("price", 0))
        QMetaObject.invokeMethod(
            window, "apply_drink_update",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(int, drink_id),
            Q_ARG(str, name),
            Q_ARG(int, price),
        )

    def on_message_log(messages):
        window.message_log_updated.emit(messages)

    if not start_health_check(
        vending_machine.get_sync_data,
        on_alert=on_alert,
        on_drink_update=on_drink_update,
        on_message_log=on_message_log,
    ):
        QMessageBox.warning(None, "연결 실패", "서버에 연결할 수 없습니다.")

    app.exec()


if __name__ == "__main__":
    main()
