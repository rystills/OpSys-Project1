from enum import Enum
"""
State is a simple enum containing each of the potential process states
"""
class State(Enum):
    Ready = 1
    Running = 2
    Blocked = 3

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
        self.timeRemaining = self.cpuBurstTime
        self.state = None
        
    """
    override the less-than operator for priority queue sorting based on cpu burst time, using PID as a tie breaker
    @param other: the process we are comparing ourselves to
    """
    def __lt__(self, other):
        return self.cpuBurstTime < other.cpuBurstTime if self.cpuBurstTime != other.cpuBurstTime else self.pid < other.pid