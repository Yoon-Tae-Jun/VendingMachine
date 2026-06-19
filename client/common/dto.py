from dataclasses import dataclass, asdict
@dataclass
class DrinkDTO:
    id: int
    name: str
    price: int
    count: int
    updated_time: str
    is_available: bool = True

    @classmethod
    def from_node(cls, node):
        """DrinkNode 객체를 DTO로 변환"""
        return cls(
            id=node.id,
            name=node.name,
            price=node.price,
            count=node.count,
            updated_time=node.updated_time,
            is_available= node.count > 0
        )
    
    def to_dict(self):
        return asdict(self)


@dataclass
class MoneyDTO:
    name: str
    count: int
    updated_time: str
    
    def to_dict(self):
        return {self.name: self.count}
    
@dataclass
class MoneyResponseDTO:
    input_money: int
    msg: str
    is_success: bool = False

@dataclass
class DrinkPurchaseResponseDTO:
    money_res: MoneyResponseDTO
    is_available_drink: bool

@dataclass
class SaleRecordDTO:
    date: str        # YYYY-MM-DD
    drink_id: int
    drink_name: str
    price: int
    stock_alert: int = 0  # 0=정상, 1=재고부족(low_stock_threshold 이하), 2=품절

    def to_dict(self):
        return asdict(self)
