from enum import Enum
import queue

"""
Algorithm is a simple enum containing each of the algorithms covered by our simulation
"""
class Algorithm(Enum):
    FCFS = 1
    SRT = 2
    RR = 3

"""
The Simulator class is responsible for emulating our CPU, running through the input processes using the selected algorithm
"""
class Simulator():
    """
    Simulator constructor: creates a new simulator with the specified algorithm and input processes, then runs the simulation
    @param algo: the algorithm that this simulator should use when executing the processes
    @param _processes: the processes that should be executed by the simulator
    """
    def __init__(self,algo,processes):
        #algo contains the selected algorithm from our enum
        self.algo = algo
        #processes defines a List of all processes that were sent to our CPU
        self.processes = list(processes)
        #hard-coded context switch time (in milliseconds) as specified in the project requirements
        self.t_cs = 8
        #number of processes to simulate - stored in a static variable as specified in the project requirements
        self.n = len(self.processes)
        #t stores the current time (in milliseconds) and is iterated for each step of the simulation
        self.t = 0
        #readyQueue defines a Queue of processes in the ready state (able to begin their CPU burst)
        self.readyQueue = queue()
        #currRunning holds the process which is currently using the CPU
        self.currRunning = None;
        
        #initialize the readyQueue depending on the selected algorithm
        if (self.algo == Algorithm.FCFS or self.algo == Algorithm.RR):
            self.readyQueue = queue();
        elif (self.algo == Algorithm.SRT):
            self.readyQueue = queue.PriorityQueue()
            
        self.run()
        
    """
    run this simulation
    """
    def run(self):
        
    
    """
    get the state of the ready queue in string form
    @returns a string representing the contents of the ready queue
    """
    def queueString(self):
        ans = "";
        if (self.readyQueue.Empty()):
            ans = " <empty>";
        for p  in self.readyQueue:
            ans += " "+p.id;
        return "[Q{0}]".format(ans);
        