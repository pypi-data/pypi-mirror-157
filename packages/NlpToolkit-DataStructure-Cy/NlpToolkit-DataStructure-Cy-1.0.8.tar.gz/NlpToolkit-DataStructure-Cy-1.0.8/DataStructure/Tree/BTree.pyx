from typing import Callable

cdef class BTree:

    def __init__(self, d: int, comparator: Callable[[object, object], int]):
        self.comparator = comparator
        self.d = d
        self.root = None

    cpdef BTreeNode search(self, object value):
        cdef BTreeNode b
        cdef int child
        b = self.root
        while not b.leaf:
            child = b.position(value, self.comparator)
            if child < b.m and b.K[child] == value:
                return b
            b = b.children[child]
        child = b.position(value, self.comparator)
        if child < b.m and b.K[child] == value:
            return b
        return None

    cpdef insertData(self, object data):
        cdef BTreeNode s
        cdef BTreeNode root
        if self.root is None:
            self.root = BTreeNode(self.d)
        if self.root.leaf:
            s = self.root.insertLeaf(data, self.comparator)
            if s is not None:
                tmp = self.root
                self.root = BTreeNode(self.d, tmp, s, tmp.K[self.d])
        else:
            s = self.root.insertNode(data, self.comparator, True)
            if s is not None:
                self.root = s
