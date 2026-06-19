from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PyQt6.QtCore import Qt, QDate
import ui.styles as style

import matplotlib
import matplotlib.ticker
import platform
matplotlib.rcParams['font.family'] = 'AppleGothic' if platform.system() == 'Darwin' else 'Malgun Gothic' # 윈도우, mac 폰트 설정
matplotlib.rcParams['axes.unicode_minus'] = False
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

###### 매출 관리 화면 관련 프레임 ######
# 시각화 관련 클래스
class VisualizationManager:
    # Figure/Axes를 받아 캔버스 반환
    def make_canvas(self, fig, ax, max_height=None) -> FigureCanvasQTAgg:
        # fig, axes 배경 투명 설정정
        fig.patch.set_facecolor('none')
        ax.patch.set_facecolor('none')

        canvas = FigureCanvasQTAgg(fig) # fig -> Qt 변환
        canvas.setStyleSheet(style.CANVAS_STYLE)
        canvas.wheelEvent = lambda event: event.ignore()  # 스크롤 방지
        if max_height:
            canvas.setMaximumHeight(max_height) # 최대 높이 제한
        return canvas

    # 주간 일별 매출 막대 차트 생성
    def create_weekly_bar_chart(self, chart_data: dict, week) -> FigureCanvasQTAgg:
        fig = Figure(figsize=(5, 3), layout='constrained')
        ax = fig.add_subplot(111)

        # 데이터 변환
        labels = [d[5:] for d in chart_data] # YYYY-MM-DD → MM-DD
        revenues = list(chart_data.values())

        # 차트 생성
        bars = ax.bar(labels, revenues, color="#2D89EC66", width=0.6)  # 막대 차트 생성
        ax.set_xlabel("날짜", color="white")
        ax.set_ylabel("매출 (원)", color="white")
        ax.set_title(f"{week}주차 매출", color="white")
        ax.tick_params(colors="white")
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{int(x):,}")) # Y축 천 단위 콤

        # 차트 테두리 색상 변경
        for spine in ax.spines.values():
            spine.set_edgecolor("white")

        # 레이블 표시 공간 확보
        if max(revenues) > 0:
            ax.set_ylim(top=max(revenues) * 1.25)

        # 매출이 있는 막대 레이블 표시
        for bar, revenue in zip(bars, revenues):
            if revenue > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        f"{revenue:,}원", ha="center", va="bottom", fontsize=8, color="white")

        return self.make_canvas(fig, ax, max_height=250)

    # 음료별 매출 비중 도넛 차트 생성
    def create_drink_doughnut_chart(self, drinks: dict) -> FigureCanvasQTAgg:
        fig = Figure(figsize=(4, 3), layout='constrained')
        ax = fig.add_subplot(111)

        # 데이터 변환환
        names = list(drinks.keys())
        revenues = [drinks[n]["revenue"] for n in names]

        # 매출 데이터 없는 경우
        if sum(revenues) == 0:
            ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center", color="white")
        # 매출 데이터 있는 경우
        else:
            total = sum(revenues)
            # 도넛 차트 생성
            wedges, *_ = ax.pie(revenues, wedgeprops=dict(width=0.3))
            # 범례 생성
            legend = ax.legend(
                wedges, [f"{n}  {r / total * 100:.1f}%" for n, r in zip(names, revenues)],
                loc="center left", bbox_to_anchor=(1, 0.5), fontsize=7, frameon=False,
            )
            # 범례 텍스트 색상 설정정
            for text in legend.get_texts():
                text.set_color("white")

        # 도넛 중앙 텍스트
        ax.text(0, 0, "음료별 비중", ha="center", va="center", color="white", fontsize=8)

        return self.make_canvas(fig, ax)

# 날짜 지정 프레임
class DateSelectorFrame(QFrame):
    def __init__(self, update_sales):
        super().__init__()
        self.setStyleSheet(style.DATE_SELECTOR_FRAME)
        self.update_sales = update_sales
        self.init_ui()

    def init_ui(self):
        #화면 설정
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 날짜 선택 위젯
        self.date_edit = QDateEdit()
        self.date_edit.setFixedWidth(100)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")

        # 날짜 조회 버튼
        select_btn = QPushButton("조회")
        select_btn.setFixedWidth(50)
        select_btn.clicked.connect(self.update_sales)

        #레이아웃에 추가
        layout.addWidget(self.date_edit)
        layout.addWidget(select_btn)
        layout.addStretch()
        self.setLayout(layout)

    def get_date(self) -> str:
        return self.date_edit.date().toString("yyyy-MM-dd")

    def get_day(self) -> int:
        return self.date_edit.date().day()

# 음료 매출 카드
class SalesCard(QLabel):
    def __init__(self, title, amount):
        super().__init__()
        self.setStyleSheet(style.SALES_CARD)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(230, 60)
        self.setText(f"{title}\n{amount:,}원")

# 음료 별 매출 테이블
class DrinkSalesTable(QTableWidget):
    def __init__(self, drinks: dict):
        super().__init__(len(drinks), 3)
        self.setStyleSheet(style.TABLE_CONTENT)
        self.horizontalHeader().setStyleSheet(style.TABLE_HEADER)

        self.config_table()
        self.init_ui(drinks)

    # 테이블 설정 함수 #
    def config_table(self):
        # 헤더 설정 및 스타일 적용
        self.setHorizontalHeaderLabels(["음료명", "판매 수량", "매출액"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # 컬럼 너비 균등 분배
        self.verticalHeader().setVisible(False)  # 행 번호 숨김
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # 셀 편집 금지

        # 스크롤바 제거
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    # 테이블 초기화 및 데이터 입력 #
    def init_ui(self, drinks):
        # 행 추가
        for row, (name, stat) in enumerate(drinks.items()):
            self.setItem(row, 0, QTableWidgetItem(name))  # 음료명
            self.setItem(row, 1, QTableWidgetItem(str(stat["count"])))  # 판매 수량
            self.setItem(row, 2, QTableWidgetItem(f"{stat['revenue']:,}원"))  # 매출액

        # 테이블 높이 계산 및 고정
        total_height = self.horizontalHeader().height() + sum(
            self.rowHeight(i) for i in range(self.rowCount())
        ) + 4
        self.setFixedHeight(total_height)

# 전체 매출 테이블
class SaleLogTable(QTableWidget):
    def __init__(self):
        super().__init__(0, 3)
        self.setStyleSheet(style.TABLE_CONTENT)
        self.horizontalHeader().setStyleSheet(style.TABLE_HEADER)
        self.config_table()

    # 테이블 설정
    def config_table(self):
        self.setHorizontalHeaderLabels(["날짜", "음료명", "금액"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumHeight(185)
        self.setMaximumHeight(300)

    # 테이블 데이터 업데이트
    def update_log(self, records):
        self.setRowCount(len(records))
        for row, r in enumerate(records):
            date_item = QTableWidgetItem(r.date)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item = QTableWidgetItem(r.drink_name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            price_item = QTableWidgetItem(f"{r.price:,}원")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 0, date_item)
            self.setItem(row, 1, name_item)
            self.setItem(row, 2, price_item)
