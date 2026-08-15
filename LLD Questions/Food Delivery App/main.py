from datetime import datetime
from enum import Enum
from typing import Optional, List
from abc import ABC, abstractmethod
import uuid


# ------------------- ENUMS -------------------

class FoodType(Enum):
    VEG = "veg"
    NON_VEG = "non_veg"

class OrderStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class DeliveryPartnerStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"


# ------------------- CORE ENTITIES -------------------

class Address:
    def __init__(self, street, city, pincode, lat, long):
        self.street = street
        self.city = city
        self.pincode = pincode
        self.lat = lat
        self.long = long


class User:
    def __init__(self, id, name, email, address: Address):
        self.userId = id
        self.userName = name
        self.userEmail = email
        self.address = address


class FoodItem:
    def __init__(self, id, name, price, foodType: FoodType):
        self.foodId = id
        self.foodName = name
        self.foodType = foodType
        self.price = price


class Menu:
    def __init__(self, id, foodItems: List[FoodItem]):
        self.menuId = id
        self.foodItems = foodItems  # list of FoodItem


class Restaurant:
    def __init__(self, id, name, menu: Menu, lat, long):
        self.restId = id
        self.restName = name
        self.menu = menu
        self.lat = lat
        self.long = long


class DeliveryPartner:
    def __init__(self, id, name, lat, long, status: DeliveryPartnerStatus):
        self.delId = id
        self.delName = name
        self.lat = lat
        self.long = long
        self.status = status


# ------------------- CART -------------------

class CartItem:
    def __init__(self, food_item: FoodItem, quantity: int):
        self.foodItem = food_item
        self.quantity = quantity

    def get_subtotal(self) -> float:
        return self.foodItem.price * self.quantity  # live price


class Cart:
    def __init__(self, id, user_id, restaurant: Restaurant):
        self.cartId = id
        self.userId = user_id
        self.restaurant = restaurant
        self.items: List[CartItem] = []

    def add_item(self, food_item: FoodItem, quantity: int = 1):
        for item in self.items:
            if item.foodItem.foodId == food_item.foodId:
                item.quantity += quantity
                return
        self.items.append(CartItem(food_item, quantity))

    def remove_item(self, food_id):
        self.items = [i for i in self.items if i.foodItem.foodId != food_id]

    def get_total_price(self) -> float:
        return sum(item.get_subtotal() for item in self.items)

    def clear(self):
        self.items = []


# ------------------- ORDER -------------------

class OrderItem:
    def __init__(self, food_item: FoodItem, quantity: int, price_at_order: float):
        self.foodItem = food_item
        self.quantity = quantity
        self.priceAtOrder = price_at_order  # snapshot, not live FoodItem.price

    def get_subtotal(self) -> float:
        return self.priceAtOrder * self.quantity


class Order:
    def __init__(self, id, user: User, restaurant: Restaurant, items: List[OrderItem], status: OrderStatus,
                 delivery_address: Address, delivery_partner: Optional[DeliveryPartner] = None):
        self.orderId = id
        self.user = user
        self.restaurant = restaurant
        self.items = items
        self.status = status
        self.createdAt = datetime.now()
        # Snapshot the address at order time — if User.address changes later,
        # this order's delivery address must NOT silently change with it.
        self.deliveryAddress = delivery_address
        # Not known at order-creation time; assigned later in the flow.
        self.deliveryPartner = delivery_partner

    def assign_partner(self, partner: DeliveryPartner):
        self.deliveryPartner = partner

    def update_status(self, status: OrderStatus):
        self.status = status

    def get_total_amount(self) -> float:
        return sum(item.get_subtotal() for item in self.items)


# There might be a doubt why we are using interfaces here.
# Using an interface makes it easy to plug and play — e.g. when we want to
# swap the storage from in-memory to a real DB, callers depend on the
# interface, not the concrete class, so nothing above the repo layer changes.

# ------------------- USER REPOSITORY -------------------

