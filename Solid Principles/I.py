from abc import ABC, abstractmethod

# Without I — Interface Segregation Principle
class Worker(ABC):
    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def eat(self):
        pass


class HumanWorker(Worker):
    def work(self):
        return "Human is working"

    def eat(self):
        return "Human is eating lunch"


class RobotWorker(Worker):
    def work(self):
        return "Robot is working"

    def eat(self):
        raise Exception("Robots don't eat!")


# With I — Interface Segregation Principle
class Workable(ABC):
    @abstractmethod
    def work(self):
        pass


class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass


class HumanWorker(Workable, Eatable):
    def work(self):
        return "Human is working"

    def eat(self):
        return "Human is eating lunch"


class RobotWorker(Workable):
    def work(self):
        return "Robot is working"


human = HumanWorker()
robot = RobotWorker()

print(human.work())
print(human.eat())
print(robot.work())