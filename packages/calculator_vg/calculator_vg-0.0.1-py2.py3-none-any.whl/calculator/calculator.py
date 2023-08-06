"""This module contains class `Calculator` which performs basic mathematical
operations.
"""


class Calculator:
    """Class which works as a simple calculator.

    The class performs basic math operations with the value of attribute
    `.result` (its initial value is 0), and saves the result as a new value
    of `.result`.

    To reset `.result` value to 0, use `.reset()` method.

    Examples
    --------
    >>> calculator = Calculator()
    >>> print(calculator.result)
    0.0
    >>> calculator.add(100)
    >>> print(calculator.result)
    100.0
    >>> calculator.sqrt()
    >>> print(calculator.result)
    10.0
    >>> calculator.reset()
    >>> print(calculator.result)
    0.0
    """

    def __init__(self) -> None:
        """Initialize class 'Calculator'."""
        self.result = 0.0

    def add(self, value: float) -> None:
        """Addition.

        Add `value` to `.result` and save the result as `.result`.

        ```
        .result = .result + value
        ```

        Parameters
        ----------
        value: float :
            The value that is added to `.result`.

        Returns
        -------
        Noting. Updates the value of attribute `.result` with the result
        of performed mathematical operation.

        Examples
        --------
        >>> calculator = Calculator()
        >>> calculator.add(100)
        >>> print(calculator.result)
        100.0
        >>> calculator.add(6)
        >>> print(calculator.result)
        106.0
        """
        self.result += value

    def subtract(self, value: float) -> None:
        """Subtraction.

        From `.result` subtract `value` and save the result as `.result`.
        ```
        .result = .result - value
        ```

        Parameters
        ----------
        value: float :
            The value that is subtracted from `.result`.

        Returns
        -------
        Noting. Updates the value of attribute `.result` with the result
        of performed mathematical operation.

        Examples
        --------
        >>> calculator = Calculator()
        >>> calculator.subtract(100)
        >>> print(calculator.result)
        -100.0
        >>> calculator.subtract(6)
        >>> print(calculator.result)
        -106.0
        """
        self.result -= value

    def multiply_by(self, value: float) -> None:
        """Scalar multiplication.

        Multiply `.result` by `value` and save the result as `.result`.

        Parameters
        ----------
        value: float :
            The value that `.result` is multiplied by.
        ```
        .result = .result * value
        ```

        Returns
        -------
        Noting. Updates the value of attribute `.result` with the result
        of performed mathematical operation.

        Examples
        --------
        >>> calculator = Calculator()
        >>> calculator.reset(to=100)
        >>> calculator.multiply_by(2)
        >>> calculator.result
        200.0
        """
        self.result *= value

    def divide_by(self, value: float) -> None:
        """Division.

        Divide  `.result` by `value` and save the result as `.result`.
        ```
        .result = .result / value
        ```

        Parameters
        ----------
        value: float :
            Divisor.

        Returns
        -------
        Noting. Updates the value of attribute `.result` with the result
        of performed mathematical operation.

        Examples
        --------
        >>> calculator = Calculator()
        >>> calculator.reset(to=100)
        >>> calculator.divide_by(2)
        >>> calculator.result
        50.0

        """
        self.result /= value

    def exponentiate(self, n: float) -> None:
        """Exponentiation.

        Exponentiate `.result` by `n` (`.result^n`, or in Python `.result**n`)
        and save the result as `.result`.
        ```
        .result = .result ** n
        ```

        Parameters
        ----------
        n: float :
            exponent

        Returns
        -------
        Noting. Updates the value of attribute `.result` with the result
        of performed mathematical operation.

        Examples
        --------
        >>> calculator = Calculator()
        >>> calculator.reset(to=10)
        >>> calculator.exponentiate(2)
        >>> calculator.result
        100.0
        """
        self.result = self.result**n

    def take_n_root(self, n: float = 2) -> None:
        """Take n-th root.

        Take n-th root of attribute.

        Parameters
        ----------
        n: float :
             Degree of the root.
             (Default value = 2)

        Returns
        -------
        Noting. Updates the value of attribute `.result` with the result
        of performed mathematical operation.

        Examples
        --------
        >>> calculator = Calculator()
        >>> calculator.reset(to=1000)
        >>> calculator.take_n_root(3)
        >>> calculator.result
        9.999999999999998

        # 9.999999999999998 is an approximate result of 10.0
        """
        self.result = self.result ** (1 / n)

    def sqrt(self) -> None:
        """Square root.

        Takes a square root of attribute `.result` and updates its value with
        the result of mathematical operation. It is a convenience method
        wrapped around `.take_n_root()` with value `n=2`.

        Examples
        --------
        >>> calculator = Calculator()
        >>> calculator.reset(to=10000)
        >>> calculator.sqrt()
        >>> calculator.result
        100.0
        """
        self.take_n_root(n=2)

    def reset(self, to: float = 0.0) -> None:
        """Reset the value of attribute `.result`.

        By default, the value is reset to 0.

        Parameters
        ----------
        to: float :
             New value of attribute `.result`.
             (Default value = 0.0)

        Returns
        -------
        Noting. Updates the value of attribute `.result` to 0 (default) or
        other numeric value provided by user.

        Examples
        --------
        >>> calculator = Calculator()
        >>> calculator.reset(to=10000)
        >>> print(calculator.result)
        10000.0
        >>> calculator.reset()
        >>> print(calculator.result)
        0.0
        """
        if not isinstance(to, (int, float)):
            raise TypeError(f"`to` must be int of float, but is {type(to)}")

        self.result = float(to)


if __name__ == "__main__":
    import doctest

    print(doctest.testmod())
