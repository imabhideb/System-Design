class Mobiles:
    def purchase(self):
        raise NotImplementedError("Subclasses must implement purchase()")


# Brand classes - You can keep on creating new class for new brands with impacting other flow
class Apple(Mobiles):
    def purchase(self):
        return "iPhone purchased"

class Samsung(Mobiles):
    def purchase(self):
        return "Samsung purchased"

class Google(Mobiles):
    def purchase(self):
        return "Pixel purchased"


# Factory Design - You can add any number of brands
class MobilesShop:
    brands = {
        "apple": Apple,
        "samsung": Samsung,
        "google": Google
    }

    @classmethod
    def getMobile(cls, brand):
        brand_cls = cls.brands.get(brand.lower())
        if brand_cls is None:
            raise ValueError(f"Unknown brand: {brand}")
        return brand_cls()

# You dont need to keep mofifying main to use/add/remove different brands
def main():
    # Usage of factory pattern
    mobile = MobilesShop.getMobile("Apple")
    print(mobile.purchase())

    mobile = MobilesShop.getMobile("Google")
    print(mobile.purchase())

main()



# FACTORY PATTERN

# One place decides WHICH object to create, based on some input.
# Callers just ask for what they want — they don't build it themselves.

# Why: if object-creation logic (if/elif chains, class lookups) is duplicated
# everywhere in your code, adding a new type means hunting down and editing
# every single place. With a factory, you add the new type in ONE place.


