from __future__ import print_function
import sys
from Process import Process
from _dummy_thread import error

"""
print to standard error
@param args: optional array of arguments
@param kwargs: optional array of keyword arguments
"""
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    
"""
display a message on standard error and exit the program
@param msg: the message to display
"""
def exitError(msg):
    eprint("Error:",msg)
    sys.exit(1)
    
"""
read the process info from the specified input file
@param fileName: the name of the file containing our process info
"""
def readInput(fileName):
    processes = []
    try:
        for line in (l for l in open(fileName) if l[0] != '#'):
            processes.append(Process(*(line.strip().split('|'))))
    except IOError:
        exitError("Invalid input file format")
    
def main():
    #make sure the user specifies the correct number of arguments
    if (len(sys.argv) < 2):
        exitError("ERROR: Invalid arguments\nUSAGE: ./a.out <input-file> <stats-output-file>")
   
    readInput(sys.argv[1])
    
if __name__ == "__main__":
    main()