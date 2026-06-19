import copy
from utils.structure import MoneyStack, MoneyLinkedList
from utils.util import FileManager, now_time
from network.driver import send_money
from common.dto import MoneyDTO, DrinkDTO, MoneyResponseDTO
import common.exception as exception

class MoneyManager:
    def __init__(self, machine_id: int):
        self.machine_id = machine_id
        self.input_money = 0 # 음료 구매 후 남은 잔액
        self.money_data = MoneyLinkedList()
        self.file_manager = FileManager()
        self.input_stack = None

        config = self.file_manager.load_config()
        self.min_money_reserve = config.get("min_money_reserve", 5)
        self.load_money()

    def load_money(self):
        "자판기에 돈 데이터 초기화"
        money_data = self.file_manager.load_money()
        for dto in money_data:
            self.money_data.add_data(dto)
                
    def insert_money(self, money: str):
        "돈 투입"
        try:
            # 최초 화폐 투입 시 메모리 할당
            if self.input_stack is None:
                self.input_stack = MoneyStack()
            
            money = MoneyDTO(name=money, count=1, updated_time=now_time())
            # 지폐 투입 제한: 지폐는 1000원까지만 허용, 지폐는 최대 5장까지만 허용
            if money.name == "1000" and (self.input_stack.get_bill_count() >= 5):
                raise exception.ExceedMaxBillError(self.input_stack.get_bill_count())
            
            # 최대 투입 금액 제한: 7000원까지만 허용
            if self.input_money + int(money.name) > 7000:
                raise exception.ExceedMaxMoneyError(money.name)

            self.input_stack.push(money)
            self.input_money += int(money.name)

            return MoneyResponseDTO(self.input_money, f"투입된 금액: {self.input_money}원", True)
        
        except exception.ExceedMaxBillError as e:
            return MoneyResponseDTO(self.input_money, e.message)
        except exception.ExceedMaxMoneyError as e:
            return MoneyResponseDTO(self.input_money, e.message)
        
    def return_money(self):
        "투입된 돈 반환"
        try:
            # 음료 구매 후 잔액 반환
            if self.input_stack is None:
                returned_money = self.calculate_change_details(self.input_money)
                for key, count in returned_money.items():
                    self.money_data.minus_money(str(key), count)
                self.file_manager.write_money(self.money_data)
                send_money(self.money_data)

            # 음료 구매 전 돈 반환
            else:
                while not self.input_stack.is_empty():
                    self.input_stack.pop()
                # 반환 후 메모리 해제
                self.input_stack = None 
                
            returned_money = self.input_money
            self.input_money = 0
            return MoneyResponseDTO(self.input_money, f"반환된 금액: {returned_money}원", True)
        
        except exception.NoRefundAvailableError as e:
            return MoneyResponseDTO(self.input_money, e.message)
        except exception.ShortageChangeError as e:
            return MoneyResponseDTO(self.input_money, e.message)
        
    def save_state(self):
        "구매 커밋 전 상태 저장 (롤백용)"
        self.saved_input_money = self.input_money
        self.saved_input_stack = copy.deepcopy(self.input_stack)
        self.saved_money_data  = copy.deepcopy(self.money_data)

    def rollback_purchase(self):
        "purchase_drink 커밋을 구매 전 상태로 원복"
        self.input_money = self.saved_input_money
        self.input_stack = self.saved_input_stack
        self.money_data  = self.saved_money_data
        self.file_manager.write_money(self.money_data)

    def purchase_drink(self, drink: DrinkDTO):
        "음료 구매 시 투입된 돈에서 가격 차감"
        try:
            # 예외처리
            # 투입된 돈이 없는 경우, 투입된 돈이 구매하려는 음료의 가격보다 적은 경우
            if self.input_money < drink.price:
                raise exception.ShortageMoneyError(drink.price, self.input_money)

            if not drink.is_available:
                raise exception.ShortageStockError(drink.name)
            
            # 구매확정
            if self.input_stack is not None:
                # 구매 커밋 전 돈 상태 저장 (롤백용)
                self.save_state()
                while not self.input_stack.is_empty():
                    money = self.input_stack.pop()
                    self.money_data.add_money(money)
                self.file_manager.write_money(self.money_data) # 구매 후 돈 데이터 파일에 저장 
                self.input_stack = None # 구매 후 입력 스택 초기화
            
            self.input_money -= drink.price # 잔액 반환
            return MoneyResponseDTO(self.input_money, f"{drink.name} 구매 완료({drink.price}원 차감)", True)
        except exception.ShortageMoneyError as e:
            return MoneyResponseDTO(self.input_money, e.message)
        except exception.ShortageStockError as e:
            return MoneyResponseDTO(self.input_money, e.message)
        
        
    # 특정 권종 시재 보충
    def set_min_money_reserve(self, value: int) -> None:
        self.min_money_reserve = value
        config = self.file_manager.load_config()
        config["min_money_reserve"] = value
        self.file_manager.write_config(config)

    def refill_money(self, denomination: str, amount: int) -> None:
        node = self.money_data.find_by_name(denomination)
        old_count = node.count
        node.count += amount
        self.file_manager.write_money(self.money_data)
        if not send_money(self.money_data):
            node.count = old_count
            self.file_manager.write_money(self.money_data)
            raise exception.ServerConnectionError()

    # 각 권종에서 최소 수량 초과분 수금
    def collect_money(self, reserve: int) -> int:
        saved = copy.deepcopy(self.money_data)
        collected = 0
        for money in self.money_data.get_datas():
            excess = max(0, money.count - reserve)
            collected += int(money.name) * excess
            money.count -= excess
        self.file_manager.write_money(self.money_data)
        if not send_money(self.money_data):
            self.money_data = saved
            self.file_manager.write_money(self.money_data)
            raise exception.ServerConnectionError()
        return collected

    def calculate_change_details(self, change_amount: int):
        """
        거스름돈 반환 로직
        - return: {단위: 개수} 딕셔너리
        - raise: 부족한 금액 정보를 담은 Exception
        """
        if change_amount == 0:
            raise exception.NoRefundAvailableError()

        units = [1000, 500, 100, 50, 10]
        result_change = {}
        remaining_change = change_amount

        # 1. 큰 단위 동전부터 탐색 (Greedy)
        for unit in units:
            if remaining_change <= 0:
                break
                
            count_needed = remaining_change // unit
            current_stock = self.money_data.find_by_name(str(unit)).count
            
            # 필요한 개수와 현재 재고 중 작은 값을 선택
            actual_count = min(count_needed, current_stock)
            
            if actual_count > 0:
                result_change[unit] = actual_count
                remaining_change -= (unit * actual_count)

        # 2. 거스름돈이 부족한 경우 처리
        if remaining_change > 0:
            raise exception.ShortageChangeError(remaining_change)

        return result_change