from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel
)

import ui.styles as style
from ui.frame.SalesFrame import DateSelectorFrame, SalesCard, DrinkSalesTable, SaleLogTable, VisualizationManager
from datetime import datetime

class SalesWidget(QWidget):
    def __init__(self, sales_manager):
        super().__init__()
        self.sales_manager = sales_manager
        self.vm = VisualizationManager()
        self.init_ui()

    def init_ui(self):
        # 화면 설정
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # 스크롤 영역 초기화
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(style.SCROLL_AREA)

        # 컨텐츠 영역 초기화
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(8, 2, 8, 8)
        self.content_layout.setSpacing(10)

        # 위젯 초기화
        self.init_selector()
        self.init_cards()
        self.init_chart()
        self.init_bottom()
        self.init_log()
        self.content_layout.addStretch()

        # 매출 초기화
        self.update_sales()

        # 레이아웃에 추가
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)
        self.setLayout(outer_layout)

    # 날짜 위젯 초기화
    def init_selector(self):
        self.date_selector = DateSelectorFrame(self.update_sales)
        self.content_layout.addWidget(self.date_selector)

    # 매출 카드 초기화
    def init_cards(self):
        # 카드 초기화
        self.daily_card   = SalesCard("", 0)
        self.weekly_card  = SalesCard("", 0)
        self.monthly_card = SalesCard("", 0)

        # 레이아웃에 추가
        cards_row = QHBoxLayout()
        cards_row.addWidget(self.daily_card)
        cards_row.addWidget(self.weekly_card)
        cards_row.addWidget(self.monthly_card)
        self.content_layout.addLayout(cards_row)

    # 주매출 차트 초기화
    def init_chart(self):
        # 차트 화면 설정
        self.chart_container = QWidget()
        self.chart_container.setMinimumHeight(230)
        self.chart_inner = QVBoxLayout(self.chart_container)
        self.chart_inner.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.chart_container)

    # 음료별 매출 테이블, 도넛 차트 초기화
    def init_bottom(self):
        self.bottom_row = QHBoxLayout()
        self.content_layout.addLayout(self.bottom_row)
        self.update_bottom()

    # 전체 매출 로그 테이블 초기화
    def init_log(self):
        # 매출 로그 제목
        title = QLabel("전체 매출 로그")
        title.setStyleSheet(style.STOCK_TITLE)
        self.content_layout.addWidget(title)

        # 매출 로그 테이블
        self.log_table = SaleLogTable()
        self.content_layout.addWidget(self.log_table)

    # 음료별 매출 테이블, 도넛 차트 업데이트
    def update_bottom(self):
        # 기존 위젯 제거
        while self.bottom_row.count():
            item = self.bottom_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 전체 매출 기반 테이블, 도넛 차트 생성
        total = self.sales_manager.get_total_sales()
        self.bottom_row.addWidget(DrinkSalesTable(total["drinks"]), stretch=3)
        self.bottom_row.addWidget(self.vm.create_drink_doughnut_chart(total["drinks"]), stretch=3)

    # 전체 매출 로그 테이블 업데이트
    def update_log(self):
        records = list(reversed(self.sales_manager.load()))
        self.log_table.update_log(records)
        
    # 주매출 차트 업데이트
    def update_chart(self, date: str):
        while self.chart_inner.count():
            item = self.chart_inner.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        chart_data = self.sales_manager.get_weekly_chart_by_date(date)
        self.chart_inner.addWidget(self.vm.create_weekly_bar_chart(chart_data, self.get_week(date)))

    # 매출 관리 위젯 업데이트
    def update_sales(self):
        date = self.date_selector.get_date()
        day  = self.date_selector.get_day()
        week  = self.get_week(date)
        month = datetime.fromisoformat(date).month

        # 매출 데이터 조회
        daily   = self.sales_manager.get_sales_by_date(date)
        weekly  = self.sales_manager.get_weekly_sales_by_date(date)
        monthly = self.sales_manager.get_monthly_sales_by_date(date)

        # 매출 데이터 업데이트
        self.daily_card.setText(f"{month}.{day} 매출\n{daily['total_revenue']:,}원")
        self.weekly_card.setText(f"{month}-{week} 주차 매출\n{weekly['total_revenue']:,}원")
        self.monthly_card.setText(f"{month}월 매출\n{monthly['total_revenue']:,}원")
        self.update_chart(date)
        self.update_log()
        self.update_bottom()

    # 화면 업데이트
    def refresh(self):
        self.update_sales()

    # 주 계산
    def get_week(self, date: str) -> int:
        d = datetime.strptime(date, "%Y-%m-%d")
        return (d.day - 1) // 7 + 1