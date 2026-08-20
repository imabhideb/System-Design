# SOLID Principles

SOLID is a set of five design principles for writing maintainable, scalable, and easy-to-extend object-oriented code. Below is a quick reference for each principle, along with the context/example used to understand it.

---

## S — Single Responsibility Principle (SRP)

**Definition:** A class should have only one reason to change. Each class should be responsible for a single part of the functionality.

**Context:** An `Invoice` class was doing three unrelated jobs at once — calculating totals, generating/printing the bill, and saving it to a registry. This meant any change to *how* something was saved or printed also risked breaking the invoice calculation logic.

**Fix:** Split the class into three focused classes — `InvoiceGenerator` (handles bill generation), `Registry` (handles saving), and `Revenue` (handles revenue tracking) — each with a single, clear responsibility.

---

## O — Open/Closed Principle (OCP)

**Definition:** A class should be open for extension but closed for modification. You should be able to add new behavior without changing existing, already-tested code.

**Context:** A `DiscountCalculator` used a chain of `if/elif` statements to decide the discount based on customer type. Every time a new discount type was introduced, the existing class had to be edited directly — risking bugs in code that already worked.

**Fix:** Introduced an abstract `DiscountStrategy` base class, with each discount type (`RegularDiscount`, `SpecialDiscount`, `VIPDiscount`) as its own subclass. New discount types are added by creating new classes — the `DiscountCalculator` itself is never touched again.

---

## L — Liskov Substitution Principle (LSP)

**Definition:** Subtypes must be substitutable for their base types. Any subclass should be usable wherever its parent class is expected, without breaking correctness or behavior.

**Context:** A `Bird` base class had a `fly()` method. A `Sparrow` subclass flew fine, but an `Ostrich` subclass — which technically "is a" bird — couldn't fly, and calling `fly()` on it caused an exception. This broke the assumption that "any `Bird` can fly."

**Fix:** Restructured the hierarchy so the base class only promised a generic `move()` behavior. `FlyingBird` (with `Sparrow` under it) implements flying, while `Ostrich` implements running instead — every subclass can now be substituted safely without breaking the calling code.

---

## I — Interface Segregation Principle (ISP)

**Definition:** Clients shouldn't be forced to depend on methods they don't use. Prefer several small, specific interfaces over one large, general-purpose one.

**Context:** A single `Worker` interface forced every implementer to define both `work()` and `eat()`. This made sense for a `HumanWorker`, but a `RobotWorker` was forced to implement `eat()` even though it made no sense — leading to a method that just threw an exception.

**Fix:** Split the fat `Worker` interface into smaller, focused interfaces — `Workable` and `Eatable`. `HumanWorker` implements both, while `RobotWorker` only implements `Workable`, since eating doesn't apply to it.

---

## D — Dependency Inversion Principle (DIP)

**Definition:** High-level modules should not depend on low-level modules — both should depend on abstractions. Abstractions should not depend on details; details should depend on abstractions.

**Context:** An `InvoiceService` (high-level business logic) directly created and depended on a concrete `MySQLDatabase` class. Switching databases, or mocking the database for testing, meant editing `InvoiceService` directly.

**Fix:** Introduced an abstract `Database` interface. `MySQLDatabase` and `PostgreSQLDatabase` both implement it, and `InvoiceService` depends only on the `Database` abstraction — the actual implementation is injected from outside. This is the foundation of **dependency injection**.

---

## Summary

| Principle | One-liner |
|---|---|
| **S**RP | One class, one job |
| **O**CP | Extend behavior without modifying existing code |
| **L**SP | Subclasses must honor the parent's behavioral contract |
| **I**SP | Don't force classes to implement methods they don't need |
| **D**IP | Depend on abstractions, not concrete implementations |

Together, these principles push toward code that's loosely coupled, easy to extend, and safe to change — without breaking things that already work.