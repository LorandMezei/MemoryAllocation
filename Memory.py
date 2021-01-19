# Source credit:
# Computer Systems Book - Chapter 9, Section 9. From C code written in figures.  

from LinkedList import LinkedList, Block
import math

#------------------------------
class Heap():
    word_array = None #array of ints (4 bytes each element)
    block_list = None #linked list of Blocks
    
    word_size        = 4 #bytes
    double_word_size = 8 #bytes
    min_block_size   = 8 #bytes
    init_heap_size   = 1001 # 1000 words + 1 word for padding (4004 bytes)
    curr_heap_size   = 1001 # words
    max_heap_size    = word_size*100000
    
    start_address    = 0 #bytes
    prologue_address = 8 #bytes
    epilogue_address = word_size*curr_heap_size - 4 #bytes
    
    def __init__(self):
        self.word_array = [0]*self.init_heap_size 
        self.block_list = LinkedList() 
        self.block_list.add_beg(Block("", 8, "initial", self.word_size*self.init_heap_size, 0))
                      
    def myalloc(self, request):
        # Ex: request = ["a", "5", "0"]
        
        # Block variables.
        block_size = int(request[1])
        reference_ID = request[2]
        temp_block_size = self.double_word_size + block_size
         
        # Ignore alloc request of size 0.
        if (block_size == 0):
            return
        
        # Adjust the block size to include overhead and 
        # alignment requirements.
        if (block_size <= self.min_block_size):
            adjusted_block_size = 2*(self.min_block_size)
        else:
            adjusted_block_size = self.get_next_multiple_8(temp_block_size)
        
        # Put the block size and allocate status together to put in header/footer.
        header_value = self.pack(adjusted_block_size, 1)
                    
        # Search the block list for a fitting free block.
        # Get the block payload address.
        pointer = self.first_fit(adjusted_block_size)
        # If needed to resize, set to 1.
        resize = 0
        
        # Check if the last block has enough block size to handle request.
        # Extend the size of the heap if it is not big enough.
        end_block = self.block_list.get_end_block()
        if adjusted_block_size >= end_block.block_size:
            self.mysbrk(adjusted_block_size)
            pointer = self.first_fit(adjusted_block_size)
            resize = 1
    
        # Write the block data into the word array.
        self.put_word(header_value, self.get_header_address(pointer.pointer_address))
        self.put_word(header_value, self.get_footer_address(pointer.pointer_address))

        # Split block only if did not need to resize.
        if resize == 0:
            self.split(reference_ID, adjusted_block_size, pointer)
        
        # Return a "pointer" to the starting address of the block payload.
        return pointer.pointer_address

    def myrealloc(self, request):
        # Free and then alloc.
        call = request[0]
        new_size = request[1]
        block_to_resize = request[2]
        referenceID = request[3]
        
        # Free
        free_request = [call, block_to_resize]
        self.myfree(free_request)
        
        # Alloc
        alloc_request = [call, new_size, referenceID]
        self.myalloc(alloc_request)
    
    def myfree(self, request):
        # Ex: f, 0
        reference_ID = request[1]
        
        # Find the block to free, given reference id.
        block = self.block_list.findblock_referenceID_traverse(reference_ID)
        
        # If block is not found, just return.
        if  block is None:
            return
    
        # Set the block to not allocated (free).
        block.allocated = 0
        
        # Update headers and footers of the block in the word array.
        header = self.pack(block.block_size, 0)
        self.put_word(header, self.get_header_address(block.pointer_address))
        self.put_word(header, self.get_footer_address(block.pointer_address))
        
        # If the block being freed is the first block, or the last block
        # in the list, then make sure these edge cases dont write/right
        # address that are out of bounds on the word array.
        # Check for edge cases:
        edge_case = 0 # 0 for not an edge case.
        # If the block being freed is the first block in the block list.
        if block.pointer_address <= self.prologue_address:
            edge_case = 1
        # If the block being freed is the last block in the block list.
        elif block.pointer_address >- self.epilogue_address:
            edge_case = 2
            
        # Join adjacent free blocks.
        if edge_case == 0:
            self.coalesce(block)
    
    def mysbrk(self, extend_size):
        # Max word array size is 100,000 words.
        # Give an error and halt simulation if the heap grows bigger than this.
        if self.word_size*self.curr_heap_size + extend_size > self.max_heap_size:
            return
        
        # Turn extend_size(bytes) into words.
        extend_size_words = int(extend_size / self.word_size)
        
        # Increase the word array length by extend size.
        for i in range(extend_size_words):
            self.word_array.append(0)
        
        # Increase the block size of the last block in the block list by extend size.
        end_block = self.block_list.get_end_block()
        end_block.block_size = end_block.block_size + extend_size
        
        # Increase current heap size.
        self.curr_heap_size = self.curr_heap_size + extend_size
        
    def coalesce(self, old_block):
        # Join together adjacent free blocks.
        # Edge cases are not coalesced.
        # Check four cases.
        
        prev_block_node = self.block_list.findblock_address_traverse(self.get_prevBlock_address(old_block.pointer_address))
        prev_block_size = self.get_block_size(self.get_prevBlock_address(old_block.pointer_address))
        prev_block_allocated = self.get_block_allocated(self.get_prevBlock_address(old_block.pointer_address))
        
        next_block_size = old_block.next_block.block_size       
        next_block_allocated = self.get_block_allocated(self.get_nextBlock_address(old_block.pointer_address))
       
        size = old_block.block_size
         
        # Case 1, previous block and next block are both allocated:
        if prev_block_allocated == 1 and next_block_allocated == 1:
            # No adjacent free blocks to coalesce.
            return
        
        # Case 2, previous block is allocated, next block is free:
        elif prev_block_allocated == 1 and next_block_allocated == 0:
            # Join old block and next block.
            
            # Old block's size is old block size + next block size.
            old_block.block_size = size + next_block_size
            
            # Delete the next block.
            block_to_delete = self.get_nextBlock_address(old_block.pointer_address)
            self.block_list.delete_block(block_to_delete)
            
            # Update the word array for old block.
            header = self.pack(old_block.block_size, 0)
            self.put_word(header, self.get_header_address(old_block.pointer_address))
            self.put_word(header, self.get_footer_address(old_block.pointer_address))
        
        # Case 3, previous block is free, next block is allocated:
        elif prev_block_allocated == 0 and next_block_allocated == 1:
            # Join old block and previous block.
          
            # Delete the old block.
            block_to_delete = old_block.pointer_address
            self.block_list.delete_block(block_to_delete)
             
            # Prev block's size is old block size + prev block size.
            prev_block_node.block_size = prev_block_node.block_size + old_block.block_size
        
            # Update the word array for prev block.
            header = self.pack(prev_block_node.block_size, 0)
            self.put_word(header, self.get_header_address(self.get_prevBlock_address(old_block.pointer_address)))
            self.put_word(header, self.get_footer_address(self.get_prevBlock_address(old_block.pointer_address)))
        
        # Case 4, previous block and next block are both free:
        elif prev_block_allocated == 0 and next_block_allocated == 0:
            # Join old block, previous block, and next block.
    
            # Delete the next block.
            block_to_delete = self.get_nextBlock_address(old_block.pointer_address)
            self.block_list.delete_block(block_to_delete)
            
            # Prev block's size is prev block size + old block size + next block size.
            prev_block_node.block_size = prev_block_node.block_size + old_block.block_size + next_block_size
            
            # Delete the old block.
            block_to_delete = old_block.pointer_address
            self.block_list.delete_block(block_to_delete)
            
            # Update the word array for prev block.
            header = self.pack(prev_block_node.block_size, 0)
            self.put_word(header, self.get_header_address(self.get_prevBlock_address(old_block.pointer_address)))
            self.put_word(header, self.get_footer_address(self.get_prevBlock_address(old_block.pointer_address)))
    
    def split(self, new_reference_ID, new_block_size, old_block):
        # Create a next free block, add it to old block's next block in linked list.
         
        # Next block's pointer address will be old block pointer address + old block size.
        next_address = old_block.pointer_address + new_block_size
        # Next block's size will be old_block_size - new_block_size
        # Next block's allocate bit will be 0.
        next_size = old_block.block_size - new_block_size 
        
        # Create next block and add to linked list:
        next_block = Block("", next_address, "next free", next_size, 0)
        self.block_list.add_end(next_block)
        
        # (Old) Newly allocated block's size is new_block_size.
        # (Old) Newly allocated block's allocate bit will remain 1)
        # Update old block:
        old_block.allocated = 1
        old_block.block_size = new_block_size
        old_block.reference_ID = new_reference_ID
                                      
    def first_fit(self, size):
        # Go through the linked list of blocks 
        # until a block with sufficient size is found. 
        # Return free block pointer address.
        return self.block_list.firstfit_traverse(size)
    
    def best_fit(self, size):
        pass
    
    # Combines a size and a allocate bit and returns a value
    # that can be placed in a header or footer.
    def pack(self, size, allocate):
        return size | allocate
    
    # Reads and returns the word referenced by the address.
    def get_word(self, address):
        # Turn address into an index into the words array.
        index =  int(address / 4)
        return self.word_array[index]
    
    # Stores the value in the word referenced by the address.
    def put_word(self, value, address):
        # Turn address into an index into the words array.
        index =  int(address / 4)
        #print(index)
        self.word_array[index] = value
        
    # Returns the size bits from the header at the 
    # word referenced by the block pointer address.
    def get_block_size(self, address):
        # Turn payload address into header address.
        header_address = self.get_header_address(address)
        index =  int(header_address / 4)
        size = self.word_array[index] & ~0x7
        return size
    
    # Returns the allocated bit from the header at the 
    # word referenced by the block pointer address.
    def get_block_allocated(self, address):
        # Turn payload address into header address.
        header_address = self.get_header_address(address)
        index =  int(header_address / 4)
        size = self.word_array[index] & 0x1
        return size
    
    # Returns the address of the block header at block pointer bp.
    def get_header_address(self, bp):
        return bp - self.word_size
    
    # Returns the address of the block footer at block pointer bp.
    def get_footer_address(self, bp):
        return bp + self.get_block_size(bp) - 2*self.word_size
    
    # Returns the address of the next block at block pointer bp.
    def get_nextBlock_address(self, bp):
        return bp + self.get_block_size(bp)
    
    # Returns the address of the previous block at block pointer bp.
    def get_prevBlock_address(self, bp):
        prev_block_size = self.get_block_size(bp - self.word_size)
        return bp - prev_block_size
    
    def get_next_multiple_8(self, number):
        return ((number + 7) & (-8)) 
#-----------------------------^
