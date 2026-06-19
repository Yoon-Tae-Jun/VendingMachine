from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QFrame, QMessageBox
from PyQt6.QtCore import Qt
import ui.styles as style
from ui.frame.AdminFrame import ScrollListFrame
from ui.frame.MoneyFrame import MoneyRow, TotalRow

class MoneyWidget(QWidget):
    def __init__(self, vending_machine):
        super().__init__()
        self.vending_machine = vending_machine
        self.money_manager = self.vending_machine.money_manager
        self.init_ui()

    def init_ui(self):
        # 화면 설정
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.frame = ScrollListFrame("시재 관리")

        # 권종 내림차순 정렬
        money_list = sorted(
            self.vending_machine.get_money_data(),
            key=lambda m: int(m.name),
            reverse=True
        )
        # 권종 행 생성
        for money in money_list:
            self.frame.add_row(MoneyRow(money, self.on_click_refill))

        # 합계, 수금 행 생성
        self.total_row = TotalRow(self.update_total)
        self.update_total()  # total_row 할당 후 초기값 갱신

        # 합계, 수금 행 추가
        self.frame.add_footer(self.total_row)
        self.frame.add_footer(self.make_collect_btn())
        self.frame.finalize()

        # 레이아웃에 추가
        layout.addWidget(self.frame)
        self.setLayout(layout)

    # 수금 버튼 생성
    def make_collect_btn(self):
        self.collect_btn = QPushButton()
        self.collect_btn.setStyleSheet(style.MONEY_COLLECT_BTN)
        self.collect_btn.clicked.connect(self.on_click_collect)
        self.update_collect_btn()
        return self.collect_btn

    # 합계 라벨 업데이트
    def update_total(self):
        total = sum(int(r.money_dto.name) * r.money_dto.count for r in self.frame.rows)
        self.total_row.set_total(total)

    # 수금 버튼 텍스트 및 활성화 상태 업데이트
    def update_collect_btn(self):
        reserve = self.money_manager.min_money_reserve
        # 각 권종에서 최소 잔류 수량 초과분 * 권종 금액의 합
        collectable = sum(
            int(r.money_dto.name) * max(0, r.money_dto.count - reserve)
            for r in self.frame.rows
        )
        # 수금 가능한 경우
        if collectable > 0:
            self.collect_btn.setText(f"수금  ({collectable:,}원)  →  각 권종 {reserve}개 유지")
            self.collect_btn.setEnabled(True)
        # 수금 불가능한 경우
        else:
            self.collect_btn.setText(f"수금 가능 금액 없음  (현재 각 권종 {reserve}개 이하)")
            self.collect_btn.setEnabled(False)

    # 보충 버튼 이벤트
    def on_click_refill(self, denomination, amount):
        try:
            self.money_manager.refill_money(denomination, amount)
            self.update_total()
            self.update_collect_btn()
        except Exception as e:
            QMessageBox.warning(self, "보충 오류", f"시재 보충 중 오류가 발생했습니다.\n{e}")

    # 수금 버튼 이벤트
    def on_click_collect(self):
        try:
            self.money_manager.collect_money(self.money_manager.min_money_reserve)
            for row in self.frame.rows:
                row.refresh()
            self.update_total()
            self.update_collect_btn()
        except Exception as e:
            QMessageBox.warning(self, "수금 오류", f"수금 중 오류가 발생했습니다.\n{e}")

    # 화면 업데이트 함수
    def refresh(self):
        for row in self.frame.rows:
            row.refresh()
        self.update_total()
        self.update_collect_btn()
