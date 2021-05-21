#!/usr/bin/env python

from abc import abstractmethod
import json
import random

from typing import TypeVar, Generic, Optional, Any, Protocol


T = TypeVar('T', bound='TotalOrderable', contravariant=True)


class TotalOrderable(Protocol[T]):
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

    def __repr__(self) -> str:
        result = [f"Node({self.value}"]
        if self.left:
            result.append(f", left={self.left!r}")
        if self.right:
            result.append(f", right={self.right!r}")
        result.append(")")
        return "".join(result)

    def __eq__(self, other) -> bool:
        return self.value == other.value and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash((self.value, self.left, self.right))

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
        else:
            # do nothing for ==
            pass

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = dict(value=self.value)
        if self.left:
            d['left'] = self.left.to_dict()
        if self.right:
            d['right'] = self.right.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: Optional[dict]) -> Optional['Node']:
        if d is None:
            return None
        return Node(
                value=d['value'],
                left=cls.from_dict(d.get('left')),
                right=cls.from_dict(d.get('right')))


class Tree(Generic[T]):
    root: Optional[Node[T]]

    def __init__(self, root: Optional[Node[T]] = None):
        self.root = root

    def __repr__(self) -> str:
        return f"Tree(root={self.root!r})"

    def __eq__(self, other) -> bool:
        return self.root == other.root

    def __hash__(self) -> int:
        return hash(self.root)

    def insert(self, value: T) -> None:
        if self.root is None:
            self.root = Node(value)
        else:
            self.root.insert(value)

    def to_dict(self) -> dict[str, Any]:
        if self.root is None:
            return {}
        else:
            return self.root.to_dict()

    @classmethod
    def from_dict(cls, d: Optional[dict]) -> Optional['Tree']:
        return cls(root=Node.from_dict(d) if d else None)


def n2c(n: int) -> str:
    assert 1 <= n <= 26
    return chr(ord('a') + n - 1)


def random_tree(lower: int, upper: int, probability: float) -> Tree:
    def inner(l, u) -> Optional[Node]:
        # print(f"l={l} u={u}")
        r = random.random()
        if r > probability:
            # print(f"{r}")
            return None
        if u < l:
            return None
        value = random.randint(l, u)
        # print(f"{n2c(value)}")
        left = inner(l, value-1)
        right = inner(value+1, u)
        return Node(n2c(value), left, right)
    return Tree(root=inner(lower, upper))


def random_tree2(lower: int, upper: int, count: int) -> Tree:
    # print(f"l={lower} u={upper} c={count}")
    values = random.sample(range(lower, upper+1), count)
    tree: Tree = Tree()
    for value in values:
        tree.insert(n2c(value))
    return tree


def random_tree3(lower: int, upper: int, count: int) -> Tree:
    def inner(l, u):
        nonlocal count
        # print(f"l={l} u={u} c={count}")
        if count < 0 or u < l:
            return None
        count -=1
        value = random.randint(l, u)
        # print(f"{n2c(value)}")
        if random.random() < 0.5:
            left = inner(l, value-1)
            right = inner(value+1, u)
        else:
            right = inner(value+1, u)
            left = inner(l, value-1)
        return Node(n2c(value), left, right)

    return Tree(root=inner(lower, upper))


def print_tree(tree) -> None:
    def print_node(n, depth):
        if n is None:
            return
        print_node(n.right, depth + 1)
        print(f"{' ' * 3 * depth}{n.value}")
        print_node(n.left, depth + 1)
    print_node(tree.root, 0)


def draw_tree(tree):
    x = 0
    def draw(n, depth):
        nonlocal x
        if n.left:
            yield from draw(n.left, depth+1)
        yield n, x, depth
        x += 1
        if n.right:
            yield from draw(n.right, depth+1)

    if tree.root:
        return draw(tree.root, 0)


