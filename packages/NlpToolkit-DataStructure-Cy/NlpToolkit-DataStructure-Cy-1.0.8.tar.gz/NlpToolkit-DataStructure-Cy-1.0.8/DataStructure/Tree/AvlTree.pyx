from typing import Callable

from DataStructure.Stack cimport Stack


cdef class AvlTree(Tree):

    def __init__(self, comparator: Callable[[object, object], int]):
        super().__init__(comparator)

    cpdef int height(self, AvlTreeNode d):
        if d is None:
            return 0
        else:
            return d.height

    cpdef AvlTreeNode rotateLeft(self, AvlTreeNode k2):
        cdef AvlTreeNode k1
        k1 = k2.left
        k2.left = k1.right
        k1.right = k2
        k2.height = max(self.height(k2.left), self.height(k2.right)) + 1
        k1.height = max(self.height(k1.left), AvlTreeNode(k1.right).height) + 1
        return k1

    cpdef AvlTreeNode rotateRight(self, AvlTreeNode k1):
        cdef AvlTreeNode k2
        k2 = k1.right
        k1.right = k2.left
        k2.left = k1
        k2.height = max(AvlTreeNode(k2.left).height, self.height(k2.right)) + 1
        k1.height = max(self.height(k1.left), self.height(k1.right)) + 1
        return k2

    cpdef doubleRotateLeft(self, AvlTreeNode k3):
        k3.left = self.rotateRight(k3.left)
        return self.rotateLeft(k3)

    cpdef doubleRotateRight(self, AvlTreeNode k1):
        k1.right = self.rotateLeft(k1.right)
        return self.rotateRight(k1)

    cpdef insertTree(self, AvlTreeNode node):
        cdef AvlTreeNode x
        cdef AvlTreeNode y
        cdef AvlTreeNode t
        cdef int LEFT, RIGHT, dir1, dir2
        cdef Stack c
        LEFT = 1
        RIGHT = 2
        y = None
        x = self.root
        dir1 = 0
        dir2 = 0
        c = Stack()
        while x is not None:
            y = x
            c.push(y)
            dir1 = dir2
            if self.comparator(node.data, x.data) < 0:
                x = x.left
                dir2 = LEFT
            else:
                x = x.right
                dir2 = RIGHT
        self.insertChild(y, node)
        while not c.isEmpty():
            x = c.pop()
            x.height = max(self.height(x.left), self.height(x.right)) + 1
            if abs(self.height(x.left) - self.height(x.right)) == 2:
                if dir1 == LEFT:
                    if dir2 == LEFT:
                        t = self.rotateLeft(x)
                    else:
                        t = self.doubleRotateLeft(x)
                else:
                    if dir2 == LEFT:
                        t = self.doubleRotateRight(x)
                    else:
                        t = self.rotateRight(x)
                y = c.pop()
                self.insertChild(y, t)
                break

    cpdef insertData(self, object data):
        self.insertTree(AvlTreeNode(data))
