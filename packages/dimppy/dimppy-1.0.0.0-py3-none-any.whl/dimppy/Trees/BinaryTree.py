class Queue:
    def __init__(self,N = 'inf'):
        self._data = [] 
        self._N = N  

    # Size of Queue
    def __len__(self):
        return len(self._data)
    # Print Queue using print function
    def __str__(self):
        if self.isEmpty():
            return "Queue is Empty!"
        s = ""
        for i in self._data:
            s += str(i) + " "
        return s
    # Check if Queue is empty
    def isEmpty(self):
        return len(self._data) == 0
    # Check if Queue is full
    def isFull(self):
        return len(self._data) == self._N

    # Insert an element to the Queue
    def enqueue(self,e):
        if self.isFull():
            print("Queue is Full!")
            return
        else:
            self._data.append(e)

    # Remove an element out of the Queue
    def dequeue(self):
        if self.isEmpty():
            print("Queue is Empty!")
            return
        else:
            return self._data.pop(0)

    # Return first element of the Queue
    def first(self):
        if self.isEmpty():
            print("Queue is Empty!")
            return
        else:
            return self._data[0]
    
    # Display the Queue
    def display(self):
        for i in self._data:
            print(i,"|",end=" ")
        print()
    
    # Delete the Queue
    def clear(self):
        self._data = []
class _Node:
    __slots__='_element','_left','_right'

    def __init__(self,element,left=None,right=None):
        self._element = element
        self._left = left
        self._right = right

class Tree:
    def __init__(self):
        self._root = None

    def makeTree(self,e,left,right):
        self._root = _Node(e,left._root,right._root)

    def inOrder(self,tRoot):
        if tRoot:
            self.inOrder(tRoot._left)
            print(tRoot._element,end=" ")
            self.inOrder(tRoot._right)
    def preOrder(self,tRoot):
        if tRoot:
            print(tRoot._element,end=" ")
            self.preOrder(tRoot._left)
            self.preOrder(tRoot._right)
    def postOrder(self,tRoot):
        if tRoot:
            self.postOrder(tRoot._left)
            self.postOrder(tRoot._right)
            print(tRoot._element,end=" ")
    def levelOrder(self):
        q = Queue()
        t = self._root
        print(t._element,end=" ")
        q.enqueue(t)
        while not q.isEmpty():
            t = q.dequeue()
            if t._left:
                print(t._left._element,end=" ")
                q.enqueue(t._left)
            if t._right:
                print(t._right._element,end=" ")
                q.enqueue(t._right)
        
    def count(self,tRoot):
        if tRoot:
            x = self.count(tRoot._left)   
            y = self.count(tRoot._right)   
            return x+y+1
        return 0

    def calHeight(self,tRoot):
        if tRoot:
            x = self.calHeight(tRoot._left)   
            y = self.calHeight(tRoot._right)   
            if x > y:
                return x+1
            else:
                return y+1
        return 0

    def height(self,tRoot):
        h = self.calHeight(tRoot)
        return h-1
if __name__ == '__main__':
    x = Tree()
    y = Tree()
    z = Tree()
    r = Tree()
    s = Tree()
    t = Tree()
    a = Tree()
    x.makeTree(40,a,a)
    y.makeTree(60,a,a)
    z.makeTree(20,x,a)
    r.makeTree(50,a,y)
    s.makeTree(30,r,a)
    t.makeTree(10,z,s)
    print("In order:")
    t.inOrder(t._root)
    print()
    print("Pre order:")
    t.preOrder(t._root)
    print()
    print("Post order:")
    t.postOrder(t._root)
    print()
    print("Post order:")
    t.levelOrder()
    print()
    print("No of Nodes:",end=" ")
    print(t.count(t._root))
    print("Height of tree:",end=" ")
    print(t.height(t._root))