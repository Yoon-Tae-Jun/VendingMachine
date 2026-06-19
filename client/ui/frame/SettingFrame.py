from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QLineEdit
)
from PyQt6.QtCore import Qt
import ui.styles as style
from utils.util import PasswordManager

###### 설정 화면 관련 프레임 ######
# 설정 소제목
class SettingTitle(QLabel):
    def __init__(self, title):
        super().__init__(title)
        self.setStyleSheet(style.SETTING_TITLE)

# 설정 저장 버튼
class SettingSaveBtn(QPushButton):
    def __init__(self, click_event):
        super().__init__("저장")
        self.setFixedHeight(32)
        self.setStyleSheet(style.SETTING_SAVE_BTN)
        self.clicked.connect(click_event)

# 설정 행
class SettingRow(QFrame):
    def __init__(self, row_info):
        super().__init__()
        self.row_info = row_info
        self.init_ui(row_info)

    def init_ui(self, row_info):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(row_info["title"])
        label.setStyleSheet(style.SETTING_ROW_LABEL)

        spin = QSpinBox()
        spin.setRange(row_info["min_val"], row_info["max_val"])
        spin.setValue(row_info["value"])
        spin.setFixedWidth(80)
        spin.setStyleSheet(style.STOCK_SPINBOX)
        setattr(self, row_info["spin_name"], spin)

        #레이아웃에 추가
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(spin)

        self.setLayout(layout)

# 설정 구분선
class SettingLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setStyleSheet(style.SETTING_LINE)

# 비밀번호 변경 영역
class PasswordSection(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(style.PASSWORD_SECTION)
        self.row_data = [
            {
                "title": "현재 비밀번호",
                "attr": "current_pw_input"
            },
            {
                "title": "새 비밀번호",
                "attr": "new_pw_input"
            },
            {
                "title": "새 비밀번호 확인",
                "attr": "confirm_pw_input"
            }
        ]
        self.pw_manager = PasswordManager()
        self.input_fields = []

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 제목
        layout.addWidget(SettingTitle("비밀번호 변경"))

        # 비밀번호 섹션 행 추가
        for row in self.row_data:
            row_layout, field = self.init_pw_row(row["title"], row["attr"])
            layout.addLayout(row_layout)
            self.input_fields.append(field)

        # 상태 메시지
        self.pw_msg_label = QLabel("")
        self.pw_msg_label.setObjectName("status")
        layout.addWidget(self.pw_msg_label)

        # 저장 버튼
        layout.addWidget(SettingSaveBtn(self.change_password))

    def init_pw_row(self, label_text: str, attr_name: str):
        # 행 설정
        row = QHBoxLayout()
        row.setSpacing(8)

        # 라벨
        label = QLabel(label_text)
        label.setObjectName("row_label")
        label.setFixedWidth(110)

        # 입력 창
        field = QLineEdit()
        field.setEchoMode(QLineEdit.EchoMode.Password)
        field.setFixedHeight(28)
        setattr(self, attr_name, field)

        #행에 추가
        row.addWidget(label)
        row.addWidget(field)
        return row, field

    def change_password(self):
        current = self.input_fields[0].text()
        new_pw  = self.input_fields[1].text()
        confirm = self.input_fields[2].text()

        # 비밀번호 검증
        result = self.pw_manager.validation(current, new_pw, confirm)

        # 비밀번호 검증 성공 시
        if result["status"]:
            self.pw_manager.change(new_pw)
            self.set_pw_msg("비밀번호가 변경되었습니다.", error=False)
            self.current_pw_input.clear()
            self.new_pw_input.clear()
            self.confirm_pw_input.clear()
        # 비밀번호 검증 실패 시
        else:
            self.set_pw_msg(result["msg"], error=True)

    # 비밀번호 메시지 라벨 업데이트
    def set_pw_msg(self, msg: str, error: bool):
        if error:
            self.pw_msg_label.setProperty("status", "error")
        else:
            self.pw_msg_label.setProperty("status", "ok")
        self.pw_msg_label.setText(msg)

    # 비밀번호 폼 초기화
    def refresh(self):
        for field in self.input_fields:
            field.clear()
        self.pw_msg_label.setText("")


###### 음료 설정 관련 프레임 ######
# 음료 설정 행 (이름 입력 + 가격 스핀박스 + 저장 버튼)
class DrinkEditRow(QFrame):
    def __init__(self, drink, on_save):
        super().__init__()
        self.drink = drink
        self.on_save = on_save
        self.setStyleSheet(style.STOCK_ROW)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # 이름 입력 필드
        self.name_input = QLineEdit(self.drink.name)
        self.name_input.setFixedHeight(28)
        self.name_input.setStyleSheet(style.DRINK_EDIT_INPUT)

        # 가격 스핀박스
        self.price_spin = QSpinBox()
        self.price_spin.setRange(10, 99999)
        self.price_spin.setSingleStep(10)
        self.price_spin.setValue(self.drink.price)
        self.price_spin.setFixedWidth(100)
        self.price_spin.setFixedHeight(28)
        self.price_spin.setStyleSheet(style.STOCK_SPINBOX)
        self.price_spin.setSuffix("원")

        # 저장 버튼
        save_btn = QPushButton("저장")
        save_btn.setFixedSize(52, 28)
        save_btn.setStyleSheet(style.STOCK_RESTOCK_BTN)
        save_btn.clicked.connect(self.on_click_save)

        layout.addWidget(self.name_input, 1)
        layout.addWidget(self.price_spin)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def on_click_save(self):
        self.on_save(self.drink.id, self.name_input.text().strip(), self.price_spin.value())

    # 음료 데이터가 외부에서 변경됐을 때 입력 필드 동기화
    def refresh(self):
        self.name_input.setText(self.drink.name)
        self.price_spin.setValue(self.drink.price)


# 음료 설정 섹션 (전체 음료 목록)
class DrinkEditSection(QWidget):
    def __init__(self, drinks, on_save):
        super().__init__()
        self.setStyleSheet(style.DRINK_EDIT_SECTION)
        self.on_save = on_save
        self.rows = []
        self.init_ui(drinks)

    def init_ui(self, drinks):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        layout.addWidget(SettingTitle("음료 설정"))

        for drink in drinks:
            row = DrinkEditRow(drink, self.on_row_save)
            self.rows.append(row)
            layout.addWidget(row)

        # 저장 결과 메시지
        self.msg_label = QLabel("")
        self.msg_label.setObjectName("status")
        layout.addWidget(self.msg_label)

    def on_row_save(self, drink_id, name, price):
        if not name:
            self.set_msg("음료 이름을 입력해주세요.", error=True)
            return
        try:
            self.on_save(drink_id, name, price)
            self.set_msg("저장되었습니다.", error=False)
        except Exception as e:
            self.set_msg(f"저장 실패: {e}", error=True)

    def set_msg(self, msg, error):
        self.msg_label.setProperty("status", "error" if error else "ok")
        self.msg_label.style().unpolish(self.msg_label)
        self.msg_label.style().polish(self.msg_label)
        self.msg_label.setText(msg)

    # 관리자 모드 진입 시 입력 필드·메시지 초기화
    def refresh(self):
        for row in self.rows:
            row.refresh()
        self.msg_label.setText("")
