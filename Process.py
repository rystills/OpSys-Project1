'''
Created on Oct 15, 2017

@author: Ryan
'''

"""
The Process class represents a single process on our CPU
"""
class Process():
    """
    Process contructor: creates a new process with the specified properties
    @param id: the string ID given to the process by the input file; used for tie-breaking
    @param arrivalTime: the time it takes for the process to arrive on the ready queue
    @param cpuBurstTime: the time (in milliseconds) that the process requires to complete its CPU burst
    @param numBursts: the number of CPU bursts that this process must execute
    @param ioTime: the time (in milliseconds) that the process requires for performing i/o
    """
    def __init__(self, pid, arrivalTime, cpuBurstTime, numBursts, ioTime):
        #throw an exception if any of the specified times or numBursts are not ints
        for i in [arrivalTime,cpuBurstTime,numBursts,ioTime]:
            if (not i.isdigit()):
                raise TypeError()
        #assign each argument to a local variable
        self.pid = pid
        self.arrivalTime = int(arrivalTime)
        self.cpuBurstTime = int(cpuBurstTime)
        self.numBursts = int(numBursts)
        self.ioTime = int(ioTime)