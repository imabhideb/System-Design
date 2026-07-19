class ControlTower:
    _instance = None    # Just a variable name(can be anything)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            print("Control Tower initialised")
        return cls._instance
    
    def manageFlights(self, flight):
        print("Managing flight {flight}")

tower1 = ControlTower()
tower2 = ControlTower()

tower1.manageFlights("Indigo")
tower2.manageFlights("Air India")

print(tower1 is tower2)



# Here even though two towers are created but both refers to one single instance
# The concept of Singleton is that only one instance will be created so that there isn't any conflict or issue in flow

# Example USE CASES 
# A database having multiple instances might led to data duplication or data corruption as multiple user might create multiple instance
# and play with data 