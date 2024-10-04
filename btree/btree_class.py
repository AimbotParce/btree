import math
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, Union

import more_itertools as mit

T = TypeVar("T")


@dataclass
class BTreeNode(Generic[T]):
    children: list[Union["BTreeNode[T]", "BTreeLeaf[T]"]] = field(default_factory=list)
    indexes: list[float] = field(default_factory=list)

    capacity: int | None = field(default=None)  # Only for representation

    def getNextNode(self, index: float):
        if index < self.indexes[0]:
            return self.children[0]
        for j, other in enumerate(self.indexes):
            if index >= other:
                return self.children[j + 1]
        raise ValueError("How did we get here?")

    def __str__(self):
        if self.capacity is None:
            return f"BTreeNode(indexes={self.indexes})"
        else:
            indexes = self.indexes.copy()
            indexes.extend(["NA" for _ in range(self.capacity - len(indexes))])
            return f"BTreeNode(indexes={indexes})"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class BTreeLeaf(Generic[T]):
    indexes: list[float]
    values: list[T]

    next_leaf: Union["BTreeLeaf", None] = field(default=None)
    prev_leaf: Union["BTreeLeaf", None] = field(default=None)

    capacity: int | None = field(default=None)  # Only for representation

    def getNextNode(self, index: float) -> None:
        raise ValueError("BTreeLeaf does not have children nodes.")

    def getValue(self, index: float) -> T:
        for other, value in zip(self.indexes, self.values):
            if index == other:
                return value
        raise ValueError("How did we get here?")

    def __str__(self) -> str:
        if self.capacity is None:
            return f"BTreeLeaf(indexes={self.indexes})"
        else:
            indexes = self.indexes.copy()
            indexes.extend(["NA" for _ in range(self.capacity - len(indexes))])
            return f"BTreeLeaf(indexes={indexes})"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class BTree(Generic[T]):
    root: BTreeNode[T] | BTreeLeaf[T]
    order: int
    load: int

    def find(self, index: float) -> Any:
        node = self.root

        while not isinstance(node, BTreeLeaf):
            node = node.getNextNode(index)

        return node.getValue(index)

    @classmethod
    def build(cls, indexed_list: list[tuple[float, T]], order: int, load: float):
        if not isinstance(order, int) or not order >= 1:
            raise TypeError("order must be an integer and >= 1")
        if not 0 < load <= 1:
            raise ValueError("load must be between 0 and 1")

        sorted_list = sorted(indexed_list, key=lambda x: x[0])
        max_data_per_bucket = math.floor(2 * order * load)

        leaves: list[BTreeLeaf] = []

        current_index_bucket = []
        current_value_bucket = []
        for index, value in sorted_list:
            current_index_bucket.append(index)
            current_value_bucket.append(value)
            if len(current_index_bucket) >= max_data_per_bucket:
                prev = leaves[-1] if leaves else None
                leaf = BTreeLeaf(
                    indexes=current_index_bucket, values=current_value_bucket, prev_leaf=prev, capacity=2 * order
                )
                if prev is not None:
                    prev.next_leaf = leaf
                leaves.append(leaf)
                current_index_bucket = []
                current_value_bucket = []

        to_join = leaves
        min_indices: dict[BTreeLeaf | BTreeNode, float] = {id(l): l.indexes[0] for l in leaves}
        iteration = 0
        while len(to_join) > 1:
            new_nodes = []
            edge_count = math.ceil(len(to_join) / (max_data_per_bucket + 1))
            children_count = math.ceil(len(to_join) / edge_count)
            if iteration % 2 == 0:  # Its too late, I slept 4.5h last night and I cannot think of a better way
                # of avoiding having a side too heavy.
                to_join = reversed(to_join)
            for children in mit.batched(to_join, n=children_count, strict=False):
                if iteration % 2 == 0:
                    children = list(reversed(children))
                if len(children) == 1:
                    new_nodes.append(children[0])
                else:
                    indexes = []
                    for j, c in enumerate(children):
                        if j == 0:
                            min_children_node_index = min_indices[id(c)]
                        else:
                            indexes.append(min_indices[id(c)])
                    node = BTreeNode(children=children, indexes=indexes, capacity=2 * order)
                    min_indices[id(node)] = min_children_node_index
                    new_nodes.append(node)

            if iteration % 2 == 0:
                new_nodes = list(reversed(new_nodes))
            to_join = new_nodes

            iteration += 1

        return cls(root=to_join[0], order=order, load=load)
