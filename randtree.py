#!/usr/bin/env python

import random

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        result = [f"Node({self.value}"]
        if self.left:
            result.append(f", left={self.left!r}")
        if self.right:
            result.append(f", right={self.right!r}")
        result.append(")")
        return "".join(result)

    def insert(self, value):
        if value < self.value:
            if self.left is None:
                self.left = Node(value)
            else:
                self.left.insert(value)
        elif value > self.value:
            if self.right is None:
                self.right = Node(value)
            else:
                self.right.insert(value)


def random_tree(lower, upper, probability):
    print(f"l={lower} u={upper} p={probability}")
    r = random.random()
    if r > probability:
        print(f"{r}")
        return None
    if upper < lower:
        return None
    value = random.randint(lower, upper)
    print(f"{value}")
    left = random_tree(lower, value-1, probability)
    right = random_tree(value+1, upper, probability)
    return Node(value, left, right)


def random_tree2(lower, upper, count):
    print(f"l={lower} u={upper} c={count}")
    tree = None
    for value in random.sample(range(lower, upper+1), count):
        if tree is None:
            tree = Node(value)
        else:
            tree.insert(value)
    return tree


def print_tree(tree):

    def p(n, depth, connector):
        if n is None:
            return
        indent = "    " * depth
        p(n.left, depth + 1,  r"/--")
        print(f"{indent}{connector}{n.value}")
        p(n.right, depth + 1, r"\--")

    p(tree, 0, "")


tree = random_tree2(1, 32, 10)
print(tree)
print_tree(tree)

