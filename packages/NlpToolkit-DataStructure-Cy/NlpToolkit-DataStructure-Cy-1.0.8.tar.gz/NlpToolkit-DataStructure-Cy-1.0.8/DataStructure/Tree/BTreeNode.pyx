cdef class BTreeNode:

    def __init__(self, d: int, firstChild: BTreeNode = None, secondChild: BTreeNode = None, newK: object = None):
        self.d = d
        self.K = []
        self.children = []
        if firstChild is None:
            self.m = 0
            self.leaf = True
        else:
            self.leaf = False
            self.m = 1
            self.children.append(firstChild)
            self.children.append(secondChild)
            self.K.append(newK)

    cpdef int position(self, object value, object comparator):
        if self.m == 0:
            return 0
        if comparator(value, self.K[self.m - 1]) > 0:
            return  self.m
        else:
            for i in range(self.m):
                if comparator(value, self.K[i]) <= 0:
                    return i
        return -1

    cpdef insertIntoK(self, int index, object insertedK):
        if index < len(self.K):
            for i in range(self.m, index, -1):
                self.K[i] = self.K[i - 1]
            self.K[index] = insertedK
        else:
            self.K.append(insertedK)

    cpdef moveHalfOfTheKToNewNode(self, BTreeNode newNode):
        for i in range(self.d):
            newNode.K.append(self.K[i + self.d + 1])
        newNode.m = self.d

    cpdef moveHalfOfTheChildrenToNewNode(self, BTreeNode newNode):
        for i in range(self.d):
            newNode.children.append(self.children[i + self.d + 1])

    cpdef moveHalfOfTheElementsToNewNode(self, BTreeNode newNode):
        self.moveHalfOfTheKToNewNode(newNode)
        self.moveHalfOfTheChildrenToNewNode(newNode)

    cpdef BTreeNode insertNode(self, object value, object comparator, bint isRoot):
        cdef int child
        cdef BTreeNode s
        cdef BTreeNode newNode
        cdef BTreeNode a
        cdef BTreeNode childNode
        child = self.position(value, comparator)
        childNode = self.children[child]
        if not childNode.leaf:
            s = childNode.insertNode(value, comparator, False)
        else:
            s = childNode.insertLeaf(value, comparator)
        if s is None:
            return None
        self.insertIntoK(child, childNode.K[self.d])
        if self.m < 2 * self.d:
            self.children.append(s)
            self.m = self.m + 1
            return None
        else:
            newNode = BTreeNode(self.d)
            newNode.leaf = False
            self.moveHalfOfTheElementsToNewNode(newNode)
            newNode.children.append(s)
            self.m = self.d
            if isRoot:
                a = BTreeNode(self.d, self, newNode, self.K[self.d])
                return a
            else:
                return newNode

    cpdef BTreeNode insertLeaf(self, object value, object comparator):
        cdef int child
        cdef BTreeNode newNode
        child = self.position(value, comparator)
        self.insertIntoK(child, value)
        if self.m < 2 * self.d:
            self.m = self.m + 1
            return None
        else:
            newNode = BTreeNode(self.d)
            self.moveHalfOfTheKToNewNode(newNode)
            self.m = self.d
            return newNode
