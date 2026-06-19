from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout
import ui.frame.AdminFrame as admin_frame
from ui.widget.SalesWidget import SalesWidget
from ui.widget.StockWidget import StockWidget
from ui.widget.MoneyWidget import MoneyWidget
from ui.widget.SettingWidget import SettingWidget

class AdminWidget(QWidget):
    def __init__(self, vending_machine, sales_manager, exit_admin):
        super().__init__()
        self.vending_machine = vending_machine
        self.sales_manager = sales_manager
        self.exit_admin = exit_admin

        self.init_admin_ui()

    def init_admin_ui(self):
        # 화면 설정
        self.setFixedHeight(400)
        self.admin_layout = QVBoxLayout()
        self.setLayout(self.admin_layout)
    
        # 관리자 화면 상단(제목)
        top_layout = QHBoxLayout()
        top_layout.addWidget(admin_frame.TitleFrame())

        # 관리자 화면 하단(메뉴, 콘텐츠)
        bottom_layout = QHBoxLayout()
        content_stack = self.init_content_stack()
        menu_frame = admin_frame.MenuFrame(content_stack, self.exit_admin)
        bottom_layout.addWidget(menu_frame)
        bottom_layout.addWidget(content_stack)

        # 상하단 레이아웃 메인 레이아웃에 추가 
        self.admin_layout.addLayout(top_layout)
        self.admin_layout.addLayout(bottom_layout)

    # 스택 위젯 생성 및 초기화
    def init_content_stack(self):
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(StockWidget(self.vending_machine))
        self.content_stack.addWidget(SalesWidget(self.sales_manager))
        self.content_stack.addWidget(MoneyWidget(self.vending_machine))
        self.content_stack.addWidget(SettingWidget(self.vending_machine, self.refresh_all))
        return self.content_stack

    # 판매 화면 -> 관리자 화면 이동 시 화면 업데이트
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_all()

    # 각 메뉴 위젯 화면 업데이트 함수(설정 변경 후 호출)   
    def refresh_all(self):
        for i in range(self.content_stack.count()):
            widget = self.content_stack.widget(i)
            if hasattr(widget, 'refresh'):
                widget.refresh()
    
