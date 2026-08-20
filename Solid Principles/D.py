# Without D — Dependency Inversion Principle
class MySQLDatabase:
    def save(self, data):
        print(f"Saving '{data}' to MySQL database")


class InvoiceService:
    def __init__(self):
        self.db = MySQLDatabase()   # hardcoded dependency

    def save_invoice(self, data):
        self.db.save(data)


service = InvoiceService()
service.save_invoice("Invoice #123")


# With D — Dependency Inversion Principle
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def save(self, data):
        pass


class MySQLDatabase(Database):
    def save(self, data):
        print(f"Saving '{data}' to MySQL database")


class PostgreSQLDatabase(Database):
    def save(self, data):
        print(f"Saving '{data}' to PostgreSQL database")


class InvoiceService:
    def __init__(self, db: Database):
        self.db = db   # depends on the abstraction, injected from outside

    def save_invoice(self, data):
        self.db.save(data)


service1 = InvoiceService(MySQLDatabase())
service1.save_invoice("Invoice #123")

service2 = InvoiceService(PostgreSQLDatabase())
service2.save_invoice("Invoice #456")