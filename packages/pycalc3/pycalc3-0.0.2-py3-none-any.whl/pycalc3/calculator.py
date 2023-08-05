"""Calculator class implementation."""


class Calculator:
    """Calculator class for applying basic math operations on \
            internal memory.

    Usage:

        >>> cal = Calculator()
        >>> cal.add(12)
        >>> cal.memory_value
        12.0
        >>> cal.subtract(3)
        >>> cal.memory_value
        9.0
        >>> cal.multiply(3)
        >>> cal.memory_value
        27.0
        >>> cal.divide(3)
        >>> cal.memory_value
        9.0
        >>> cal.root(2)
        >>> cal.memory_value
        3.0
        >>> cal.reset()
        >>> cal.memory_value
        0.0
    """

    def __init__(self) -> None:
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

        if real_number != 0:
            self.memory_value /= real_number

    def root(self, real_number: float) -> None:
        """Math operation for taking (n) root of a number."""

        if self.memory_value != 0 and real_number != 0:

            self.memory_value **= 1 / real_number

    def reset(self) -> None:
        """Reseting internal memory to 0."""

        self.memory_value = 0.0
