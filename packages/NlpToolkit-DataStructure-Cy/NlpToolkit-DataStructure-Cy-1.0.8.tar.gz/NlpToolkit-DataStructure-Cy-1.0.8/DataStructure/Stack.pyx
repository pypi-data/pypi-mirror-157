cdef class Stack:

    def __init__(self):
        self.__stack = []

    cpdef push(self, object item):
        self.__stack.append(item)

    cpdef object pop(self):
        if len(self.__stack) > 0:
            return self.__stack.pop()
        else:
            return None

    cpdef bint isEmpty(self):
        return len(self.__stack) == 0
