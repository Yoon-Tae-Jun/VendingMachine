from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import pyqtSignal, pyqtSlot

from ui.widget.AdminWidget import AdminWidget
from ui.widget.VendingMachineWidget import VendingMachineWidget
import ui.frame.AdminFrame as admin_frame
from utils.util import PasswordManager

class MainUI(QMainWindow):
    message_log_updated = pyqtSignal(list)

    def __init__(self, vending_machine, sales_manager):
        super().__init__()

        # 자판기, 매출 인스턴스 저장
        self.vending_machine = vending_machine
        self.sales_manager = sales_manager
        self.pw_manager = PasswordManager()  # 비밀번호 관리자

        self.initUI()

    def initUI(self):
        # 윈도우 설정
        self.setWindowTitle(f"Vending Machine #{self.vending_machine.machine_id}")
        self.setGeometry(0, 0, 900, 460)
        self.setStyleSheet("background-color: #1A1A2E; color: white;")
        
        # 스택 위젯 생성
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 판매 화면, 관리자 화면 추가
        self.stack.addWidget(VendingMachineWidget(self.vending_machine, self.on_click_admin))
        self.stack.addWidget(AdminWidget(self.vending_machine, self.sales_manager, self.exit_admin))
        self.message_log_updated.connect(self.update_message_log)

    # 관리자 화면 -> 판매 화면 이동
    def exit_admin(self):
        self.stack.setCurrentIndex(0)

    # 판매 화면 -> 관리자 화면 이동
    def on_click_admin(self):
        # 비밀번호 검증 후 관리자 화면으로 이동
        dialog = admin_frame.AdminPasswordDialog(self)
        if dialog.exec():
            self.stack.setCurrentIndex(1)

    # 서버 push — 재고 부족 알림 (QMetaObject.invokeMethod로 호출)
    @pyqtSlot(str)
    def show_alert(self, msg: str):
        QMessageBox.warning(self, "재고 알림", msg)

    # 서버 push — 음료 이름/가격 변경 (QMetaObject.invokeMethod로 호출)
    @pyqtSlot(int, str, int)
    def apply_drink_update(self, drink_id: int, name: str, price: int):
        self.vending_machine.update_drink(drink_id, name, price)
        vm_widget = self.stack.widget(0)
        vm_widget.drink_frame.refresh(self.vending_machine.get_drinks(), self.vending_machine.get_input_money())

    # 서버 push — 메시지 로그 갱신 (message_log_updated signal로 호출)
    @pyqtSlot(list)
    def update_message_log(self, messages: list):
        vm_widget = self.stack.widget(0)
        vm_widget.message_log_frame.update_log(messages)

    # 앱 종료 시 잔액 자동 반환
    def closeEvent(self, event):
        input_money = self.vending_machine.get_input_money()
        if input_money > 0:
            res = self.vending_machine.refund_money()
            QMessageBox.information(self, "잔돈 반환", f"투입된 금액 {input_money}원을 반환합니다.\n{res.msg}")
        event.accept()