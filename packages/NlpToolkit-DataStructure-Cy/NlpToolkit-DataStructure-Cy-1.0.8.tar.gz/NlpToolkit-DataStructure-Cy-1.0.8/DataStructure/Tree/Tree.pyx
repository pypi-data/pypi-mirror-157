from typing import Callable

cdef class Tree:

    def __init__(self, comparator: Callable[[object, object], int]):
        self.comparator = comparator

    cpdef TreeNode search(self, object value):
        cdef TreeNode d
        d = self.root
        while d is not None:
            if self.comparator(d.data, value) == 0:
                return d
            else:
                if self.comparator(d.data, value) > 0:
                    d = d.left
                else:
                    d = d.right
        return None

    cpdef insertChild(self, TreeNode parent, TreeNode child):
        if parent is None:
            self.root = child
        else:
            if self.comparator(child.data, parent.data) < 0:
                parent.left = child
            else:
                parent.right = child

    cpdef insert(self, TreeNode node):
        cdef TreeNode y
        cdef TreeNode x
        y = None
        x = self.root
        while x is not None:
            y = x
            if self.comparator(node.data, x.data) < 0:
                x = x.left
            else:
                x = x.right
        self.insertChild(y, node)

    cpdef insertData(self, object data):
        self.insert(TreeNode(data))
