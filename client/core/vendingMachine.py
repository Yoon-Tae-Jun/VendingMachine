import utils.structure as structure
from utils.util import FileManager

from core.MoneyManager import MoneyManager
from common.dto import DrinkPurchaseResponseDTO, MoneyResponseDTO
import common.exception as exception
from network.driver import send_purchase, is_connected, send_config_update
class VendingMachine:
    def __init__(self, machine_id: int):
        self.machine_id = machine_id
        self.drinks = structure.DrinkLinkedList()
        self.file_manager = FileManager()
        self.init_drinks()
        self.money_manager = MoneyManager(machine_id=machine_id)

    def init_drinks(self):
        drink_data = self.file_manager.load_drink()
        for drink in drink_data:
            self.drinks.add_data(drink)
        config = self.file_manager.load_config()
        self.low_stock_threshold = config.get("low_stock_threshold", 3)
        self.max_stock = config.get("max_stock", 10)

    # 재고 경고 임계값 setter
    def set_low_stock_threshold(self, value):
        self.low_stock_threshold = value
        config = self.file_manager.load_config()
        config["low_stock_threshold"] = value
        self.file_manager.write_config(config)
        send_config_update(value)

    # 재고 최대 임계값 setter
    def set_max_stock(self, value):
        self.max_stock = value
        config = self.file_manager.load_config()
        config["max_stock"] = value
        self.file_manager.write_config(config)



    # 음료 리스트 반환
    def get_drinks(self):
        return self.drinks.get_datas()
    
    # 시재 데이터 반환
    def get_money_data(self):
        return self.money_manager.money_data.get_datas()
    
    # 입력 돈 반환
    def get_input_money(self):
        return self.money_manager.input_money
    
    # 돈 입력
    def insert_money(self, money):
        return self.money_manager.insert_money(money)

    # 돈 반환
    def refund_money(self):
        return self.money_manager.return_money()
    
    # 음료, 돈 반환(싱크용)
    def get_sync_data(self):
        return self.get_drinks(), self.money_manager.money_data 
    # 음료 이름/가격 수정 후 파일 저장
    def update_drink(self, drink_id: int, name: str, price: int):
        self.drinks.update_drink(drink_id, name, price)
        self.file_manager.write_drink(self.drinks)

    # 음료 구매
    def purchase_drink(self, drink: str):
        # 음료 이름으로 DTO 조회
        drink_dto = self.drinks.find_by_name(drink)
        if drink_dto is None:
            err = MoneyResponseDTO(self.money_manager.input_money, exception.DrinkNotFoundError(drink).message)
            return DrinkPurchaseResponseDTO(err, False)

        # 서버 미연결 예외 처리
        if not is_connected():
            err = MoneyResponseDTO(self.money_manager.input_money, "서버 연결 오류: 구매가 취소되었습니다.")
            return DrinkPurchaseResponseDTO(err, drink_dto.is_available)

        # 구매 트랜잭션
        # 1. money 차감
        res = self.money_manager.purchase_drink(drink_dto)
        if res.is_success:
            # 구매 후 재고 알림 레벨 결정 (0=정상, 1=부족, 2=품절)
            next_count = drink_dto.count - 1
            if next_count == 0:
                stock_alert = 2
            elif next_count <= self.low_stock_threshold:
                stock_alert = 1
            else:
                stock_alert = 0

            # 2. 메모리 재고 차감
            try:
                self.drinks.minus_drink(drink_dto)
            except Exception as e:
                # 실패 시 money 롤백
                self.money_manager.rollback_purchase()
                err = MoneyResponseDTO(self.money_manager.input_money, f"재고 오류: {e}")
                return DrinkPurchaseResponseDTO(err, drink_dto.is_available)

            # 3. 재고 파일 저장
            try:
                self.file_manager.write_drink(self.drinks)
            except Exception as e:
                # 실패 시 money, 메모리 재고 롤백
                self.drinks.plus_drink(drink_dto)
                self.money_manager.rollback_purchase()
                err = MoneyResponseDTO(self.money_manager.input_money, f"파일 오류: {e}")
                return DrinkPurchaseResponseDTO(err, drink_dto.is_available)

            # 4. 매출 파일 저장
            try:
                self.file_manager.write_sale(drink_dto.id, drink_dto.name, drink_dto.price, stock_alert)
            except Exception as e:
                # 실패 시 money, 재고 메모리 및 파일 롤백
                self.drinks.plus_drink(drink_dto)
                self.file_manager.write_drink(self.drinks)
                self.money_manager.rollback_purchase()
                err = MoneyResponseDTO(self.money_manager.input_money, f"파일 오류: {e}")
                return DrinkPurchaseResponseDTO(err, drink_dto.is_available)

            # 5. 서버 전송
            try:
                send_purchase(
                    drink_dto.id, drink_dto.name, drink_dto.price, stock_alert,
                    drink_dto.count, self.money_manager.money_data
                )
            except Exception as e:
                # 실패 시 money, 재고 메모리 및 파일, 매출 파일 롤백
                self.drinks.plus_drink(drink_dto)
                self.file_manager.write_drink(self.drinks)
                self.file_manager.delete_last_sale()
                self.money_manager.rollback_purchase()
                err = MoneyResponseDTO(self.money_manager.input_money, str(e))
                return DrinkPurchaseResponseDTO(err, drink_dto.is_available)

        # 품절 시 소진 날짜 기록 (트랜잭션 전 단계 성공 후 기록)
        if res.is_success and stock_alert == 2:
            try:
                self.file_manager.write_stock_depletion(drink_dto.id, drink_dto.name)
            except Exception:
                pass

        return DrinkPurchaseResponseDTO(res, self.drinks.get_is_available(drink_dto))

            