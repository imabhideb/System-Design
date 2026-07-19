from abc import ABC, abstractmethod

# Interface
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

# Different Payment Strategies
class UPIPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"{amount} paid using UPI")

class CardPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"{amount} paid using Credit Card")

class CryptoPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"{amount} paid using Cryptocurrency")
    
# Context Class to use the payment strategies
class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def processPayment(self, amount):
        self.strategy.pay(amount)
    
    def setStrategy(self, strategy: PaymentStrategy):
        self.strategy = strategy


# Client Code 
processor = PaymentProcessor(CardPayment())
processor.processPayment(200)

processor.setStrategy(UPIPayment())
processor.processPayment(500)


# Factory Pattern: concerned with HOW an object is created (decides which class to instantiate)
# Strategy Pattern: concerned with WHAT an object does (interchangeable algorithms/behavior)
# They're often combined: a factory picks the right strategy instance based on some input.