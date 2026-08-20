from abc import ABC, abstractmethod

# Without O - Open/Closed Principle

class Disounts:
    def calculate(self, price, customer_type):
        if customer_type == "regular":
            return price * 0.95
        elif customer_type == "special":
            return price * 0.85
        elif customer_type == "vip":
            return price * 0.80
        else:
            return price

disc = Disounts()
print(disc.calculate(100, "vip"))

# With O - Open/Closed Principle

class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, price):
        pass

class RegularDiscount(DiscountStrategy):
    def apply(self, price):
        return price * 0.95

class SpecialDiscount(DiscountStrategy):
    def apply(self, price):
        return price * 0.90

class VIPDiscount(DiscountStrategy):
    def apply(self, price):
        return price * 0.80

class DiscountCalculator:
    def calculate_discount(self, price, strategy):
        return strategy.apply(price)

calculator = DiscountCalculator()
print(calculator.calculate_discount(1000, RegularDiscount()))
print(calculator.calculate_discount(1000, VIPDiscount()))