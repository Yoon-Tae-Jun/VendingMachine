################## 공통 색상 ##################
OK           = "#2ECC71"         # 초록 (정상/성공)
DANGER       = "#E74C3C"         # 빨강 (오류/품절)
ACCENT       = "52, 152, 219"    # 파랑 RGB (rgba 사용)
ACCENT_PRESS = "41, 128, 185"    # 파랑 pressed
DANGER_RGB   = "231, 76, 60"     # 빨강 RGB (rgba 사용)
DANGER_PRESS = "192, 57, 43"     # 빨강 pressed
####################################################

################## 1. 자판기 화면 ##################
# 1.1 잔액 프레임
BALANCE_FRAME = """
    QWidget#balance_frame_container {
        border: 1px solid #ffffff;
        border-radius: 2px;
    }
    QLabel {
        qproperty-alignment: 'AlignCenter';
        color: white;
    }
    QLabel#balance_label {
        font-size: 30px;
        font-weight: bold;
    }
"""

# 1.2 음료 표시 프레임
DRINK_FRAME = f"""
    QPushButton {{
        height: 80px;
        font-size: 30px;
        border-radius: 2px;
        color: white;
    }}

    QPushButton#drink_button[status="ok"] {{
        background-color: {OK};
    }}

    QPushButton#drink_button[status="unaffordable"] {{
        background-color: rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.5);
    }}

    QPushButton#drink_button[status="empty"] {{
        background-color: {DANGER};
        color: white;
    }}
"""

# 1.3 돈 입력 프레임
MONEY_INPUT_FRAME = """
    QPushButton {
        color: white;
        background-color: rgba(255, 255, 255, 0.1);
    }
"""
####################################################
####################################################

################## 2. 관리자 화면 ##################
# 2.1 관리자 메뉴 프레임
ADMIN_MENU_FRAME = f"""
    QPushButton {{
        height: 30px;
        width: 120px;
        font-size: 14px;
        margin: 0;
        border: none;
    }}

    QPushButton#menu_button[active="true"] {{
        background-color: rgba({ACCENT}, 0.4);
        color: white;
    }}

    QPushButton#menu_button[active="false"] {{
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
    }}

    QPushButton#exit_button {{
        background-color: {DANGER};
        color: white;
    }}
"""

# 2.1.1 관리자 화면 제목
ADMIN_TITLE = """
    color: white;
    font-size: 18px;
    font-weight: bold;
"""
# 2.2 매출 관리 위젯 #
## 2.2.1 매출 스크롤 영역
SCROLL_AREA = """
    QScrollArea {
        border: none;
    }
"""

## 2.2.2 날짜 선택 프레임
DATE_SELECTOR_FRAME = f"""
    QDateEdit {{
        color: white;
        background: rgba({ACCENT}, 0.6);
        border: none;
        border-radius: 4px;
        padding: 4px;
    }}

    QPushButton {{
        color: white;
        background: rgba({ACCENT}, 0.6);
        border: none;
        border-radius: 4px;
        padding: 4px;
    }}
"""

## 2.2.3 매출 표시 카드(일, 주, 월 매출)
SALES_CARD = """
    QLabel {
        font-size: 14px;
        color: white;
        background: rgba(255, 255, 255, 0.1);
        border-radius:8px;
        padding:12px;
    }
"""

## 2.2.4 주 매출 그래프 프레임
CANVAS_STYLE = """
    background: rgba(255, 255, 255, 0.1);
"""

## 2.2.5 음료별 매출 테이블 내용
TABLE_CONTENT = """
    background: transparent;
    color: white;
    gridline-color: rgba(255,255,255,0.2);
"""

## 2.2.6 음료별 매출 테이블 제목
TABLE_HEADER = """
    color: white;
    background: rgba(255,255,255,0.1);
"""
####################################################
# 2.3 재고 관리 위젯 #
## 2.3.1 재고 위젯 제목
STOCK_TITLE = """
    color: white;
    font-size: 15px;
    font-weight: bold;
    padding: 0px 2px 8px 2px;
"""

## 2.3.2 재고 행 프레임
STOCK_ROW = """
    QFrame {
        background: rgba(255, 255, 255, 0.07);
        border-radius: 8px;
    }
    QFrame:hover {
        background: rgba(255, 255, 255, 0.12);
    }
"""

## 2.3.3 재고 이름 라벨
STOCK_NAME_LABEL = """
    color: white;
    font-size: 14px;
    background: transparent;
"""

## 2.3.4 재고 상태 뱃지 (뱃지 전용 색상은 별도 팔레트 사용)
STOCK_BADGE = """
    QLabel#stock_badge{
        color: white;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    QLabel#stock_badge[status="ok"] {
        background: rgba(5, 184, 23, 0.4);
    }
    QLabel#stock_badge[status="warning"] {
        background: rgba(126, 95, 37, 0.9);
    }
    QLabel#stock_badge[status="empty"] {
        background: rgba(249, 27, 6, 0.4);
    }
"""

