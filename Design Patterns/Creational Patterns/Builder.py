class TravelPackage:
    def __init__(self, guests, rooms, vehicles, flight, food):
        self.guests = guests
        self.rooms = rooms
        self.vehicles = vehicles
        self.flight = flight
        self.food = food

    def packages(self):
        return (
            f"Booking done for {self.rooms} rooms for {self.guests} guests. "
            f"Vehicles will {'be' if self.vehicles else 'not be'} provided. "
            f"Flights will {'be' if self.flight else 'not be'} booked. "
            f"Food is {'available' if self.food else 'not available'}."
        )


class TravelPackageBuilder:
    def __init__(self):
        self.guests = 0
        self.rooms = 0
        self.vehicles = False
        self.flight = False
        self.food = False

    def addGuests(self, guests):
        self.guests = guests
        return self

    def addRooms(self, rooms):
        self.rooms = rooms
        return self

    def needVehicles(self, vehicles):
        self.vehicles = vehicles
        return self

    def flightBooking(self, booking):
        self.flight = booking
        return self

    def addFood(self, food):
        self.food = food
        return self

    def getPackage(self):
        return TravelPackage(self.guests, self.rooms, self.vehicles, self.flight, self.food)


# Usage
package1 = (
    TravelPackageBuilder()
    .addGuests(3)
    .addRooms(2)
    .needVehicles(False)
    .flightBooking(True)
    .addFood(True)
    .getPackage()
)

print(package1.packages())


# Builder Pattern is used to simplify the construction of complex objects
# It separates the construction of an object from its representation,
# so the same step-by-step construction process can produce different
# configurations of an object. 

# Pros:
# - Simplifies creation of complex objects with many fields
# - Makes object construction more readable (named methods instead of
#   long positional constructor arguments)
# - Avoids "telescoping constructors" (multiple overloaded constructors
#   or one constructor with many optional parameters)
# - Allows validation of all fields together before the object is created
# - Final object can be made immutable once built, while the builder
#   itself stays mutable during construction

# Cons:
# - Overkill for simple objects with only a few fields
# - Duplicates fields between the builder class and the target class
# - Adds extra boilerplate code (an entire builder class) for what
#   could sometimes be a simple constructor call