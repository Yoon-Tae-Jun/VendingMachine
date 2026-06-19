from utils.util import FileManager

# 매출 관련 유틸 
class SalesManager:
    def __init__(self):
        self.file_manager = FileManager()

    # 매출 데이터 읽기
    def load(self):
        return self.file_manager.load_sales()

    # 매출 데이터 집계
    def aggregate(self, records) -> dict:
        drinks = {}
        for r in records:
            if r.drink_name not in drinks:
                drinks[r.drink_name] = {"count": 0, "revenue": 0}
            drinks[r.drink_name]["count"] += 1
            drinks[r.drink_name]["revenue"] += r.price
        return drinks

    # 특정 날짜의 일별 매출 조회
    def get_sales_by_date(self, date: str) -> dict:
        records = [r for r in self.load() if r.date[:10] == date]
        return {
            "date": date,
            "total_revenue": sum(r.price for r in records),
            "drinks": self.aggregate(records)
        }

    # 특정 날짜가 속한 주의 매출 조회
    def get_weekly_sales_by_date(self, date: str) -> dict:
        from datetime import datetime, timedelta
        d = datetime.strptime(date, "%Y-%m-%d")
        monday = d - timedelta(days=d.weekday()) # 해당 주 월요일
        sunday = monday + timedelta(days=6) # 해당 주 일요일
        dates = {(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)}
        records = [r for r in self.load() if r.date[:10] in dates]
        return {
            "week_start": monday.strftime("%Y-%m-%d"),
            "week_end": sunday.strftime("%Y-%m-%d"),
            "total_revenue": sum(r.price for r in records),
        }

    # 특정 날짜가 속한 월의 매출 조회
    def get_monthly_sales_by_date(self, date: str) -> dict:
        prefix = date[:7]  # "YYYY-MM" 앞 7자리로 월 필터링
        records = [r for r in self.load() if r.date.startswith(prefix)]
        return {
            "month": prefix,
            "total_revenue": sum(r.price for r in records),
        }

    # 특정 날짜가 속한 주의 일별 매출 조회 (막대 차트용)
    def get_weekly_chart_by_date(self, date: str) -> dict:
        from datetime import datetime, timedelta
        d = datetime.strptime(date, "%Y-%m-%d")
        monday = d - timedelta(days=d.weekday())
        dates = [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        records = [r for r in self.load() if r.date[:10] in dates]
        daily = {d: 0 for d in dates}

        # 매출 총액 계산
        for r in records:
            daily[r.date[:10]] += r.price
        return daily

    # 전체 매출 조회 (음료별 테이블, 도넛 차트용)
    def get_total_sales(self) -> dict:
        records = self.load()
        return {
            "total_revenue": sum(r.price for r in records),
            "drinks": self.aggregate(records)
        }
    