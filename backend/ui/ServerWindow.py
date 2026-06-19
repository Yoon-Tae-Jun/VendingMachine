"""서버 관리자 PyQt6 데스크탑 GUI."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QDateEdit, QComboBox, QLineEdit, QSpinBox,
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QColor, QFont

from ui import styles


def make_table(headers: list) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    return t


def cell(text: str, align=Qt.AlignmentFlag.AlignCenter) -> QTableWidgetItem:
    item = QTableWidgetItem(str(text))
    item.setTextAlignment(align)
    return item


# ── 머신 상태 바 ─────────────────────────────────────────
class MachineStatusBar(QFrame):
    def __init__(self, server):
        super().__init__()
        self.server  = server
        self.machine_labels = {}
        self.peer_labels    = {}
        self.setFixedHeight(42)
        self.setStyleSheet(styles.STATUS_BAR_FRAME)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)
        layout.setSpacing(16)

        layout.addWidget(QLabel("머신:"))
        for mid in range(1, 5):
            lbl = QLabel(f"M{mid}")
            lbl.setFixedWidth(48)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(styles.STATUS_LABEL_DEFAULT)
            self.machine_labels[mid] = lbl
            layout.addWidget(lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(styles.STATUS_SEPARATOR)
        layout.addWidget(sep)

        layout.addWidget(QLabel("피어 서버:"))
        port_names = {9000: "Server1", 9001: "Server2", 9002: "Backup"}
        for (host, port) in server.peers:
            lbl = QLabel(port_names.get(port, f"{port}"))
            lbl.setFixedWidth(64)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(styles.STATUS_LABEL_DEFAULT)
            self.peer_labels[(host, port)] = lbl
            layout.addWidget(lbl)

        layout.addStretch()

    def refresh(self):
        with self.server.clients_lock:
            connected = set(self.server.clients.keys())
        for mid, lbl in self.machine_labels.items():
            if mid in connected:
                lbl.setStyleSheet(styles.STATUS_LABEL_ON)
                lbl.setToolTip("연결됨")
            else:
                lbl.setStyleSheet(styles.STATUS_LABEL_OFF)
                lbl.setToolTip("미연결")

        for (host, port), lbl in self.peer_labels.items():
            alive = self.server.peer_status.get((host, port), True)
            if alive:
                lbl.setStyleSheet(styles.STATUS_LABEL_ON)
                lbl.setToolTip(f"{host}:{port} 정상")
            else:
                lbl.setStyleSheet(styles.STATUS_LABEL_DANGER)
                lbl.setToolTip(f"{host}:{port} 장애 감지")


# ── 재고 현황 탭 ─────────────────────────────────────────
class StockPanel(QWidget):
    def __init__(self, server):
        super().__init__()
        self.server = server
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        title = QLabel("실시간 재고 현황")
        title.setFont(QFont("", 13, QFont.Weight.Bold))
        layout.addWidget(title)

        self.table = make_table(["머신", "음료", "재고", "상태"])
        layout.addWidget(self.table)

    def refresh(self):
        rows = []
        for mid, drinks in sorted(self.server.stocks.items()):
            for _, info in sorted(drinks.items()):
                rows.append((mid, info["name"], info["count"]))

        self.table.setRowCount(len(rows))
        for r, (mid, name, count) in enumerate(rows):
            count = int(count)
            threshold = self.server.thresholds.get(mid, 3)
            if count == 0:
                status, color = "품절", styles.DANGER
            elif count <= threshold:
                status, color = "부족", styles.WARN
            else:
                status, color = "정상", styles.OK

            self.table.setItem(r, 0, cell(f"Machine {mid}"))
            self.table.setItem(r, 1, cell(name))
            self.table.setItem(r, 2, cell(count))
            item = cell(status)
            item.setForeground(QColor(color))
            self.table.setItem(r, 3, item)


# ── 매출 현황 탭 ─────────────────────────────────────────
class SalesPanel(QWidget):
    def __init__(self, server):
        super().__init__()
        self.server = server
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 날짜 선택
        top = QHBoxLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setFixedWidth(120)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["일별", "월별", "전체(누적)"])
        self.mode_combo.setFixedWidth(100)
        self.mode_combo.currentIndexChanged.connect(self.on_mode_change)

        btn = QPushButton("조회")
        btn.setFixedWidth(60)
        btn.clicked.connect(self.refresh)

        top.addWidget(QLabel("날짜:"))
        top.addWidget(self.date_edit)
        top.addWidget(self.mode_combo)
        top.addWidget(btn)
        top.addStretch()
        layout.addLayout(top)

        # 요약 카드
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet(styles.SUMMARY_LABEL)
        layout.addWidget(self.summary_label)

        # 테이블
        self.table = make_table(["머신", "음료", "판매수량", "매출액"])
        layout.addWidget(self.table)

    def on_mode_change(self):
        is_all = self.mode_combo.currentText() == "전체(누적)"
        self.date_edit.setVisible(not is_all)

    def refresh(self):
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        mode     = self.mode_combo.currentText()

        if mode == "일별":
            records = self.server.sales_bst.range_query(date_str, date_str)
            label   = f"{date_str} 일별 매출"
        elif mode == "월별":
            prefix = date_str[:7]           # YYYY-MM
            start  = prefix + "-01"
            end    = prefix + "-31"
            records = self.server.sales_bst.range_query(start, end)
            label   = f"{prefix} 월별 매출"
        else:
            records = self.server.sales_bst.inorder()
            label   = "전체 누적 매출"

        # 머신 + 음료별 집계
        agg = {}
        for r in records:
            mid  = r.get("machine_id", "?")
            name = r.get("drink_name", "?")
            key  = (mid, name)
            if key not in agg:
                agg[key] = {"count": 0, "revenue": 0}
            agg[key]["count"]   += 1
            agg[key]["revenue"] += int(r.get("price", 0))

        total = sum(v["revenue"] for v in agg.values())
        self.summary_label.setText(f"{label}  |  총 {total:,}원  ({len(records)}건)")

        # 버블 정렬 — 매출액 기준 내림차순
        items = list(agg.items())
        n = len(items)
        for i in range(n):
            for j in range(0, n - i - 1):
                if items[j][1]["revenue"] < items[j + 1][1]["revenue"]:
                    items[j], items[j + 1] = items[j + 1], items[j]

        self.table.setRowCount(n)
        for row, ((mid, name), stat) in enumerate(items):
            self.table.setItem(row, 0, cell(f"Machine {mid}"))
            self.table.setItem(row, 1, cell(name))
            self.table.setItem(row, 2, cell(stat["count"]))
            self.table.setItem(row, 3, cell(f"{stat['revenue']:,}원"))


# ── 제어 탭 ──────────────────────────────────────────────
class ControlPanel(QWidget):
    def __init__(self, server):
        super().__init__()
        self.server = server
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("음료 이름 / 가격 변경")
        title.setFont(QFont("", 13, QFont.Weight.Bold))
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("머신 선택:"), 0, 0)
        self.machine_combo = QComboBox()
        self.machine_combo.addItems([f"Machine {i}" for i in range(1, 5)])
        self.machine_combo.currentIndexChanged.connect(self.on_machine_change)
        grid.addWidget(self.machine_combo, 0, 1)

        grid.addWidget(QLabel("음료 선택:"), 1, 0)
        self.drink_combo = QComboBox()
        grid.addWidget(self.drink_combo, 1, 1)

        grid.addWidget(QLabel("새 이름:"), 2, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("변경할 이름 입력")
        grid.addWidget(self.name_input, 2, 1)

        grid.addWidget(QLabel("새 가격 (원):"), 3, 0)
        self.price_spin = QSpinBox()
        self.price_spin.setRange(10, 99999)
        self.price_spin.setSingleStep(10)
        self.price_spin.setValue(1000)
        grid.addWidget(self.price_spin, 3, 1)

        layout.addLayout(grid)

        send_btn = QPushButton("변경 전송")
        send_btn.setFixedWidth(120)
        send_btn.clicked.connect(self.on_send)
        layout.addWidget(send_btn)

        self.msg_label = QLabel("")
        layout.addWidget(self.msg_label)

        self.on_machine_change()

    def on_machine_change(self):
        mid = self.machine_combo.currentIndex() + 1
        self.drink_combo.clear()
        drinks = self.server.stocks.get(mid, {})
        for did, info in sorted(drinks.items()):
            self.drink_combo.addItem(info["name"], userData=did)

    def on_send(self):
        mid      = self.machine_combo.currentIndex() + 1
        drink_id = self.drink_combo.currentData()
        name     = self.name_input.text().strip()
        price    = self.price_spin.value()

        if not name:
            self.msg_label.setStyleSheet(styles.MSG_DANGER)
            self.msg_label.setText("이름을 입력해주세요.")
            return
        if drink_id is None:
            self.msg_label.setStyleSheet(styles.MSG_DANGER)
            self.msg_label.setText("음료를 선택해주세요.")
            return

        ok = self.server.send_to_client(mid, "DRINK_UPDATE", {
            "drink_id"  : int(drink_id),
            "drink_name": name,
            "price"     : price,
        })
        if ok:
            # 서버 인메모리 재고 이름도 갱신
            self.server.stocks.setdefault(mid, {})[str(drink_id)]["name"] = name
            self.msg_label.setStyleSheet(styles.MSG_OK)
            self.msg_label.setText(f"Machine {mid}에 전송 완료")
            self.on_machine_change()
        else:
            self.msg_label.setStyleSheet(styles.MSG_DANGER)
            self.msg_label.setText(f"Machine {mid} 미연결 — 전송 실패")


# ── 메인 윈도우 ──────────────────────────────────────────
class ServerWindow(QMainWindow):
    def __init__(self, server):
        super().__init__()
        self.server = server
        port_names = {9000: "Server1", 9001: "Server2", 9002: "Backup"}
        name = port_names.get(server.port, f":{server.port}")
        self.setWindowTitle(f"자판기 관리 서버 [{name}]")
        self.setGeometry(100, 100, 900, 560)
        self.setStyleSheet(styles.BASE_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 머신 상태 바
        self.status_bar = MachineStatusBar(server)
        root.addWidget(self.status_bar)

        # 탭
        tabs = QTabWidget()
        self.stock_panel   = StockPanel(server)
        self.sales_panel   = SalesPanel(server)
        self.control_panel = ControlPanel(server)
        tabs.addTab(self.stock_panel,   "재고 현황")
        tabs.addTab(self.sales_panel,   "매출 현황")
        tabs.addTab(self.control_panel, "제어")
        root.addWidget(tabs)

        # 3초 자동 갱신
        timer = QTimer(self)
        timer.timeout.connect(self.refresh_panels)
        timer.start(3000)
        self.refresh_panels()

    def refresh_panels(self):
        self.status_bar.refresh()
        self.stock_panel.refresh()
