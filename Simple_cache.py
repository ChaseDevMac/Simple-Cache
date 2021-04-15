import pdb
class ContentItem:
    def __init__(self, cid, size, header, content):
        self.cid = cid
        self.size = size
        self.header = header
        self.content = content

    def __str__(self):
        return f'CONTENT ID: {self.cid} SIZE: {self.size} HEADER: {self.header} CONTENT: {self.content}'

    __repr__=__str__


class Node:
    def __init__(self, content):
        self.value = content
        self.next = None

    def __str__(self):
        return f'CONTENT:{self.value}\n'

    __repr__=__str__


class CacheList:
    def __init__(self, size):
        self.head = None
        self.tail = None
        self.maxSize = size
        self.remainingSize = size
        self.numItems = 0

    def __str__(self):
        listString = ""
        current = self.head
        while current is not None:
            listString += "[" + str(current.value) + "]\n"
            current = current.next
        return f'REMAINING SPACE:{self.remainingSize}\nITEMS:{self.numItems}\nLIST:\n{listString}\n'     

    __repr__=__str__

    def __len__(self):
        return self.numItems

    def put(self, content, evictionPolicy):
        if content.size > self.maxSize:
            return 'Insertion not allowed. Content size is too large.'

        matching_ID_node = self.__matchingID(content.cid)[1]
        if isinstance(matching_ID_node, Node):
            return f'Insertion of content item {content.cid} not allowed. Content already in cache.'

        if content.size > self.remainingSize:
            self.__makeSpace(content, evictionPolicy)

        inserted_node = Node(content)
        if len(self) == 0:
            self.head, self.tail = inserted_node, inserted_node
        else:
            inserted_node.next = self.head
            self.head = inserted_node
        self.numItems += 1
        self.remainingSize -= inserted_node.value.size
        return f'INSERTED: {content}'

    def __makeSpace(self, content, evictionPolicy):
        '''Takes in content and eviction policy and removes a node in linked list until there is enough space for input content can be put into linked list'''
        if evictionPolicy == 'mru':
            while content.size > self.remainingSize:
                self.mruEvict()
        else:
            while content.size > self.remainingSize:
                self.lruEvict()
    
    def __matchingID(self, cid):
        '''Takes in a content cid and returns a tuple of the general position in the linked list (head/middle/tail) and node with matching content cid of input'''

        if len(self) == 0:
            return ('nowhere', None)
        elif cid == self.head.value.cid:
            return ('head', self.head)

        current_node = self.head
        while current_node:
            next_node = current_node.next
            if isinstance(next_node, Node) and next_node.value.cid == cid:
                if next_node == self.tail:
                    return ('tail', current_node)
                else:
                    return ('middle', current_node)
            current_node = next_node
        return ('nowhere', None)

    def find(self, cid):
        general_position, previous_of_matching_node = self.__matchingID(cid)
        if general_position == 'nowhere':
            return None

        matching_node = previous_of_matching_node.next
        if general_position == 'middle':
            previous_of_matching_node.next = matching_node.next
            matching_node.next = self.head
            self.head = matching_node
        elif general_position == 'tail':
            previous_of_matching_node.next = None
            self.tail = previous_of_matching_node
            matching_node.next = self.head
            self.head = matching_node
        #if general_position == 'head' then linked list is unchanged, all paths return self.head
        return self.head 


    def update(self, cid, content):
        found_node = self.find(cid)
        if found_node:
            updated_node = Node(content)
            updated_node.next = self.head.next
            self.head = updated_node
            return f'UPDATED: {self.head.value}'
        return None
        

    def mruEvict(self):
        if len(self) == 1:
            self.remainingSize += self.head.value.size
            self.clear()
        else:
            self.remainingSize += self.head.value.size
            self.numItems -= 1
            self.head = self.head.next

    
    def lruEvict(self):
        if len(self) == 1:
            self.remainingSize += self.tail.value.size
            self.clear()
        else:
            current_node = self.head
            while current_node:
                if current_node.next == self.tail:
                    self.remainingSize += self.tail.value.size
                    self.tail = current_node
                    current_node.next = None
                    self.numItems -= 1
                current_node = current_node.next

    
    def clear(self):
        self.head = None
        self.numItems = 0
        self.remainingSize = self.maxSize
        return 'Cleared cache!'


class Cache:
    def __init__(self):
        self.hierarchy = [CacheList(200) for _ in range(3)]
        self.size = 3
    
    def __str__(self):
        return f'L1 CACHE:\n{self.hierarchy[0]}\nL2 CACHE:\n{self.hierarchy[1]}\nL3 CACHE:\n{self.hierarchy[2]}\n'
    
    __repr__=__str__


    def clear(self):
        for item in self.hierarchy:
            item.clear()
        return 'Cache cleared!'

    def hashFunc(self, contentHeader):
        total = 0
        for char in contentHeader:
            total += ord(char)
        return total % self.size


    def insert(self, content, evictionPolicy):
        hash_func = self.hashFunc(content.header)
        return self.hierarchy[hash_func].put(content, evictionPolicy)


    def retrieveContent(self, content):
        hash_func = self.hashFunc(content.header)
        cache_level = self.hierarchy[hash_func]
        cache_find = cache_level.find(content.cid)
        if cache_find:
            return content
        return 'Cache miss!'
        
    def updateContent(self, content):
        hash_func = self.hashFunc(content.header)
        cache_level = self.hierarchy[hash_func]
        cache_update = cache_level.update(content.cid, content)
        if cache_update:
            return cache_update
        return 'Cache miss!'
