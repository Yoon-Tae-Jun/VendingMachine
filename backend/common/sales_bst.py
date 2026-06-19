"""서버 매출 데이터를 날짜 기준 BST로 관리한다.

날짜 문자열(YYYY-MM-DD)을 key로 사용한다.
문자열 사전순 비교가 날짜 순서와 일치하므로 별도 변환 없이 사용 가능하다.
"""


class SalesNode:
    def __init__(self, date: str):
        self.date = date          # key: "YYYY-MM-DD"
        self.records = []         # list of dict (sales row)
        self.left = None
        self.right = None


class SalesBST:
    def __init__(self):
        self.root = None

    # ── 삽입 ────────────────────────────────────────────
    def insert(self, record: dict):
        """매출 레코드 1건을 날짜 노드에 삽입한다."""
        date = record.get("date")
        if not date:
            return
        self.root = self.insert_node(self.root, date, record)

    def insert_node(self, node, date: str, record: dict):
        if node is None:
            node = SalesNode(date)
            node.records.append(record)
            return node
        if date < node.date:
            node.left = self.insert_node(node.left, date, record)
        elif date > node.date:
            node.right = self.insert_node(node.right, date, record)
        else:
            node.records.append(record)
        return node

    # ── 단일 날짜 검색 ───────────────────────────────────
    def search(self, date: str):
        """특정 날짜 노드를 반환한다. 없으면 None."""
        return self.search_node(self.root, date)

    def search_node(self, node, date: str):
        if node is None or node.date == date:
            return node
        if date < node.date:
            return self.search_node(node.left, date)
        return self.search_node(node.right, date)

    # ── 날짜 범위 조회 ───────────────────────────────────
    def range_query(self, start: str, end: str) -> list:
        """start ~ end (inclusive) 범위의 모든 레코드를 날짜 오름차순으로 반환한다."""
        result = []
        self.range_query_node(self.root, start, end, result)
        return result

    def range_query_node(self, node, start: str, end: str, result: list):
        if node is None:
            return
        if node.date > start:
            self.range_query_node(node.left, start, end, result)
        if start <= node.date <= end:
            result.extend(node.records)
        if node.date < end:
            self.range_query_node(node.right, start, end, result)

    # ── 중위 순회 (전체 레코드, 날짜 오름차순) ────────────
    def inorder(self) -> list:
        result = []
        self.inorder_node(self.root, result)
        return result

    def inorder_node(self, node, result: list):
        if node is None:
            return
        self.inorder_node(node.left, result)
        result.extend(node.records)
        self.inorder_node(node.right, result)

    # ── 집계 헬퍼 ────────────────────────────────────────
    def aggregate_by_date(self, date: str) -> dict:
        """특정 날짜의 machine_id별 총매출을 반환한다."""
        node = self.search(date)
        return self.aggregate(node.records if node else [])

    def aggregate_range(self, start: str, end: str) -> dict:
        """날짜 범위의 machine_id별 총매출을 반환한다."""
        records = self.range_query(start, end)
        return self.aggregate(records)

    def aggregate(self, records: list) -> dict:
        """레코드 리스트 → {machine_id: {total, drinks: {name: {count, revenue}}}}"""
        result = {}
        for r in records:
            mid = r.get("machine_id", "unknown")
            if mid not in result:
                result[mid] = {"total": 0, "drinks": {}}
            price = int(r.get("price", 0))
            name  = r.get("drink_name", "")
            result[mid]["total"] += price
            drinks = result[mid]["drinks"]
            if name not in drinks:
                drinks[name] = {"count": 0, "revenue": 0}
            drinks[name]["count"]   += 1
            drinks[name]["revenue"] += price
        return result
