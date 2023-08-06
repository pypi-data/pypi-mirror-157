from typing import Generic, TypeVar
from abc import abstractmethod, ABC


T = TypeVar("T")


class A(ABC, Generic[T]):
    def process_child_method(self) -> T:
        child_return = self.child_method()
        # Some actions on the return of the method
        ...
        return child_return

    @abstractmethod
    def child_method(self) -> T:
        pass


class B(A[int]):
    def child_method(self) -> int:
        return 83


b = B()
b.process_child_method()  # None
b.child_method()