def serialize_preorder(tree: Tree) -> list:
    seq = []

    def serialize(node):
        if node is None:
            seq.append(None)
            return
        seq.append(node.value)
        serialize(node.left)
        serialize(node.right)

    serialize(tree.root)
    return seq


def deserialize_preorder(seq: list) -> Tree:
    seq = seq[:] # copy

    def deserialize():
        value = seq.pop(0)
        if value is None:
            return None
        left = deserialize()
        right = deserialize()
        return Node(value, left, right)

    return Tree(root=deserialize())


def serialize_array_index(tree: Tree) -> list:
    end_index = 0
    array: list[Any] = [] 

    def serialize_in_order(node: Node) -> int:
        nonlocal end_index
        assert end_index == len(array)
        index = end_index
        entry = [node.value, -1, -1]
        array.append(entry)
        end_index += 1
        if node.left:
            entry[1] = serialize_in_order(node.left)
        if node.right:
            entry[2] = serialize_in_order(node.right)
        return index

    def serialize_post_order(node: Node) -> int:
        left = serialize_post_order(node.left) if node.left else -1
        right = serialize_post_order(node.right) if node.right else -1
        array.append((node.value, left, right))
        return len(array) - 1

    if tree.root:
        serialize_post_order(tree.root)
    return array


def deserialize_array_index(array: list) -> Tree:
    def deserialize_forwards() -> Tree:
        nodes = [Node(entry[0]) for entry in array]
        for node, entry in zip(nodes, array):
            if entry[1] >= 0:
                node.left = nodes[entry[1]]
            if entry[2] >= 0:
                node.right = nodes[entry[2]]
        return Tree(nodes[0] if nodes else None)

    def deserialize_backwards() -> Tree:
        nodes: list[Node] = [None] * len(array)  # type: ignore
        for i in range(len(array) - 1, -1, -1):
            entry = array[i]
            left = right = None
            if entry[1] >= 0:
                left = nodes[entry[1]]
            if entry[2] >= 0:
                right = nodes[entry[2]]
            nodes[i] = Node(entry[0], left, right)
        return Tree(nodes[0] if nodes else None)

    def deserialize_post_order() -> Tree:
        nodes: list[Node] = []
        for entry in array:
            left = nodes[entry[1]] if entry[1] >= 0 else None
            right = nodes[entry[2]] if entry[2] >= 0 else None
            node = Node(entry[0], left, right)
            nodes.append(node)
        return Tree(nodes[-1] if nodes else None)

    return deserialize_post_order()


if __name__ == '__main__':
    N = 10
    tree1 = random_tree2(1, 26, N)
    print(tree1)
    # print_tree(tree1)

    grid = [[' ' for _ in range(30)] for _ in range(12)]
    for n, x, y in draw_tree(tree1):
        print(f"v={n.value}, x={x:02d}, y={y:02d}"
              f", left={getattr(n.left, 'value', '-')}"
              f", right={getattr(n.right, 'value', '-')}")
        grid[y][x] = n.value

    for row in grid:
        line = "".join(row)
        if line.strip():
            print(line)

    seq = serialize_preorder(tree1)
    print("serialize_preorder:", seq)
    print(f"{N=}, len={len(seq)}, #None={seq.count(None)}")
    tree2 = deserialize_preorder(seq)
    print("deserialize_preorder:", tree2)
    print("preorder worked:", tree1 == tree2)

    array = serialize_array_index(tree1)
    print("serialize_array_index:", array)
    tree2 = deserialize_array_index(array)
    print("deserialize_array_index:", tree2)
    print("array_index worked:", tree1 == tree2)

    d = tree1.to_dict()
    print("to_dict:", d)
    # print(json.dumps(d, indent=4))

    tree3 = Tree.from_dict(d)
    print("from_dict:", tree3)
    print("from_dict worked:", tree1 == tree3)

    tree4: Tree = Tree()
    d = tree4.to_dict()
    print("4", d)
    tree5 = Tree.from_dict(d)
    print("empty worked:", tree4 == tree5)
