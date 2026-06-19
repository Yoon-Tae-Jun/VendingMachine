from common.dto import DrinkDTO, MoneyDTO

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    # 데이터 추가
    def add_data(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def get_datas(self):
        data_list = []
        current = self.head
        while current:
            data_list.append(current.data)
            current = current.next
        return data_list

class DrinkLinkedList(LinkedList):
    def find_by_name(self, name: str):
        current = self.head
        while current:
            if current.data.name == name:
                return current.data
            current = current.next
        return None
    
    def minus_drink(self, drink: DrinkDTO):
        current = self.head
        while current:
            if current.data.name == drink.name:
                current.data.count -= 1
                current.data.is_available = current.data.count > 0
                return current.data.is_available
            current = current.next
        raise ValueError(f"{drink.name} 음료가 존재하지 않습니다.")

    def plus_drink(self, drink: DrinkDTO):
        current = self.head
        while current:
            if current.data.name == drink.name:
                current.data.count += 1
                current.data.is_available = True
                return
            current = current.next
        raise ValueError(f"{drink.name} 음료가 존재하지 않습니다.")

    def get_is_available(self, drink: DrinkDTO):
        current = self.head
        while current:
            if current.data.name == drink.name:
                return current.data.is_available
            current = current.next

    def update_drink(self, drink_id: int, name: str, price: int):
        current = self.head
        while current:
            if current.data.id == drink_id:
                current.data.name = name
                current.data.price = price
                return current.data
            current = current.next
        raise ValueError(f"ID {drink_id} 음료가 존재하지 않습니다.")
    
class MoneyLinkedList(LinkedList):
    def add_money(self, money: MoneyDTO):
        current = self.head
        while current:
            if current.data.name == money.name:
                current.data.count += money.count
                return
            current = current.next
        raise ValueError(f"{money.name} 권종이 존재하지 않습니다.")
    
    def minus_money(self, money: str, count: int):
        current = self.head
        while current:
            if current.data.name == money:
                current.data.count -= count
                return
            current = current.next
        raise ValueError(f"{money} 권종이 존재하지 않습니다.")
    

    def find_by_name(self, name: str):
        current = self.head
        while current:
            if current.data.name == name:
                return current.data
            current = current.next
        return None
    
class MoneyStack:
    def __init__(self):
        self.stack = []

    def push(self, money):
        "돈 추가"
        self.stack.append(money)

    def pop(self):
        ""
        if not self.is_empty():
            return self.stack.pop()
        raise IndexError("스택이 비어있습니다.")

    def is_empty(self):
        return len(self.stack) == 0
    
    def size(self):
        return len(self.stack)

    def get_total(self):
        return sum(int(money.name) for money in self.stack)

    def get_bill_count(self):
        return len([m for m in self.stack if m.name == "1000"])
    
    def clear(self):
        self.stack.clear()


class Queue:
    def __init__(self):
        self.front = None
        self.rear  = None
        self.count = 0

    def enqueue(self, data):
        node = Node(data)
        if not self.rear:
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self.count += 1

    def dequeue(self):
        if not self.front:
            return None
        data = self.front.data
        self.front = self.front.next
        if not self.front:
            self.rear = None
        self.count -= 1
        return data

    def size(self):
        return self.count

    def is_empty(self):
        return self.count == 0

    def to_list(self):
        result, cur = [], self.front
        while cur:
            result.append(cur.data)
            cur = cur.next
        return result