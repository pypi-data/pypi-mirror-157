from __future__ import annotations
import typing as t


class Node:
    def __init__(self, val, next_: t.Optional[Node] = None) -> Node:
        self.val = val
        self.next_ = next_

    def __str__(self) -> str:
        return f'Node(val={self.val}), next=>{self.next_}'
