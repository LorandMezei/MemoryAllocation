# -*- coding: utf-8 -*-

# Source credit: 
# https://realpython.com/linked-lists-python/#introducing-collectionsdeque
# https://www.geeksforgeeks.org/linked-list-set-3-deleting-node/

#------------------------------
class LinkedList():
    def __init__(self):
        self.head = None
        
    def add_beg(self, new_block):
        new_block.next_block = self.head
        self.head = new_block
        
    def add_end(self, new_block):
        # If the freelist is empty (head is not assigned a node yet), assign
        # head block to new block
        if self.head is None:
            self.head = new_block
            return
        
        # If the freelist is not empty, go to the last block and insert new block there.
        block = self.head
        
        while block.next_block is not None:
            block = block.next_block 
            
        block.next_block = new_block
        
    def get_end_block(self):
        # If the freelist is not empty, go to the last block.
        block = self.head
        
        while block.next_block is not None:
            block = block.next_block 
            
        return block
            
    def delete_block(self, pointer_address):
        # Save the head block to a temp variable.
        temp = self.head
        
        if temp is None:
            return
        
        # If the head block is the block to be deleted.
        if temp is not None:
            if temp.pointer_address == pointer_address:
                self.head = temp.next_block
                temp = None
                return
            
        # Find the block to be deleted. Keep track of previous block.
        while temp is not None:
            if temp.pointer_address == pointer_address:
                break
            
            prev = temp
            temp = temp.next_block
            
        # If block to be deleted was not found.
        if temp == None:
            return
        
        # Delete block from linked list.
        prev.next_block = temp.next_block
        
        temp = None
        
    def print_traverse(self):
        block = self.head
        
        if block is None:
            return
        
        print("Block id: " + str(block.reference_ID))
        print("Block address: " + str(block.pointer_address))
        print("Block size: " + str(block.block_size))
        print("Block allocated: " + str(block.allocated))
        print("\n")
        
        while block.next_block is not None:
            block = block.next_block
           
            print("Block id: " + str(block.reference_ID))
            print("Block address: " + str(block.pointer_address))
            print("Block size: " + str(block.block_size))
            print("Block allocated: " + str(block.allocated))
            print("\n")
            
    def firstfit_traverse(self, size):
        block = self.head
                    
        if block.block_size >= size and block.allocated == 0:
            return block
        
        while block.next_block is not None:
            block = block.next_block

            if block.block_size >= size and block.allocated == 0:
                return block
            
    def findblock_referenceID_traverse(self, reference_ID):
        block = self.head
                    
        if block.reference_ID == reference_ID:
            return block
        
        while block.next_block is not None:
            block = block.next_block

            if block.reference_ID == reference_ID:
                return block
            
    def findblock_address_traverse(self, pointer_address):
        block = self.head
                    
        if block.pointer_address == pointer_address:
            return block
        
        while block.next_block is not None:
            block = block.next_block

            if block.pointer_address == pointer_address:
                return block
#-----------------------------^

#------------------------------
class Block():
    def __init__(self, request, pointer_address, reference_ID, block_size, allocated):
        self.request = request
        self.pointer_address = pointer_address # Points to block payload.
        self.reference_ID = reference_ID
        
        self.block_size = block_size
        self.allocated = allocated
        
        self.next_block = None
        self.prev_block = None
#-----------------------------^

# -*- coding: utf-8 -*-