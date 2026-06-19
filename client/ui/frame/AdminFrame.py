from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDialog, QLineEdit, QFrame, QWidget, QScrollArea,
)
import ui.styles as style
from utils.util import PasswordManager

# 비밀번호 확인 다이얼로그
class AdminPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(style.PASSWORD_INPUT)

        self.pw_manager = PasswordManager()

        self._init_ui()

    def _init_ui(self):
        # 화면 설정
        self.setWindowTitle("관리자 인증")
        self.setFixedSize(300, 160)
        layout = QVBoxLayout()

        # 비밀번호 입력 필드
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("비밀번호를 입력하세요")
        self.password_input.returnPressed.connect(self.on_confirm)

        # 오류 메시지 라벨
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e74c3c; font-size: 11px;")

        # 비밀번호 확인 버튼
        confirm_btn = QPushButton("확인")
        confirm_btn.clicked.connect(self.on_confirm)

        # 레이아웃에 추가
        layout.addWidget(QLabel("관리자 비밀번호"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.error_label)
        layout.addWidget(confirm_btn)
        self.setLayout(layout)

    # 비밀번호 검증 후 일치하면 다이얼로그 닫기
    def on_confirm(self):
        if self.pw_manager.verify(self.password_input.text()):
            self.accept()
        else:
            self.error_label.setText("비밀번호가 올바르지 않습니다.")
            self.password_input.clear()

    def get_password(self):
        return self.password_input.text()

# 스크롤 리스트 프레임(시재, 재고 관리 공통)
class ScrollListFrame(QWidget):
    """제목 + 스크롤 가능한 행 목록 공통 프레임"""

    def __init__(self, title):
        super().__init__()
        self.rows = []
        self.init_ui(title)

    def init_ui(self, title):
        # 화면 설정
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 스크롤 영역 설정
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(style.SCROLL_AREA)

        # 콘텐츠 영역 설정
        self._content = QWidget()
        self.content_layout = QVBoxLayout(self._content)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(6)

        # 제목 라벨
        title_label = QLabel(title)
        title_label.setStyleSheet(style.STOCK_TITLE)
        self.content_layout.addWidget(title_label)

        # 레이아웃에 추가
        self._scroll.setWidget(self._content)
        layout.addWidget(self._scroll)
        self.setLayout(layout)

    # 행 추가
    def add_row(self, row):
        self.rows.append(row)
        self.content_layout.addWidget(row)

    # 하단 위젯 추가 (합계행, 버튼 등)
    def add_footer(self, widget):
        self.content_layout.addWidget(widget)

    # 마지막에 호출해 stretch 추가
    def finalize(self):
        self.content_layout.addStretch()

# 관리자 제목 프레임
class TitleFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(style.ADMIN_TITLE)
        self.init_ui()

    def init_ui(self):
        title_layout = QHBoxLayout()

        # 제목 라벨
        title_label = QLabel("관리자 모드")
        title_layout.addWidget(title_label)

        self.setLayout(title_layout)

# 관리자 메뉴 프레임
class MenuFrame(QFrame):
    def __init__(self, content_stack, exit_admin):
        super().__init__()
        self.setStyleSheet(style.ADMIN_MENU_FRAME)
        self.content_stack = content_stack
        self.exit_admin = exit_admin

        # 메뉴 이름 및 인덱스 리스트
        self.MENUS = [
            ("재고 관리", 0),
            ("매출 관리", 1),
            ("시재 관리", 2),
            ("설정", 3)
        ]
        # 메뉴 버튼 리스트
        self.buttons = []
        self.init_ui()

    def init_ui(self):
        # 화면 설정
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(3)
        menu_layout.setContentsMargins(0, 0, 0, 0)

        # 메뉴 버튼 생성 및 이벤트 연결
        for menu_name, index in self.MENUS:
            btn = QPushButton(menu_name)
            btn.setObjectName("menu_button")
            btn.clicked.connect(lambda _, idx=index: self.on_click_menu(idx))

            #  첫 번째 메뉴 버튼을 활성화 상태로 설정
            if index == 0:
                btn.setProperty("active", True)
            else:
                btn.setProperty("active", False)

            menu_layout.addWidget(btn)
            self.buttons.append(btn)
        menu_layout.addStretch()

        # 종료 버튼
        exit_btn = QPushButton("관리자 모드 종료")
        exit_btn.setObjectName("exit_button")
        exit_btn.clicked.connect(self.exit_admin)

        # 레이아웃에 추가
        menu_layout.addWidget(exit_btn)
        self.setLayout(menu_layout)

    # 메뉴 버튼 클릭 이벤트
    def on_click_menu(self, index):
        self.content_stack.setCurrentIndex(index)
        self.set_active_button(index)

    # 활성화된 메뉴 버튼 스타일 업데이트 함수
    def set_active_button(self, index):
        for i, btn in enumerate(self.buttons):
            if i == index:
                btn.setProperty("active", True)
            else:
                btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
