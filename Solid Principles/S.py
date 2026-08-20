
# Issues without Singular responsibility
class Invoice:
    def __init__(self, amount):
        self.revenue = 5000
        self.amount = amount

    def get_bill(self):
        return f"The total bill is ₹{self.amount}"

    def save_bill(self):
        return f"The bill amount of {self.amount} is saved in registry"

    def fetch_revenue(self):
        return f"Total revenue is ₹{self.amount + self.revenue}"


# With Singular responsibility
class InvoiceGenerator:
    def __init__(self, amount):
        self.amount = amount

    def gen_bill(self):
        return f"Your bill is {self.amount}"

class Registry:
    def __init__(self, amount):
        self.amount = amount

    def save_bill(self, amount):
        return f"The bill amount of {self.amount} is saved in registry"

class Revenue:
    def __init__(self, amount):
        self.revenue = 5000
        self.amount = amount

    def fetch_revenue(self,amount):
        self.revenue += amount
        return f"Total revenue is ₹{self.amount}"

invoice1 = Invoice(100)
print(invoice1.fetch_revenue())


invoice2 = InvoiceGenerator(500)
print(invoice2.gen_bill())