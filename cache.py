class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


def cache(maxsize=128):

    def decorator(func):
        storage = {}

        head = Node(None, None)
        tail = Node(None, None)

        head.next = tail
        tail.prev = head

        def add_node(node):
            node.next = head.next
            node.prev = head
            head.next.prev = node
            head.next = node

        def remove_node(node):
            prev = node.prev
            nxt = node.next
            prev.next = nxt
            nxt.prev = prev
        
        def move_to_front(node):
            remove_node(node)
            add_node(node)

        def pop_tail():
            node = tail.prev
            remove_node(node)
            return node

        def wrapper(*args,**kwargs):
            key = (args, tuple(sorted(kwargs.items())))

            if key in storage:
                node = storage[key]
                move_to_front(node)
                print("FROM CACHE")
                return node.value
            

            print("CALCULATIG")
            result = func(*args, **kwargs)
            node = Node(key, result)
            storage[key] = node
            add_node(node)

            if len(storage) > maxsize:
                tail_node = pop_tail()
                del storage[tail_node.key]

            return result
    
        return wrapper
    
    return decorator

