import typing as t

from src.base_linked_list import BaseLinkedList


class LinkedList(BaseLinkedList):
    def append(self, val):
        """This method adds a value to the end of the list"""
        self._append(val)

    def prepend(self, val):
        """This method adds a value to the beginning of the list"""
        self._prepend(val)

    def lookup(self, val) -> t.Optional[int]:
        """This method finds the index of an element by value"""
        return self._lookup(val)

    def insert(self, idx: int, val):
        """This method inserts an element at a specific index, shifting the elements to the right"""
        self._insert(idx, val)

    def delete(self, idx):
        """This method removes an element by index"""
        self._delete(idx)

    def __str__(self) -> str:
        return f'LinkedList({self._head})'

    def __repr__(self) -> str:
        return f'LinkedList({self._head})'
