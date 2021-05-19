from abc import abstractmethod
from typing import TypeVar, Generic, Optional, Protocol

T = TypeVar('T', bound='Orderable', contravariant=True)

class Orderable(Protocol[T]):
    @abstractmethod
    def __lt__(self: T, other: T) -> bool:
        pass

class Node(Generic[T]):
    value: T
    left: Optional['Node']
    right: Optional['Node']

    def __init__(self, value: T, left: 'Node' = None, right: 'Node' = None):
        self.value = value
        self.left = left
        self.right = right

    def insert(self, value: T) -> None:
        if value < self.value:
            if self.left is None:
                self.left = Node(value)
            else:
                self.left.insert(value)
        elif self.value < value:
            if self.right is None:
                self.right = Node(value)
            else:
                self.right.insert(value)