class IUserRepository(ABC):
    @abstractmethod
    def addUser(self, user: User) -> None: ...

    @abstractmethod
    def getById(self, user_id) -> Optional[User]: ...

    @abstractmethod
    def getByEmail(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def remove(self, user_id) -> None: ...


class UserRepository(IUserRepository):
    def __init__(self):
        self.users = {}

    def addUser(self, user: User) -> None:
        self.users[user.userId] = user

    def getById(self, user_id) -> Optional[User]:
        return self.users.get(user_id)

    def getByEmail(self, email: str) -> Optional[User]:
        email = email.strip().lower()
        return next((u for u in self.users.values() if u.userEmail.lower() == email), None)

    def remove(self, user_id) -> None:
        self.users.pop(user_id, None)


# ------------------- RESTAURANT REPOSITORY -------------------

class IRestaurantRepository(ABC):
    @abstractmethod
    def addRestaurant(self, restaurant: Restaurant) -> None: ...

    @abstractmethod
    def getById(self, restaurant_id) -> Optional[Restaurant]: ...

    @abstractmethod
    def getRestaurantByName(self, name: str) -> List[Restaurant]: ...

    @abstractmethod
    def getRestaurantByFoodItem(self, food_name: str) -> List[Restaurant]: ...

    @abstractmethod
    def remove(self, restaurant_id) -> None: ...

    @abstractmethod
    def update(self, restaurant: Restaurant) -> None: ...


class RestaurantRepository(IRestaurantRepository):
    def __init__(self):
        self.restaurants = {}

    def addRestaurant(self, restaurant: Restaurant) -> None:
        self.restaurants[restaurant.restId] = restaurant

    def getById(self, restaurant_id) -> Optional[Restaurant]:
        return self.restaurants.get(restaurant_id)

    def getRestaurantByName(self, name: str) -> List[Restaurant]:
        name = name.strip().lower()
        return [restaurant for restaurant in self.restaurants.values()
                if name in restaurant.restName.strip().lower()]

    def getRestaurantByFoodItem(self, food_name: str) -> List[Restaurant]:
        food_name = food_name.strip().lower()
        return [restaurant for restaurant in self.restaurants.values()
                if any(item.foodName.lower() == food_name for item in restaurant.menu.foodItems)]

    def remove(self, restaurant_id) -> None:
        self.restaurants.pop(restaurant_id, None)

    def update(self, restaurant: Restaurant) -> None:
        self.restaurants[restaurant.restId] = restaurant


# ------------------- CART REPOSITORY -------------------

class ICartRepository(ABC):
    @abstractmethod
    def addCart(self, cart: Cart) -> None: ...

    @abstractmethod
    def getById(self, cart_id) -> Optional[Cart]: ...

    @abstractmethod
    def getByUserId(self, user_id) -> Optional[Cart]: ...

    @abstractmethod
    def save(self, cart: Cart) -> None: ...

    @abstractmethod
    def delete(self, cart_id) -> None: ...


class CartRepository(ICartRepository):
    def __init__(self):
        self.carts = {}                # cartId -> Cart
        self.user_cart_index = {}      # userId -> cartId, for O(1) lookup by user

    def addCart(self, cart: Cart) -> None:
        self.carts[cart.cartId] = cart
        self.user_cart_index[cart.userId] = cart.cartId

    def getById(self, cart_id) -> Optional[Cart]:
        return self.carts.get(cart_id)

    def getByUserId(self, user_id) -> Optional[Cart]:
        cart_id = self.user_cart_index.get(user_id)
        return self.carts.get(cart_id) if cart_id else None

    def save(self, cart: Cart) -> None:
        # covers both create and update since Cart is mutated in place
        self.carts[cart.cartId] = cart
        self.user_cart_index[cart.userId] = cart.cartId

    def delete(self, cart_id) -> None:
        cart = self.carts.pop(cart_id, None)
        if cart:
            self.user_cart_index.pop(cart.userId, None)


# ------------------- ORDER REPOSITORY -------------------

class IOrderRepository(ABC):
    @abstractmethod
    def addOrder(self, order: Order) -> None: ...

    @abstractmethod
    def getById(self, order_id) -> Optional[Order]: ...

    @abstractmethod
    def getByUserId(self, user_id) -> List[Order]: ...

    @abstractmethod
    def getByRestaurantId(self, restaurant_id) -> List[Order]: ...

    @abstractmethod
    def getByStatus(self, status: OrderStatus) -> List[Order]: ...

    @abstractmethod
    def update(self, order: Order) -> None: ...


class OrderRepository(IOrderRepository):
    def __init__(self):
        self.orders = {}

    def addOrder(self, order: Order) -> None:
        self.orders[order.orderId] = order

    def getById(self, order_id) -> Optional[Order]:
        return self.orders.get(order_id)

    def getByUserId(self, user_id) -> List[Order]:
        return [o for o in self.orders.values() if o.user.userId == user_id]

    def getByRestaurantId(self, restaurant_id) -> List[Order]:
        return [o for o in self.orders.values() if o.restaurant.restId == restaurant_id]

    def getByStatus(self, status: OrderStatus) -> List[Order]:
        return [o for o in self.orders.values() if o.status == status]

    def update(self, order: Order) -> None:
        self.orders[order.orderId] = order


# ------------------- DELIVERY PARTNER REPOSITORY -------------------

class IDeliveryPartnerRepository(ABC):
    @abstractmethod
    def add(self, partner: DeliveryPartner) -> None: ...

    @abstractmethod
    def getById(self, partner_id) -> Optional[DeliveryPartner]: ...

    @abstractmethod
    def getAvailableNear(self, lat, long, radius_km) -> List[DeliveryPartner]: ...

    @abstractmethod
    def updateStatus(self, partner_id, status: DeliveryPartnerStatus) -> None: ...

    @abstractmethod
    def remove(self, partner_id) -> None: ...


class DeliveryPartnerRepository(IDeliveryPartnerRepository):
    def __init__(self):
        self.partners = {}

    def add(self, partner: DeliveryPartner) -> None:
        self.partners[partner.delId] = partner

    def getById(self, partner_id) -> Optional[DeliveryPartner]:
        return self.partners.get(partner_id)

    def getAvailableNear(self, lat, long, radius_km) -> List[DeliveryPartner]:
        # placeholder distance check — swap in a real haversine calc later
        return [p for p in self.partners.values()
                if p.status == DeliveryPartnerStatus.AVAILABLE
                and _distance(lat, long, p.lat, p.long) <= radius_km]

    def updateStatus(self, partner_id, status: DeliveryPartnerStatus) -> None:
        partner = self.partners.get(partner_id)
        if partner:
            partner.status = status

    def remove(self, partner_id) -> None:
        self.partners.pop(partner_id, None)


def _distance(lat1, long1, lat2, long2) -> float:
    # TODO: replace with haversine formula for real lat/long distance
    return ((lat1 - lat2) ** 2 + (long1 - long2) ** 2) ** 0.5


# ------------------------- SERVICES -------------------------------------

class CartService:
    def __init__(self, cart_repo: ICartRepository):
        self.cart_repo = cart_repo

    def get_or_create_cart(self, user_id, restaurant: Restaurant) -> Cart:
        cart = self.cart_repo.getByUserId(user_id)

        if cart is None:
            cart = Cart(id=str(uuid.uuid4()), user_id=user_id, restaurant=restaurant)
            self.cart_repo.addCart(cart)
            return cart

        # Enforce single-restaurant-per-cart: switching restaurants clears the old cart
        if cart.restaurant.restId != restaurant.restId:
            cart.restaurant = restaurant
            cart.clear()
            self.cart_repo.save(cart)

        return cart

    def add_item(self, user_id, restaurant: Restaurant, food_item: FoodItem, quantity: int = 1) -> Cart:
        cart = self.get_or_create_cart(user_id, restaurant)
        cart.add_item(food_item, quantity)
        self.cart_repo.save(cart)
        return cart

    def remove_item(self, user_id, food_id) -> Optional[Cart]:
        cart = self.cart_repo.getByUserId(user_id)
        if cart is None:
            return None
        cart.remove_item(food_id)
        self.cart_repo.save(cart)
        return cart

    def view_cart(self, user_id) -> Optional[Cart]:
        return self.cart_repo.getByUserId(user_id)

    def clear_cart(self, user_id) -> None:
        cart = self.cart_repo.getByUserId(user_id)
        if cart:
            cart.clear()
            self.cart_repo.save(cart)


class OrderService:
    """
    Owns the Cart -> Order transition (checkout). CartService never touches
    Order/OrderStatus — that boundary is intentional so cart logic doesn't
    have to change if the order flow changes later.
    """
    def __init__(self, order_repo: IOrderRepository, cart_repo: ICartRepository):
        self.order_repo = order_repo
        self.cart_repo = cart_repo

    def place_order(self, user: User, delivery_address: Optional[Address] = None) -> Order:
        cart = self.cart_repo.getByUserId(user.userId)
        if cart is None or len(cart.items) == 0:
            raise ValueError("Cannot place an order from an empty cart")

        # Freeze live cart prices into OrderItems — this is the snapshot step.
        # If the restaurant changes a price tomorrow, this order must not change.
        order_items = [
            OrderItem(
                food_item=cart_item.foodItem,
                quantity=cart_item.quantity,
                price_at_order=cart_item.foodItem.price
            )
            for cart_item in cart.items
        ]

        order = Order(
            id=str(uuid.uuid4()),
            user=user,
            restaurant=cart.restaurant,
            items=order_items,
            status=OrderStatus.PENDING,
            delivery_address=delivery_address or user.address
        )

        self.order_repo.addOrder(order)

        # checkout succeeded — clear the cart so a re-submit doesn't double-order
        self.cart_repo.delete(cart.cartId)

        return order

    def get_order(self, order_id) -> Optional[Order]:
        return self.order_repo.getById(order_id)

    def get_orders_for_user(self, user_id) -> List[Order]:
        return self.order_repo.getByUserId(user_id)

    def accept_order(self, order_id) -> Optional[Order]:
        order = self.order_repo.getById(order_id)
        if order is None:
            return None
        order.update_status(OrderStatus.ACCEPTED)
        self.order_repo.update(order)
        return order

    def cancel_order(self, order_id) -> Optional[Order]:
        order = self.order_repo.getById(order_id)
        if order is None:
            return None
        if order.status in (OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DELIVERED):
            raise ValueError(f"Cannot cancel an order in status {order.status}")
        order.update_status(OrderStatus.CANCELLED)
        self.order_repo.update(order)
        return order

    def update_order_status(self, order_id, status: OrderStatus) -> Optional[Order]:
        order = self.order_repo.getById(order_id)
        if order is None:
            return None
        order.update_status(status)
        self.order_repo.update(order)
        return order


class DeliveryService:
    """
    Owns delivery-partner assignment and status transitions. Kept separate
    from OrderService: matching/assignment policy is a different concern
    from order lifecycle, even though the two collaborate (order accepted
    -> triggers a partner search).
    """
    def __init__(self, partner_repo: IDeliveryPartnerRepository, order_repo: IOrderRepository):
        self.partner_repo = partner_repo
        self.order_repo = order_repo

    def assign_partner_to_order(self, order_id, search_radius_km: float = 5.0) -> Optional[Order]:
        order = self.order_repo.getById(order_id)
        if order is None:
            return None

        candidates = self.partner_repo.getAvailableNear(
            order.restaurant.lat, order.restaurant.long, search_radius_km
        )
        if not candidates:
            return None  # no partner available right now — caller decides retry policy

        # naive nearest-first policy; swap for load-balanced/round-robin later if needed
        chosen = min(
            candidates,
            key=lambda p: _distance(order.restaurant.lat, order.restaurant.long, p.lat, p.long)
        )

        order.assign_partner(chosen)
        order.update_status(OrderStatus.OUT_FOR_DELIVERY)
        self.order_repo.update(order)

        self.partner_repo.updateStatus(chosen.delId, DeliveryPartnerStatus.BUSY)

        return order

    def mark_delivered(self, order_id) -> Optional[Order]:
        order = self.order_repo.getById(order_id)
        if order is None:
            return None

        order.update_status(OrderStatus.DELIVERED)
        self.order_repo.update(order)

        if order.deliveryPartner:
            self.partner_repo.updateStatus(order.deliveryPartner.delId, DeliveryPartnerStatus.AVAILABLE)

        return order


class RestaurantService:
    def __init__(self, restaurant_repo: IRestaurantRepository):
        self.restaurant_repo = restaurant_repo

    def add_restaurant(self, restaurant: Restaurant) -> None:
        self.restaurant_repo.addRestaurant(restaurant)

    def get_restaurant(self, restaurant_id) -> Optional[Restaurant]:
        return self.restaurant_repo.getById(restaurant_id)

    def search_by_name(self, name: str) -> List[Restaurant]:
        return self.restaurant_repo.getRestaurantByName(name)

    def search_by_food(self, food_name: str) -> List[Restaurant]:
        return self.restaurant_repo.getRestaurantByFoodItem(food_name)


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def register_user(self, name, email, address: Address) -> User:
        existing = self.user_repo.getByEmail(email)
        if existing:
            raise ValueError(f"User with email {email} already exists")
        user = User(id=str(uuid.uuid4()), name=name, email=email, address=address)
        self.user_repo.addUser(user)
        return user

    def get_user(self, user_id) -> Optional[User]:
        return self.user_repo.getById(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.getByEmail(email)