#------------------------------
from Memory import Heap
from LinkedList import LinkedList, Block
#-----------------------------^

#------------------------------
def parse_line(line):
    #Example:
    #a, 5, 0
    #f, 0
    #a, 10, 1
    #r, 20, 1, 2
    #f, 2   

    tokens = line.split(",")
    
    return tokens
#-----------------------------^
    
#------------------------------
def main():
    # Get file name from user, then open file.
    file_name = input("Enter file name: ")
    input_file = open(file_name, "r")

    # Create the heap.
    heap = Heap()
    
    # Read the input file, and put every request (single line in file)
    # into a list.
    requests = []
    for line in input_file:
        requests.append(parse_line(line))

    # Execute the requests.
    for request in requests:
        if request[0] == "a":
            heap.myalloc(request)
        elif request[0] == "f":
            heap.myfree(request)
        elif request[0] == "r":
            heap.myrealloc(request)
    
    # Create a file to write output to.
    output_file = open("output.txt", "a")
    
    # Print the value of all of the words in the heap into the output file.
    x = 0
    while (x < len(heap.word_array)):
       output_file.write("Word " + str(x) + ", " + str(hex(heap.word_array[x])))
       output_file.write("\n")
       x += 1
    
    # Close the input and output file.
    input_file.close()
    output_file.close()
#-----------------------------^

#------------------------------
if __name__ == "__main__":
    main()
#-----------------------------^
