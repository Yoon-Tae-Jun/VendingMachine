from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from ui.frame.AdminFrame import ScrollListFrame
from ui.frame.StockFrame import StockRow


class StockWidget(QWidget):
    def __init__(self, vending_machine):
        super().__init__()
        self.vending_machine = vending_machine
        self.init_ui()

    def init_ui(self):
        # 스크롤 리스트 프레임 생성
        self.frame = ScrollListFrame("재고 관리")

        # 스크롤 리스트 행 생성
        for drink in self.vending_machine.get_drinks():
            row = StockRow(drink, self.vending_machine, self.save)
            self.frame.add_row(row)
        self.frame.finalize()

        # 레이아웃 설정
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.frame)
        self.setLayout(outer)

    # 재고 행 전체 갱신 (이름·뱃지 동기화)
    def refresh(self):
        for row in self.frame.rows:
            row.refresh_name()
            row.update_badge()

    # 재고 변경 시 저장 함수
    def save(self):
        try:
            self.vending_machine.file_manager.write_drink(self.vending_machine.drinks)
        except Exception as e:
            QMessageBox.warning(self, "저장 오류", f"재고 저장 중 오류가 발생했습니다.\n{e}")