## 2.3.5 재고 수량 조절 박스
STOCK_SPINBOX = """
    QSpinBox {
        color: white;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        padding: 2px 4px;
    }
    QSpinBox::up-button, QSpinBox::down-button {
        width: 16px;
    }
"""

## 2.3.6 재고 수량 보충 버튼
STOCK_RESTOCK_BTN = f"""
    QPushButton {{
        color: white;
        background: rgba({ACCENT}, 0.5);
        border-radius: 4px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background: rgba({ACCENT}, 0.85);
    }}
    QPushButton:pressed {{
        background: rgba({ACCENT_PRESS}, 1.0);
    }}
"""
####################################################
# 2.4 시재 관리 위젯 #
## 2.4.1 돈 개수 뱃지
MONEY_BADGE = """
    color: white;
    background: transparent;
    font-size: 12px;
    font-weight: bold;
"""

## 2.4.2 돈 액수 라벨
MONEY_VALUE_LABEL = """
    color: rgba(255, 255, 255, 0.7);
    font-size: 12px;
    background: transparent;
"""

## 2.4.3 시재 총합 프레임
MONEY_TOTAL_ROW = f"""
    QFrame {{
        background: rgba({ACCENT}, 0.6);
        border-radius: 8px;
    }}

    QLabel{{
        color: white;
        font-size: 13px;
        font-weight: bold;
        background: transparent;
    }}
"""

## 2.4.4 수금 버튼
MONEY_COLLECT_BTN = f"""
    QPushButton {{
        color: white;
        background: rgba({DANGER_RGB}, 0.5);
        border-radius: 4px;
        font-size: 13px;
        padding: 6px;
    }}
    QPushButton:hover {{
        background: rgba({DANGER_RGB}, 0.85);
    }}
    QPushButton:pressed {{
        background: rgba({DANGER_PRESS}, 1.0);
    }}
    QPushButton:disabled {{
        background: rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.3);
    }}
"""
####################################################
# 2.5 설정 위젯 #
## 2.5.1 비밀번호 설정 스크롤뷰
SETTING_SCROLL = """
    QScrollArea {
        background: transparent;
    }
    QScrollBar:vertical {
        width: 6px;
        background: rgba(255,255,255,0.05);
        border-radius: 3px;
    }
    QScrollBar::handle:vertical {
        background: rgba(255,255,255,0.25);
        border-radius: 3px;
        min-height: 20px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""

## 2.5.2 설정 소제목
SETTING_TITLE = """
    QLabel {
        color: white;
        font-size: 15px;
        font-weight: bold;
        padding-bottom: 4px;
    }
"""

## 2.5.3 설정 저장 버튼
SETTING_SAVE_BTN = f"""
    QPushButton {{
        color: white;
        background: rgba({ACCENT}, 0.5);
        border: 1px solid rgba({ACCENT}, 0.6);
        border-radius: 4px;
    }}
    QPushButton:hover {{
        background: rgba({ACCENT}, 0.85);
    }}
    QPushButton:pressed {{
        background: rgba({ACCENT_PRESS}, 1.0);
    }}
"""

## 2.5.4 설정 행 라벨
SETTING_ROW_LABEL = """
    color: white;
    font-size: 13px;
"""

## 2.5.5 설정 구분선
SETTING_LINE = """
    color: rgba(255,255,255,0.2);
"""

## 2.5.6 비밀번호 변경 영역
PASSWORD_SECTION = f"""
    QLabel#status {{
        font-size: 11px;
    }}
    QLabel#status[status="ok"]{{
        color: {OK};
    }}
    QLabel#status[status="error"]{{
        color: {DANGER};
    }}

    QLabel#row_label{{
        color:white;
        font-size: 12px;
    }}
"""

## 2.5.7 음료 설정 이름 입력창
DRINK_EDIT_INPUT = """
    QLineEdit {
        color: white;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 13px;
    }
"""

## 2.5.8 음료 설정 섹션 상태 메시지
DRINK_EDIT_SECTION = f"""
    QLabel#status {{
        font-size: 11px;
    }}
    QLabel#status[status="ok"] {{
        color: {OK};
    }}
    QLabel#status[status="error"] {{
        color: {DANGER};
    }}
"""

# 2.6 비밀번호 입력 다이얼로그 #
## 2.6.1 비밀번호 입력 필드
PASSWORD_INPUT = """
    QLineEdit {
        color: white;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 12px;
    }
    QLabel, QPushButton{
        color: white;
    }
"""
