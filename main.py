from __future__ import print_function
import sys
from Process import Process
from Simulator import Simulator, Algorithm

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
@returns a list of processes corresponding to the data in the input file
"""
def readInput(fileName):
    processes = []
    try:
        #read the file line by line, ignoring lines that start with a #
        for line in (l for l in open(fileName) if l[0] != '#'):
            processes.append(Process(*(line.strip().split('|'))))
    except (IOError, TypeError):
        exitError("Invalid input file format")
    return processes
  
"""
main method: parse the input file while checking for errors, then start our simulator instance
"""      
def main():
    #make sure the user specifies the correct number of arguments
    if (len(sys.argv) < 2):
        exitError("ERROR: Invalid arguments\nUSAGE: ./a.out <input-file> <stats-output-file>")
        
    #extract our processes from the input file, then begin the simulation
    processes = readInput(sys.argv[1])
    sim = Simulator(Algorithm.FCFS, processes)
    
if __name__ == "__main__":
    main()