"""Calculator class implementation."""

class Calculator():
    def __init__(self) -> None:
        """Calculator class for applying basic math operations on \
            internal memory.
        """
        
        self.memory_value = 0.0

    def add(self, real_number: float) -> None:
        """Math operation for addition."""

        self.memory_value += real_number

    def subtract(self, real_number: float) -> None:
        """Math operation for subtraction."""

        self.memory_value -= real_number

    def multiply(self, real_number: float) -> None:
        """Math operation for multiplication."""

        self.memory_value *= real_number

    def divide(self, real_number: float) -> None:
        """Math operation for division."""

        self.memory_value /= real_number

    def root(self, real_number: float) -> None:
        """Math operation for taking (n) root of a number."""

        self.memory_value **= (1 / real_number)

    def reset(self) -> None:
        """Reseting internal memory to 0."""

        self.memory_value = 0.0