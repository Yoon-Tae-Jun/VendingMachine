import os
import csv

import hashlib
import re

import common.dto as dto
import common.exception as exception
from utils.structure import DrinkLinkedList, MoneyLinkedList
###### 파일 관련 유틸 ######
class FileManager:
    def __init__(self):
        self.BASE_DIR = "./data"
        self.DRINK_FILE = os.path.join(self.BASE_DIR, "drink.csv")
        self.MONEY_FILE = os.path.join(self.BASE_DIR, "money.csv")
        self.SALES_FILE = os.path.join(self.BASE_DIR, "sales.csv")
        self.CONFIG_FILE = os.path.join(self.BASE_DIR, "config.csv")
        self.STOCK_DEPLETION_FILE = os.path.join(self.BASE_DIR, "stock_depletion.csv")

    # csv 파일 읽기
    def read_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"{file_path} 파일이 존재하지 않습니다.")
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return [row for row in reader]
        except FileNotFoundError:
            raise
        except (OSError, csv.Error) as e:
            raise exception.FileIOError(file_path, str(e))

    # csv 파일 쓰기
    def write_file(self, data, file_path):
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"{file_path} 파일이 존재하지 않습니다.")
            with open(file_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        except FileNotFoundError:
            raise
        except (OSError, csv.Error) as e:
            raise exception.FileIOError(file_path, str(e))

    # 설정 파일 쓰기
    def write_config(self, config: dict):
        data = [{"key": k, "value": v} for k, v in config.items()]
        self.write_file(data, self.CONFIG_FILE)

    # 설정 파일 읽기 (password는 str, 나머지는 int로 변환)
    def load_config(self) -> dict:
        data = self.read_file(self.CONFIG_FILE)
        return {row["key"]: row["value"] if row["key"] == "password" else int(row["value"]) for row in data}
    
    # 매출 파일 쓰기 (stock_alert: 0=정상, 1=재고부족, 2=품절)
    def write_sale(self, drink_id: int, drink_name: str, price: int, stock_alert: int = 0):
        row = {
            "date": now_time(),
            "drink_id": drink_id,
            "drink_name": drink_name,
            "price": price,
            "stock_alert": stock_alert
        }
        with open(self.SALES_FILE, 'a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "drink_id", "drink_name", "price", "stock_alert"])
            writer.writerow(row)

    # 재고 소진 날짜 기록 (품절 시 append)
    def write_stock_depletion(self, drink_id: int, drink_name: str):
        fields = ["date", "drink_id", "drink_name"]
        file_exists = os.path.exists(self.STOCK_DEPLETION_FILE)
        with open(self.STOCK_DEPLETION_FILE, 'a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "date": now_time(),
                "drink_id": drink_id,
                "drink_name": drink_name,
            })

    # 마지막 매출 행 삭제 (롤백용)
    def delete_last_sale(self):
        data = self.read_file(self.SALES_FILE)
        if not data:
            return
        data = data[:-1]
        with open(self.SALES_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "drink_id", "drink_name", "price", "stock_alert"])
            writer.writeheader()
            writer.writerows(data)

    # 매출 파일 읽기
    def load_sales(self):
        data = self.read_file(self.SALES_FILE)
        return_data = [dto.SaleRecordDTO(
            date=item["date"],
            drink_id=int(item["drink_id"]),
            drink_name=item["drink_name"],
            price=int(item["price"]),
            stock_alert=int(item.get("stock_alert", 0))
        ) for item in data]
        return return_data
    
    # 시재 파일 쓰기
    def write_money(self, money_list: MoneyLinkedList):
        data = [{
                    "denomination": m.name, 
                    "count": m.count, 
                    "updated_time": now_time()
                } for m in money_list.get_datas()]
        self.write_file(data, self.MONEY_FILE)

    # 시재 파일 읽기
    def load_money(self):
        data = self.read_file(self.MONEY_FILE)
        return_data = [dto.MoneyDTO(
            name=item["denomination"],
            count=int(item["count"]),
            updated_time=item["updated_time"]
        ) for item in data]
        return return_data
    
    # 음료 재고 파일 쓰기
    def write_drink(self, drink_list: DrinkLinkedList):
        data = [{
                    "drink_id": d.id, 
                    "drink_name": d.name, 
                    "price": d.price, 
                    "count": d.count, 
                    "updated_time": now_time()
                } for d in drink_list.get_datas()]
        self.write_file(data, self.DRINK_FILE)

    # 음료 재고 파일 읽기
    def load_drink(self):
        data = self.read_file(self.DRINK_FILE)
        return_data = [dto.DrinkDTO(
            id=int(item["drink_id"]),
            name=item["drink_name"],
            price=int(item["price"]),
            count=int(item["count"]),
            updated_time=item["updated_time"],
        ) for item in data]

        return return_data
    
###### 비밀번호 관련 유틸 ######
class PasswordManager:
    def __init__(self):
        self.file_manager = FileManager()

    # 비밀번호를 SHA-256으로 해시화
    def hash(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def verify(self, pw):
        hashed = self.file_manager.load_config().get("password", "")
        return self.hash(pw) == hashed
            
    # 입력값 유효성 검사
    def validation(self, current_pw, new_pw, confirm_pw):
        hashed = self.file_manager.load_config().get("password", "")
        if not self.verify(current_pw):
            return {"status": False, "msg": "현재 비밀번호가 올바르지 않습니다."}
        elif len(new_pw) < 8:
            return {"status": False, "msg": "비밀번호는 8자 이상이어야 합니다."}
        elif not re.search(r"\d", new_pw):
            return {"status": False, "msg": "숫자를 1개 이상 포함해야 합니다."}
        elif not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", new_pw):
            return {"status": False, "msg": "특수문자를 1개 이상 포함해야 합니다."}
        elif new_pw != confirm_pw:
            return {"status": False, "msg": "새 비밀번호가 일치하지 않습니다."}
        else:
            return {"status": True, "msg": "비밀번호 검증 성공"}


    # 새 비밀번호를 해시화 후 config.csv에 저장
    def change(self, new_password):
        config = self.file_manager.load_config()
        config["password"] = self.hash(new_password)
        self.file_manager.write_config(config)

# 현재 시간 함수
def now_time():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")