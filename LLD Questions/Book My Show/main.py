"""
Movie Booking System - LLD Demo
Entities + Repositories + Services (Search, Booking, Payment)
"""

import threading
import time
import uuid
import random
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SeatType(Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    RECLINER = "RECLINER"


class SeatStatus(Enum):
    AVAILABLE = "AVAILABLE"
    LOCKED = "LOCKED"
    BOOKED = "BOOKED"


class BookingStatus(Enum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


# ---------------------------------------------------------------------------
# Core Entities
# ---------------------------------------------------------------------------

class Movie:
    def __init__(self, id, title, duration, language, genre, cast, releaseDate):
        self.id = id
        self.title = title
        self.duration = duration
        self.language = language
        self.genre = genre
        self.cast = cast
        self.releaseDate = releaseDate


class Theatre:
    def __init__(self, id, name, city):
        self.id = id
        self.name = name
        self.city = city


class Screen:
    def __init__(self, id, theatre: Theatre, screenNumber: int, totalSeats: int):
        self.id = id
        self.theatre = theatre
        self.screenNumber = screenNumber
        self.totalSeats = totalSeats


class Seat:
    def __init__(self, id, screen: Screen, row, seatNumber, seatType: SeatType):
        self.id = id
        self.screen = screen
        self.row = row
        self.seatNumber = seatNumber
        self.seatType = seatType


class Show:
    def __init__(self, id, movie: Movie, screen: Screen, startTime: datetime,
                 endTime: datetime, basePrice: float):
        self.id = id
        self.movie = movie
        self.screen = screen
        self.startTime = startTime
        self.endTime = endTime
        self.basePrice = basePrice


class ShowSeat:
    def __init__(self, id, show: Show, seat: Seat, status: SeatStatus, price: float):
        self.id = id
        self.show = show
        self.seat = seat
        self.status = status
        self.price = price


class User:
    def __init__(self, id, name, email, phone):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone


class Booking:
    def __init__(self, id, user: User, show: Show, showSeats: list,
                 bookingStatus: BookingStatus, totalAmount: float, createdAt: float):
        self.id = id
        self.user = user
        self.show = show
        self.showSeats = showSeats          # list[ShowSeat]
        self.bookingStatus = bookingStatus
        self.totalAmount = totalAmount
        self.createdAt = createdAt


class Payment:
    def __init__(self, id, booking: Booking, amount, status: PaymentStatus, paymentMode):
        self.id = id
        self.booking = booking
        self.amount = amount
        self.status = status
        self.paymentMode = paymentMode


# ---------------------------------------------------------------------------
# Repositories (in-memory, would be DB-backed in a real system)
# ---------------------------------------------------------------------------

class MovieRepository:
    def __init__(self):
        self._movies = {}

    def add(self, movie: Movie):
        self._movies[movie.id] = movie

    def getById(self, movieId):
        return self._movies.get(movieId)

    def getAll(self):
        return list(self._movies.values())


class ShowRepository:
    def __init__(self):
        self._shows = {}

    def add(self, show: Show):
        self._shows[show.id] = show

    def getById(self, showId):
        return self._shows.get(showId)

    def getAll(self):
        return list(self._shows.values())


class ShowSeatRepository:
    def __init__(self):
        self._showSeats = {}

    def add(self, showSeat: ShowSeat):
        self._showSeats[showSeat.id] = showSeat

    def getById(self, showSeatId):
        return self._showSeats.get(showSeatId)

    def getByShow(self, showId):
        return [ss for ss in self._showSeats.values() if ss.show.id == showId]


class BookingRepository:
    def __init__(self):
        self._bookings = {}

    def save(self, booking: Booking):
        self._bookings[booking.id] = booking

    def getById(self, bookingId):
        return self._bookings.get(bookingId)


class PaymentRepository:
    def __init__(self):
        self._payments = {}

    def save(self, payment: Payment):
        self._payments[payment.id] = payment

    def getById(self, paymentId):
        return self._payments.get(paymentId)


# ---------------------------------------------------------------------------
# Payment Strategies - Used Strategy Pattern
# ---------------------------------------------------------------------------

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass


class CardPaymentStrategy(PaymentStrategy):
    def __init__(self, cardNumber, cvv, expiry):
        self.cardNumber = cardNumber
        self.cvv = cvv
        self.expiry = expiry

    def pay(self, amount: float) -> bool:
        print(f"  [Gateway] Charging Rs.{amount} to card ending {self.cardNumber[-4:]}")
        return random.random() > 0.1


class UpiPaymentStrategy(PaymentStrategy):
    def __init__(self, upiId):
        self.upiId = upiId

    def pay(self, amount: float) -> bool:
        print(f"  [Gateway] Charging Rs.{amount} via UPI {self.upiId}")
        return random.random() > 0.1


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

class SearchService:
    def __init__(self, movieRepo: MovieRepository, showRepo: ShowRepository):
        self.movieRepo = movieRepo
        self.showRepo = showRepo

    def searchMoviesByCity(self, city: str) -> list:
        matchingShows = [s for s in self.showRepo.getAll() if s.screen.theatre.city == city]
        movieIds = {s.movie.id for s in matchingShows}
        return [m for m in self.movieRepo.getAll() if m.id in movieIds]

    def searchShows(self, movieId: str, city: str, onDate) -> list:
        return [
            s for s in self.showRepo.getAll()
            if s.movie.id == movieId
            and s.screen.theatre.city == city
            and s.startTime.date() == onDate
        ]


class PaymentService:
    def __init__(self, paymentRepo: PaymentRepository):
        self.paymentRepo = paymentRepo

    def processPayment(self, booking: Booking, strategy: PaymentStrategy) -> Payment:
        payment = Payment(
            id=str(uuid.uuid4()),
            booking=booking,
            amount=booking.totalAmount,
            status=PaymentStatus.PENDING,
            paymentMode=type(strategy).__name__
        )
        try:
            success = strategy.pay(booking.totalAmount)
            payment.status = PaymentStatus.SUCCESS if success else PaymentStatus.FAILED
        except Exception as e:
            print(f"  [Gateway Error] {e}")
            payment.status = PaymentStatus.FAILED

        self.paymentRepo.save(payment)
        return payment


class BookingService:
    def __init__(self, showSeatRepo: ShowSeatRepository, bookingRepo: BookingRepository,
                 paymentService: PaymentService, lockTimeoutSeconds=300):
        self.showSeatRepo = showSeatRepo
        self.bookingRepo = bookingRepo
        self.paymentService = paymentService
        self.lockTimeoutSeconds = lockTimeoutSeconds
        self._seatLocks = {}
        self._globalLock = threading.Lock()

    def _getSeatLock(self, showSeatId):
        with self._globalLock:
            if showSeatId not in self._seatLocks:
                self._seatLocks[showSeatId] = threading.Lock()
            return self._seatLocks[showSeatId]

    def lockSeats(self, showSeatIds: list, user: User) -> Booking:
        acquired = []
        try:
            for showSeatId in showSeatIds:
                lock = self._getSeatLock(showSeatId)
                if not lock.acquire(timeout=2):
                    raise Exception(f"Seat {showSeatId} is being processed, try again")
                acquired.append(lock)

                showSeat = self.showSeatRepo.getById(showSeatId)
                if showSeat.status != SeatStatus.AVAILABLE:
                    raise Exception(f"Seat {showSeatId} is not available")
                showSeat.status = SeatStatus.LOCKED

            showSeats = [self.showSeatRepo.getById(sid) for sid in showSeatIds]
            booking = Booking(
                id=str(uuid.uuid4()),
                user=user,
                show=showSeats[0].show,
                showSeats=showSeats,
                bookingStatus=BookingStatus.CREATED,
                totalAmount=sum(ss.price for ss in showSeats),
                createdAt=time.time()
            )
            self.bookingRepo.save(booking)

            timer = threading.Timer(self.lockTimeoutSeconds, self._expireBookingIfUnpaid, args=[booking.id])
            timer.daemon = True
            timer.start()

            return booking

        except Exception as e:
            self._releaseSeats(showSeatIds)
            raise e
        finally:
            for lock in acquired:
                lock.release()

    def confirmBooking(self, bookingId, paymentStrategy: PaymentStrategy) -> Booking:
        booking = self.bookingRepo.getById(bookingId)
        if booking.bookingStatus != BookingStatus.CREATED:
            raise Exception("Booking is not in a payable state")

        payment = self.paymentService.processPayment(booking, paymentStrategy)

        if payment.status == PaymentStatus.SUCCESS:
            for showSeat in booking.showSeats:
                showSeat.status = SeatStatus.BOOKED
            booking.bookingStatus = BookingStatus.CONFIRMED
        else:
            self._releaseSeats([s.id for s in booking.showSeats])
            booking.bookingStatus = BookingStatus.CANCELLED

        self.bookingRepo.save(booking)
        return booking

    def _releaseSeats(self, showSeatIds):
        for showSeatId in showSeatIds:
            showSeat = self.showSeatRepo.getById(showSeatId)
            if showSeat and showSeat.status == SeatStatus.LOCKED:
                showSeat.status = SeatStatus.AVAILABLE

    def _expireBookingIfUnpaid(self, bookingId):
        booking = self.bookingRepo.getById(bookingId)
        if booking and booking.bookingStatus == BookingStatus.CREATED:
            self._releaseSeats([s.id for s in booking.showSeats])
            booking.bookingStatus = BookingStatus.EXPIRED
            self.bookingRepo.save(booking)
            print(f"  [System] Booking {bookingId} expired due to non-payment")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    # --- Repositories ---
    movieRepo = MovieRepository()
    showRepo = ShowRepository()
    showSeatRepo = ShowSeatRepository()
    bookingRepo = BookingRepository()
    paymentRepo = PaymentRepository()

    # --- Seed data ---
    movie = Movie(
        id="M1", title="Inception 2", duration=150, language="English",
        genre="Sci-Fi", cast=["Leo D", "Tom H"], releaseDate="2026-01-01"
    )
    movieRepo.add(movie)

    theatre = Theatre(id="T1", name="PVR Forum Mall", city="Bengaluru")
    screen = Screen(id="S1", theatre=theatre, screenNumber=3, totalSeats=4)

    show = Show(
        id="SH1", movie=movie, screen=screen,
        startTime=datetime(2026, 8, 1, 18, 0),
        endTime=datetime(2026, 8, 1, 20, 30),
        basePrice=250.0
    )
    showRepo.add(show)

    # 4 seats for this show — 2 regular, 2 premium
    seatConfigs = [
        ("A1", SeatType.REGULAR, 250.0),
        ("A2", SeatType.REGULAR, 250.0),
        ("B1", SeatType.PREMIUM, 400.0),
        ("B2", SeatType.PREMIUM, 400.0),
    ]
    showSeatIds = []
    for idx, (seatNum, seatType, price) in enumerate(seatConfigs, start=1):
        seat = Seat(id=f"SEAT{idx}", screen=screen, row=seatNum[0], seatNumber=seatNum, seatType=seatType)
        showSeat = ShowSeat(id=f"SS{idx}", show=show, seat=seat, status=SeatStatus.AVAILABLE, price=price)
        showSeatRepo.add(showSeat)
        showSeatIds.append(showSeat.id)

    user = User(id="U1", name="Abhijit Deb", email="abhijit@example.com", phone="9999999999")

    # --- Services ---
    searchService = SearchService(movieRepo, showRepo)
    paymentService = PaymentService(paymentRepo)
    bookingService = BookingService(showSeatRepo, bookingRepo, paymentService, lockTimeoutSeconds=300)

    # --- 1. Search ---
    print("=== Search: movies in Bengaluru ===")
    for m in searchService.searchMoviesByCity("Bengaluru"):
        print(f"  {m.title} ({m.language}, {m.genre})")

    print("\n=== Search: shows for Inception 2 on 2026-08-01 ===")
    shows = searchService.searchShows("M1", "Bengaluru", datetime(2026, 8, 1).date())
    for s in shows:
        print(f"  Show {s.id} at {s.screen.theatre.name}, {s.startTime}")

    # --- 2. Lock seats ---
    print("\n=== Locking seats A1, B1 ===")
    booking = bookingService.lockSeats(["SS1", "SS3"], user)
    print(f"  Booking {booking.id} created, status={booking.bookingStatus.value}, amount=Rs.{booking.totalAmount}")

    # --- 3. Pay and confirm ---
    print("\n=== Confirming booking via UPI ===")
    strategy = UpiPaymentStrategy(upiId="abhijit@upi")
    confirmed = bookingService.confirmBooking(booking.id, strategy)
    print(f"  Booking {confirmed.id} final status: {confirmed.bookingStatus.value}")
    for ss in confirmed.showSeats:
        print(f"    Seat {ss.seat.seatNumber} -> {ss.status.value}")

    # --- 4. Try booking an already-booked seat ---
    print("\n=== Attempting to re-book seat A1 (should fail) ===")
    try:
        bookingService.lockSeats(["SS1"], user)
    except Exception as e:
        print(f"  Failed as expected: {e}")


if __name__ == "__main__":
    main()