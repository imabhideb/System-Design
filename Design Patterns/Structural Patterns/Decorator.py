from abc import ABC, abstractmethod

# Interface
class Coffee(ABC):
    @abstractmethod     # Abstract method is used when you want the concrete class to change or modify it
    def cost(self):
        pass
    
    @abstractmethod
    def description(self):
        pass

# Concrete Component: the base object being decorated
class SimpleCoffee(Coffee):
    def cost(self):
        return 50
    def description(self):
        return "Coffee"


# Base Decorator: wraps a Coffee object, delegates by default
class CoffeeDecorator(Coffee):
    def __init__(self, coffee: Coffee):
        self.coffee = coffee
    
    def cost(self):
        return self.coffee.cost()

    def description(self):
        return self.coffee.description()


# Concrete Decorators: each adds its own behavior on top
class MilkDecorator(CoffeeDecorator):
    def cost(self):
        return self.coffee.cost() + 10
    
    def description(self):
        return self.coffee.description() + " + Milk"

class SugarDecorator(CoffeeDecorator):
    def cost(self):
        return self.coffee.cost() + 5
    
    def description(self):
        return self.coffee.description() + " + Sugar"

class IceCreamDecorator(CoffeeDecorator):
    def cost(self):
        return self.coffee.cost() + 20
    
    def description(self):
        return self.coffee.description() + " + Ice cream whip"
    

coffee = SimpleCoffee()
print(f"{coffee.description()} -> ₹{coffee.cost()}")

coffee = MilkDecorator(coffee)
print(f"{coffee.description()} -> ₹{coffee.cost()}")

coffee = SugarDecorator(coffee)
print(f"{coffee.description()} -> ₹{coffee.cost()}")

coffee = IceCreamDecorator(coffee)
print(f"{coffee.description()} -> ₹{coffee.cost()}")



# The Decorator pattern lets you add new behavior to an object dynamically, 
# without modifying its class or affecting other instances of the same class. 
# It's an alternative to subclassing for extending functionality — you "wrap" an 
# object with one or more decorator objects that add responsibilities.