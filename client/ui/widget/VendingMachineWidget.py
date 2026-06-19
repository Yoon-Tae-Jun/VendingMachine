from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
import ui.frame.VendingMachineFrame as frame

class VendingMachineWidget(QWidget):
    def __init__(self, vending_machine, on_click_admin):
        super().__init__()
        self.vending_machine = vending_machine
        self.on_click_admin = on_click_admin


        self.init_vending_machine_ui(
            self.vending_machine.get_drinks(), 
            self.vending_machine.get_money_data()
        )

    def init_vending_machine_ui(self, drinks_list, money_list):
        # 화면 설정
        self.setFixedHeight(460)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 상단 레이아웃(음료 선택 버튼)
        top_layout = QHBoxLayout()
        
        self.drink_frame = frame.DrinkFrame(drinks_list, self.on_click_drink) 
        top_layout.addWidget(self.drink_frame)
        self.main_layout.addLayout(top_layout)

        # 하단 레이아웃(잔액 및 돈 투입 버튼)
        bottom_layout = QHBoxLayout()
        self.balance_frame = frame.BalanceFrame() # 잔액 및 상태 표시 프레임
        self.money_input_frame = frame.MoneyInputFrame(
            money_list, 
            self.on_click_money, 
            self.on_click_refund, 
            self.on_click_admin
        )
        bottom_layout.addWidget(self.balance_frame)
        bottom_layout.addWidget(self.money_input_frame)
        self.main_layout.addLayout(bottom_layout)

        self.message_log_frame = frame.MessageLogFrame()
        self.main_layout.addWidget(self.message_log_frame)

    # 반환 버튼 이벤트
    def on_click_refund(self):
        try:
            res = self.vending_machine.refund_money()
            self.update_screen(res.input_money, res.msg)
        except Exception as e:
            self.balance_frame.update_balance(self.vending_machine.get_input_money(), f"오류: {e}")

    # 돈 투입 버튼 이벤트
    def on_click_money(self):
        try:
            button = self.sender()
            amount = button.text()[:-1]  # "1000원"에서 "1000" 추출
            res = self.vending_machine.insert_money(amount)
            self.update_screen(res.input_money, res.msg)
        except Exception as e:
            self.balance_frame.update_balance(self.vending_machine.get_input_money(), f"오류: {e}")

    # 음료 선택 버튼 이벤트
    def on_click_drink(self):
        try:
            button = self.sender()
            drink_name = button.text().split('\n')[0]
            res = self.vending_machine.purchase_drink(drink_name)
            self.update_screen(res.money_res.input_money, res.money_res.msg)
        except Exception as e:
            self.balance_frame.update_balance(self.vending_machine.get_input_money(), f"오류: {e}")

    # 관리자 화면 -> 판매 화면 이동 시 화면 새로고침
    def showEvent(self, event):
        super().showEvent(event)
        self.drink_frame.refresh(self.vending_machine.get_drinks(), self.vending_machine.get_input_money())

    # 화면 업데이트 함수(잔액 및 음료 버튼 상태)
    def update_screen(self, amount, msg):
        self.balance_frame.update_balance(amount, msg)
        self.drink_frame.refresh(self.vending_machine.get_drinks(), amount)

    
