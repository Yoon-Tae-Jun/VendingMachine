################## 공통 색상 ##################
BG      = "#1A1A2E"
SURFACE = "#16213E"
ACCENT  = "#2D89EC"
TEXT    = "#FFFFFF"
MUTED   = "#AAAAAA"
OK      = "#2ECC71"
WARN    = "#F39C12"
DANGER  = "#E74C3C"
####################################################

################## 기본 스타일 ##################
BASE_STYLE = f"""
    QMainWindow, QWidget {{ background: {BG}; color: {TEXT}; }}
    QTabWidget::pane {{ border: 1px solid #333; }}
    QTabBar::tab {{
        background: {SURFACE}; color: {MUTED};
        padding: 8px 20px; border-radius: 2px;
    }}
    QTabBar::tab:selected {{ background: {ACCENT}; color: {TEXT}; }}
    QTableWidget {{
        background: {SURFACE}; color: {TEXT};
        gridline-color: #333; border: none;
    }}
    QHeaderView::section {{
        background: #0F3460; color: {TEXT};
        padding: 4px; border: none;
    }}
    QPushButton {{
        background: {ACCENT}; color: {TEXT};
        border-radius: 4px; padding: 6px 14px;
    }}
    QPushButton:hover {{ background: #4A9EFF; }}
    QPushButton:disabled {{ background: #555; color: #888; }}
    QDateEdit, QComboBox, QLineEdit, QSpinBox {{
        background: {SURFACE}; color: {TEXT};
        border: 1px solid #444; padding: 4px; border-radius: 3px;
    }}
    QScrollArea {{ border: none; }}
    QLabel {{ color: {TEXT}; }}
"""
####################################################

################## 1. 머신 상태 바 ##################
# 1.1 상태 바 프레임
STATUS_BAR_FRAME = f"QFrame {{ background:{SURFACE}; border-bottom:1px solid #333; }}"

# 1.2 상태 라벨 기본값
STATUS_LABEL_DEFAULT = "border-radius:4px; padding:2px 6px;"

# 1.3 상태 라벨 (연결됨 / 피어 정상)
STATUS_LABEL_ON = f"background:{OK}; color:#000; border-radius:4px; padding:2px 6px;"

# 1.4 상태 라벨 (미연결)
STATUS_LABEL_OFF = f"background:#444; color:{MUTED}; border-radius:4px; padding:2px 6px;"

# 1.5 상태 라벨 (피어 장애)
STATUS_LABEL_DANGER = f"background:{DANGER}; color:#fff; border-radius:4px; padding:2px 6px;"

# 1.6 수직 구분선
STATUS_SEPARATOR = "color:#444;"
####################################################

################## 2. 매출 현황 탭 ##################
# 2.1 요약 라벨
SUMMARY_LABEL = f"color:{ACCENT}; font-size:13px;"
####################################################

################## 3. 제어 탭 ##################
# 3.1 상태 메시지 (성공)
MSG_OK = f"color:{OK};"

# 3.2 상태 메시지 (오류)
MSG_DANGER = f"color:{DANGER};"
####################################################
