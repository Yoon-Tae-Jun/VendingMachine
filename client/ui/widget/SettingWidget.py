from PyQt6.QtWidgets import QVBoxLayout, QWidget, QFrame, QScrollArea, QMessageBox
from PyQt6.QtCore import Qt
from ui.frame.SettingFrame import SettingTitle, SettingSaveBtn, SettingRow, SettingLine, PasswordSection, DrinkEditSection
import ui.styles as style

class SettingWidget(QWidget):
    def __init__(self, vending_machine, on_threshold_change):
        super().__init__()
        self.vending_machine = vending_machine
        self.money_manager = self.vending_machine.money_manager
        self.on_threshold_change = on_threshold_change

        self.setting_data = [
            {
                "title": "재고 경고 기준 (개)",
                "spin_name": "threshold_spin",
                "value": self.vending_machine.low_stock_threshold,
                "min_val": 1,
                "max_val": 99
            },
            {
                "title": "음료 최대 수량 (개)",
                "spin_name": "max_spin",
                "value": self.vending_machine.max_stock,
                "min_val": 1,
                "max_val": 999
            },
            {
                "title": "시재 최소 잔류 수량 (개)",
                "spin_name": "reserve_spin",
                "value": self.money_manager.min_money_reserve,
                "min_val": 0,
                "max_val": 99
            },
        ]
        self.init_ui()

    def init_ui(self):
        # 화면 설정
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # 스크롤 영역 설정
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(style.SETTING_SCROLL)

        # 콘텐츠 영역 설정
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 설정 영역
        layout.addWidget(SettingTitle("설정"))
        # 설정 행 추가
        for info in self.setting_data:
            row = SettingRow(info)
            setattr(self, info["spin_name"], getattr(row, info["spin_name"]))
            layout.addWidget(row)
        layout.addWidget(SettingSaveBtn(self.save)) # 설정 저장 버튼
        layout.addWidget(SettingLine()) # 구분선

        # 비밀번호 변경 섹션
        self.password_section = PasswordSection()
        layout.addWidget(self.password_section)
        layout.addWidget(SettingLine()) # 구분선

        # 음료 이름/가격 변경 섹션
        self.drink_edit_section = DrinkEditSection(
            self.vending_machine.get_drinks(),
            self.vending_machine.update_drink
        )
        layout.addWidget(self.drink_edit_section)
        layout.addStretch()

        # 레이아웃에 추가
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    # 설정 저장 함수
    def save(self):
        try:
            self.vending_machine.set_low_stock_threshold(self.threshold_spin.value())
            self.vending_machine.set_max_stock(self.max_spin.value())
            self.money_manager.set_min_money_reserve(self.reserve_spin.value())
            self.on_threshold_change()
        except Exception as e:
            QMessageBox.warning(self, "저장 오류", f"설정 저장 중 오류가 발생했습니다.\n{e}")


    # 관리자 모드 진입 시 폼 초기화
    def refresh(self):
        self.password_section.refresh()
        self.drink_edit_section.refresh()

    

