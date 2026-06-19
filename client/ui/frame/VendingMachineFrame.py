from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGridLayout, QPushButton
import ui.styles as style

# 잔액 및 상태 표시 프레임
class BalanceFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("balance_frame_container")
        self.setStyleSheet(style.BALANCE_FRAME)
        
        self.init_ui()
    
    def init_ui(self):
        # 화면 설정
        self.setFixedHeight(100)
        balance_layout = QVBoxLayout()
        balance_layout.setSpacing(0)
        
        # 잔액 라벨
        self.balance_label = QLabel("잔액: 0원")
        self.balance_label.setObjectName("balance_label")
        balance_layout.addWidget(self.balance_label)
        
        # 상태 라벨
        self.status_label = QLabel("돈을 투입해주세요.")
        balance_layout.addWidget(self.status_label)

        # 레이아웃에 추가
        self.setLayout(balance_layout)

    # 잔액 및 상태 업데이트 함수
    def update_balance(self, amount, msg):
        self.balance_label.setText(f"잔액: {amount}원")
        self.status_label.setText(msg)

# 돈 투입 및 관리자 모드 프레임
class MoneyInputFrame(QFrame):
    def __init__(self, money_list, on_click_money, on_click_refund, on_click_admin):
        super().__init__()
        self.init_ui(money_list, on_click_money, on_click_refund, on_click_admin)
        self.setStyleSheet(style.MONEY_INPUT_FRAME)
        
    def init_ui(self, money_list, on_click_money, on_click_refund, on_click_admin):
        money_input_layout = QVBoxLayout()
        money_grid = self.init_money_grid(money_list, on_click_money, on_click_refund, on_click_admin)
        money_input_layout.addLayout(money_grid)
        self.setLayout(money_input_layout)

    # 돈 투입 그리드 초기화
    def init_money_grid(self, money_list, on_click_money, on_click_refund, on_click_admin):
        grid = QGridLayout()
        # 돈 리스트를 순회하며 그리드에 추가
        for index, money in enumerate(money_list):
            row = index // 2
            col = index % 2
            new_btn = QPushButton(f"{money.name}원")
            new_btn.clicked.connect(on_click_money)
            grid.addWidget(new_btn, row, col)

        # 잔돈 반환 버튼 추가
        refund_button = QPushButton("잔돈 반환")
        refund_button.clicked.connect(on_click_refund)
        grid.addWidget(refund_button, 2, 1)

        # 관리자 모드 버튼 추가
        admin_button = QPushButton("관리자 모드")
        admin_button.clicked.connect(on_click_admin)
        grid.addWidget(admin_button, 3, 0, 1, 2)  # 2칸 병합
        return grid

class DrinkFrame(QFrame):
    def __init__(self, drinks_list, on_click_drink):
        super().__init__()
        self.setStyleSheet(style.DRINK_FRAME)
        self.buttons = {}  # {drink_id: QPushButton}
        self.init_ui(drinks_list, on_click_drink)

    def init_ui(self, drinks_list, on_click_drink):
        drink_layout = QVBoxLayout()
        drink_grid = self.init_drinks(drinks_list, on_click_drink)
        drink_layout.addLayout(drink_grid)
        self.setLayout(drink_layout)

    # 음료 그리드 초기화
    def init_drinks(self, drinks_list, on_click_drink):
        grid = QGridLayout()
        # 음료 리스트를 순회하며 그리드에 추가
        for index, drink in enumerate(drinks_list):
            row = index // 4
            col = index % 4
            new_btn = QPushButton(f"{drink.name}\n{drink.price}원")
            new_btn.setObjectName("drink_button")
            new_btn.clicked.connect(on_click_drink)
            self.buttons[drink.id] = new_btn  # id 기준으로 저장 (이름 변경에도 조회 가능)
            grid.addWidget(new_btn, row, col)
        return grid

    # 투입 금액에 따라 음료 버튼 상태 및 텍스트 업데이트
    def refresh(self, drinks_list, input_money=0):
        for drink in drinks_list:
            btn = self.buttons.get(drink.id)
            if btn:
                btn.setText(f"{drink.name}\n{drink.price}원")  # 이름·가격 변경 반영
                if not drink.is_available:
                    status = "empty"          # 품절
                elif input_money >= drink.price:
                    status = "ok"             # 구매 가능
                else:
                    status = "unaffordable"   # 잔액 부족
                btn.setEnabled(status != "empty")
                btn.setProperty("status", status)
                btn.style().unpolish(btn)
                btn.style().polish(btn)


class MessageLogFrame(QFrame):
    """서버 push 메시지 최근 3개를 표시하는 로그 프레임."""
    MAX = 3

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#0a0a1a; border-top: 1px solid #333;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(2)
        title = QLabel("서버 알림")
        title.setStyleSheet("color:#888; font-size:10px;")
        layout.addWidget(title)
        self.labels = [QLabel("") for _ in range(self.MAX)]
        for lbl in self.labels:
            lbl.setStyleSheet("color:#aaa; font-size:11px;")
            layout.addWidget(lbl)

    def update_log(self, messages: list):
        for i, lbl in enumerate(self.labels):
            lbl.setText(messages[i] if i < len(messages) else "")