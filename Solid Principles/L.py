# Without L - Liskov Substitution Principle

class Bird:
    def fly(self):
        return "I am flying"


class Sparrow(Bird):
    def fly(self):
        return "Sparrow flying high"


class Ostrich(Bird):
    def fly(self):
        raise Exception("Ostriches can't fly!")


def make_it_fly(bird: Bird):
    print(bird.fly())


make_it_fly(Sparrow())   # works fine
make_it_fly(Ostrich())   # crashes!


# Without L - Liskov Substitution Principle

class Bird:
    def move(self):
        return "I am moving"


class FlyingBird(Bird):
    def move(self):
        return "I am flying"


class Sparrow(FlyingBird):
    pass


class Ostrich(Bird):
    def move(self):
        return "I am running"


def show_movement(bird: Bird):
    print(bird.move())


show_movement(Sparrow())
show_movement(Ostrich())