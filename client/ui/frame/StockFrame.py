from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSpinBox
from PyQt6.QtCore import Qt
import ui.styles as style
from network.driver import send_stock

###### 재고 관리 화면 관련 프레임 ######
# 재고 관리 행
class StockRow(QFrame):
    def __init__(self, drink, vending_machine, on_restock):
        super().__init__()
        self.drink = drink
        self.vending_machine = vending_machine
        self.on_restock = on_restock
        self.setStyleSheet(style.STOCK_ROW)
        self.init_ui()

    def init_ui(self):
        # 화면 설정
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # 재고 이름 라벨
        self.name_label = QLabel(self.drink.name)
        self.name_label.setStyleSheet(style.STOCK_NAME_LABEL)
        self.name_label.setFixedWidth(100)

        # 재고 상태 뱃지
        self.badge = QLabel()
        self.badge.setObjectName("stock_badge")
        self.badge.setFixedSize(60, 26)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge.setStyleSheet(style.STOCK_BADGE)

        # 재고 수량 조절 박스
        self.spinbox = QSpinBox()
        self.spinbox.setRange(1, 100)
        self.spinbox.setValue(1)
        self.spinbox.setFixedWidth(70)
        self.spinbox.setStyleSheet(style.STOCK_SPINBOX)
        self.update_badge()

        # 재고 보충 버튼
        btn = QPushButton("보충")
        btn.setFixedSize(60, 30)
        btn.setStyleSheet(style.STOCK_RESTOCK_BTN)
        btn.clicked.connect(self.on_click_restock)

        # 레이아웃에 추가
        layout.addWidget(self.name_label)
        layout.addStretch()
        layout.addWidget(self.badge)
        layout.addWidget(self.spinbox)
        layout.addWidget(btn)
        self.setLayout(layout)

    # 재고 상태 뱃지 업데이트
    def update_badge(self):
        count = self.drink.count
        threshold = self.vending_machine.low_stock_threshold
        max_stock = self.vending_machine.max_stock
        if count == 0:
            self.badge.setText("품절")
            self.badge.setProperty("status", "empty")
        elif count <= threshold:
            self.badge.setText(f"{count}개")
            self.badge.setProperty("status", "warning")
        else:
            self.badge.setText(f"{count}개")
            self.badge.setProperty("status", "ok")
        self.badge.style().unpolish(self.badge)
        self.badge.style().polish(self.badge)

        # 보충 가능 수량 = 최대 - 현재 (최소 0)
        self.spinbox.setMaximum(max(0, max_stock - count))
        self.spinbox.setEnabled(count < max_stock)

    # 음료 이름 라벨 갱신 (음료 설정에서 이름 변경 시 호출)
    def refresh_name(self):
        self.name_label.setText(self.drink.name)

    # 재고 보충 버튼 이벤트
    def on_click_restock(self):
        max_stock = self.vending_machine.max_stock
        self.drink.count = min(self.drink.count + self.spinbox.value(), max_stock)
        self.drink.is_available = True
        self.update_badge()
        self.on_restock()
        send_stock(self.drink.id, self.drink.name, self.drink.count)
