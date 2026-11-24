"""Deterministic primary-secondary inventory replication demonstration."""

from collections import deque
from dataclasses import dataclass


@dataclass
class Replica:
    """A replica holding the current inventory value."""

    name: str
    stock: int

    def read(self) -> int:
        return self.stock

    def write(self, stock: int) -> None:
        self.stock = stock


class InventorySystem:
    """Model primary writes and queued asynchronous replication."""

    def __init__(self, initial_stock: int) -> None:
        self.primary = Replica("Primary", initial_stock)
        self.secondary = Replica("Secondary", initial_stock)
        self.replication_paused = False
        self.pending_updates: deque[int] = deque()

    def write_primary(self, stock: int) -> None:
        """Write on the primary, then replicate or queue the update."""
        self.primary.write(stock)
        if self.replication_paused:
            self.pending_updates.append(stock)
        else:
            self.secondary.write(stock)

    def pause_replication(self) -> None:
        self.replication_paused = True

    def resume_replication(self) -> None:
        """Deliver queued writes in order and resume normal replication."""
        self.replication_paused = False
        while self.pending_updates:
            self.secondary.write(self.pending_updates.popleft())

    def read(self, replica_name: str) -> int:
        if replica_name == "Primary":
            return self.primary.read()
        if replica_name == "Secondary":
            return self.secondary.read()
        raise ValueError(f"Unknown replica: {replica_name}")


def show_reads(system: InventorySystem, label: str) -> None:
    print(
        f"{label}: client reads Primary={system.read('Primary')}, "
        f"Secondary={system.read('Secondary')}"
    )


def main() -> None:
    system = InventorySystem(initial_stock=10)
    print("Initial inventory: Primary=10, Secondary=10")

    print("\n1. Normal replication")
    system.write_primary(12)
    print(f"Primary receives stock=12; Secondary receives stock={system.secondary.stock}")
    show_reads(system, "After replication")
    assert system.read("Primary") == system.read("Secondary") == 12

    # Restore the requested baseline before the stale-read demonstration.
    system.write_primary(10)
    print("\nReset baseline: Primary and Secondary both return stock=10")
    assert system.read("Primary") == system.read("Secondary") == 10

    print("\n2. Stale read while replication is delayed")
    system.pause_replication()
    system.write_primary(9)
    show_reads(system, "Replication paused")
    assert system.read("Primary") == 9
    assert system.read("Secondary") == 10
    print("The Secondary's value is stale because it has not received the queued write.")

    print("\n3. Recovery and convergence")
    system.resume_replication()
    show_reads(system, "After replication resumes")
    assert system.read("Primary") == system.read("Secondary") == 9
    print("Converged: both replicas return stock=9")


if __name__ == "__main__":
    main()
