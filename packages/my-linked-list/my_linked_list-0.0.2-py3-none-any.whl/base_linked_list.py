from abc import ABC
import typing as t

from src.nodes import Node


class BaseLinkedList(ABC):
    _head: t.Optional[Node] = None
    _tail: t.Optional[Node] = None
    _nodes = 0

    def __init__(self, val):
        node = Node(val)
        self._head = node
        self._tail = node
        self._nodes += 1

    def _prepend(self, val):
        node = Node(val, self._head)
        self._head = node
        self._nodes += 1

    def _append(self, val):
        node = Node(val)
        self._tail.next_ = node
        self._tail = node
        self._nodes += 1

    def _lookup(self, val) -> t.Optional[int]:
        node = self._head
        idx = 0
        while idx != self._nodes:
            if node is None:
                break
            if node.val == val:
                return idx
            idx += 1
            node = node.next_

    def _insert(self, idx: int, val):
        if abs(idx) > self._nodes:
            raise IndexError
        if idx == 0:
            self._prepend(val)
        else:
            node = self._head
            current_idx = 0
            while current_idx != self._nodes:
                if current_idx == idx - 1:
                    new_node = Node(val, node.next_)
                    node.next_ = new_node
                    break
                current_idx += 1
                node = node.next_
        self._nodes += 1

    def _del_head(self):
        self._head = self._head.next_
        if self._head is None:
            self._tail = self._head

    def _check_tail(self, node: Node, next_: Node):
        if next_ is self._tail:
            self._tail = node

    def _del_eny_node(self, idx: int):
        node = self._head
        current_idx = 0
        while current_idx != self._nodes:
            if current_idx == idx - 1:
                deleted_node = node.next_
                self._check_tail(node, deleted_node)
                node.next_ = deleted_node.next_
                break
            current_idx += 1
            node = node.next_

    def _delete(self, idx: int):
        if idx < 0 or idx > self._nodes:
            raise IndexError
        if idx == 0:
            self._del_head()
        else:
            self._del_eny_node(idx)
        self._nodes -= 1

    def _iter(self):
        node = self._head
        while node is not None:
            yield node
            node = node.next_

    @property
    def head(self):
        return self._head

    @property
    def tail(self):
        return self._tail

    def __iter__(self):
        return self._iter()
