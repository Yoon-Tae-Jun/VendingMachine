class VendingMachineError(Exception):
    """예외 기본 클래스"""
    pass

class ExceedMaxMoneyError(VendingMachineError):
    """최대 투입 금액 초과 예외"""
    def __init__(self, amount, limit=7000):
        self.amount = amount
        self.limit = limit
        self.message = f"{amount}원은 제한 금액을 초과했습니다.(제한 금액: {limit}원)"
        super().__init__(self.message)

class ExceedMaxBillError(VendingMachineError):
    """지폐 투입 제한 초과 예외"""
    def __init__(self, bill_count, limit=5):
        self.bill_count = bill_count
        self.limit = limit
        self.message = f"투입하신 지폐 개수 {bill_count}장으로 제한 수를 초과했습니다.(제한 지폐 개수: {limit}장)"
        super().__init__(self.message)

class ShortageMoneyError(VendingMachineError):
    """잔액 부족 예외"""
    def __init__(self, required, available):
        self.required = required
        self.available = available
        self.message = f"구매하려는 음료의 가격 {required}원이 현재 투입된 금액 {available}원보다 많습니다."
        super().__init__(self.message)

class ShortageStockError(VendingMachineError):
    """재고 부족 예외"""
    def __init__(self, drink_name):
        self.drink_name = drink_name
        self.message = f"선택하신 음료 '{drink_name}'의 재고가 부족합니다."
        super().__init__(self.message)

class NoRefundAvailableError(VendingMachineError):
    """환불할 돈이 없는 경우 예외"""
    def __init__(self):
        self.message = "반환할 잔돈이 없습니다."
        super().__init__(self.message)

class ShortageChangeError(VendingMachineError):
    """거스름돈 부족 예외"""
    def __init__(self, remaining_change):
        self.remaining_change = remaining_change
        self.message = f"거스름돈 재고가 부족합니다. {remaining_change}원을 더 투입하여 금액을 맞춰주세요."
        super().__init__(self.message)

class DrinkNotFoundError(VendingMachineError):
    """음료를 찾을 수 없는 경우 예외"""
    def __init__(self, drink_name):
        self.drink_name = drink_name
        self.message = f"'{drink_name}' 음료를 찾을 수 없습니다."
        super().__init__(self.message)

class FileIOError(VendingMachineError):
    """파일 읽기/쓰기 오류 예외"""
    def __init__(self, file_path, detail=""):
        self.file_path = file_path
        self.message = f"파일 처리 중 오류가 발생했습니다: {file_path}" + (f"\n{detail}" if detail else "")
        super().__init__(self.message)

class ServerConnectionError(VendingMachineError):
    """서버 전송 실패 예외"""
    def __init__(self):
        self.message = "서버 전송 실패: 구매가 취소되었습니다."
        super().__init__(self.message)