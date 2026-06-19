from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSpinBox
from PyQt6.QtCore import Qt
import ui.styles as style

###### 시재 관리 화면 관련 프레임 ######
# 합계 행
class TotalRow(QFrame):
    def __init__(self, update_total):
        super().__init__()
        self.update_total = update_total
        self.setStyleSheet(style.MONEY_TOTAL_ROW)

        self.init_ui()

    def init_ui(self):
        #화면 설정
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        # 합계 행 제목
        label = QLabel("합계")
        layout.addWidget(label)
        layout.addStretch()

        # 합계 금액
        self.total_label = QLabel()
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.total_label)

        # 레이아웃에 추가
        self.setLayout(layout)
        self.total_label.setText("0원")

    # 총합 금액 setter
    def set_total(self, amount: int):
        self.total_label.setText(f"{amount:,}원")

# 시재 행
class MoneyRow(QFrame):
    def __init__(self, money_dto, on_refill):
        super().__init__()
        self.money_dto = money_dto
        self.on_refill = on_refill
        self.setStyleSheet(style.STOCK_ROW)
        self.init_ui()

    def init_ui(self):
        # 화면 설정
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # 권종 이름 라벨
        name_label = QLabel(f"{int(self.money_dto.name):,}원")
        name_label.setStyleSheet(style.STOCK_NAME_LABEL)
        name_label.setFixedWidth(80)

        self.init_badge() # 수량 뱃지 초기화

        # 금액 라벨 (권종 * 수량)
        self.value_label = QLabel()
        self.value_label.setStyleSheet(style.MONEY_VALUE_LABEL)
        self.value_label.setFixedWidth(90)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # 충전 수량 조절 박스
        self.spinbox = QSpinBox()
        self.spinbox.setRange(1, 100)
        self.spinbox.setValue(1)
        self.spinbox.setFixedWidth(70)
        self.spinbox.setStyleSheet(style.STOCK_SPINBOX)

        # 보충 버튼
        refill_btn = QPushButton("보충")
        refill_btn.setFixedSize(60, 30)
        refill_btn.setStyleSheet(style.STOCK_RESTOCK_BTN)
        refill_btn.clicked.connect(self.on_click_refill)

        # 레이아웃에 추가
        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(self.count_badge)
        layout.addWidget(self.value_label)
        layout.addWidget(self.spinbox)
        layout.addWidget(refill_btn)
        self.setLayout(layout)

        self.refresh()

    # 수량 뱃지 초기화
    def init_badge(self):
        self.count_badge = QLabel()
        self.count_badge.setFixedSize(55, 26)
        self.count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_badge.setStyleSheet(style.MONEY_BADGE)

    # 수량 및 금액 라벨 업데이트
    def refresh(self):
        count = self.money_dto.count
        value = int(self.money_dto.name) * count
        self.count_badge.setText(f"{count}개")
        self.value_label.setText(f"{value:,}원")

    # 보충 버튼 이벤트
    def on_click_refill(self):
        self.on_refill(self.money_dto.name, self.spinbox.value())
        self.refresh()
