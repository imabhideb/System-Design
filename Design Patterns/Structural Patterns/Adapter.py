class LegacyPayment:
    def __init__(self, amount):
        self.amount = amount
    
    def makeCardPayment(self, amount):
        print(f"{amount} paid to user using card")

class ModernPayment:
    def __init__(self, amount):
        self.amount = amount
    
    def makeUPIPayment(self, amount):
        print(f"{amount} paid to user using UPI")


# Interface
class PaymentProcessor:
    def pay(self, amount):
        raise NotImplementedError
    
# Adapters
class LegacyPaymentAdapter(PaymentProcessor):
    def __init__(self, legacy_payment: LegacyPayment):
        self.legacy_payment = legacy_payment

    def pay(self, amount):
        # translates the unified `pay` call into the legacy-specific method
        self.legacy_payment.makeCardPayment(amount)


class ModernPaymentAdapter(PaymentProcessor):
    def __init__(self, modern_payment: ModernPayment):
        self.modern_payment = modern_payment

    def pay(self, amount):
        self.modern_payment.makeUPIPayment(amount)

# Client Code 
def processPayment(processor: PaymentProcessor, amount):
    processor.pay(amount)


legacy_adapter = LegacyPaymentAdapter(LegacyPayment(100))
modern_adapter = ModernPaymentAdapter(ModernPayment(200))

processPayment(legacy_adapter, 100)   
processPayment(modern_adapter, 200)   

# Adapter Design Pattern
# Used to bridge the gap between two classes when they don't share a common method.
# It creates an Adapter class on top of them so the client code's flow isn't broken.

# You might wonder: why not just edit LegacyPayment directly to match the new interface?
# Because LegacyPayment might be used elsewhere (or be a third-party/external class you
# can't touch), so modifying it directly could break other things. The adapter pattern
# solves this without touching the original class at all.
