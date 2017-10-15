from enum import Enum
import queue
from Process import State

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
        self.currRunning = None
        
        #initialize the readyQueue depending on the selected algorithm
        if (self.algo == Algorithm.FCFS or self.algo == Algorithm.RR):
            self.readyQueue = queue()
        elif (self.algo == Algorithm.SRT):
            self.readyQueue = queue.PriorityQueue()
            
        self.run()
        
    """
    run this simulation
    """
    def run(self):
        print("time {0}ms: Simulator started for {1} {2}\n".format(self.t, self.ALGO, self.queueString()))
        while (not self.processes.empty()):
            #Check for process arrival
            for p in self.processes:
                if (p.arrivalTime == self.t):
                    if (self.algo == Algorithm.SRT and self.currRunning != None and p.cpuBurstTime < self.currRunning.timeRemaining):
                        print("time {0}ms: Process {1} arrived and will preempt {2} {3}\n".format(self.t, p.id, self.currRunning.id, self.queueString()))
                    else:
                        self.readyQueue.put(p)
                        print("time {0}ms: Process {1} arrived and added to ready queue {2}\n".format(self.t, p.id, self.queueString()))
            
            #Check if the current running process is done
            if (self.currRunning != None):
                self.currRunning.timeRemaining-=1
                #If the current process is done with it's CPU burst context switch it out
                if (self.currRunning.timeRemaining == 0):                    
                    if (self.currRunning.numBursts == 0):
                        print("time {0}ms: Process {1} terminated {2}\n".format(self.t, self.currRunning.id, self.queueString()))
                        self.processes.remove(self.currRunning)
                        self.currRunning = None
                    else:
                        print("time {0}ms: Process {1} completed a CPU burst; {2} burst{3} to go {4}\n".format( 
                                self.t, self.currRunning.id, self.currRunning.numBursts, "" if self.currRunning.numBursts==1 else "s", self.queueString()))
                        print("time {0}ms: Process {1} switching out of CPU; will block on I/O until time {2}ms {3}\n".format( 
                                self.t, self.currRunning.id, self.t+self.t_cs/2+self.currRunning.ioTime, self.queueString()))
                        self.currRunning.state = State.BLOCKED
                        self.currRunning.timeRemaining = self.currRunning.ioTime
                    
                    self.currRunning = None
                    self.t += self.t_cs/2; #Half the time of a context switch is bringing in the process
            
            #TODO handle other algorithms with possible preemptions
            #Context switch in a process if possible and necessary
            if (self.currRunning == None and not self.readyQueue.isEmpty()):
                #TODO this might not be handling background IO properly during a context switch
                self.currRunning = self.readyQueue.remove()
                self.currRunning.state = State.RUNNING
                self.currRunning.timeRemaining = self.currRunning.cpuBurstTime
                self.currRunning.numBursts-=1
                self.t += self.t_cs/2; #Half the time of a context switch is bringing in the process
                print("time {0}ms: Process {1} started using the CPU {2}\n".format(self.t, self.currRunning.id, self.queueString()))
            
            for p in (proc for proc in sorted(self.processes) if proc.state == State.BLOCKED):
                if (p.timeRemaining == 0):
                    p.state = State.READY
                    self.readyQueue.add(p)
                    print("time {0}ms: Process {1} completed I/O; added to ready queue {2}\n".format(self.t, p.id, self.queueString()))
                else:
                    p.timeRemaining -= 1
            self.t+=1
        print("time {0}ms: Simulator ended for {1}\n".format(self.t,self.algo))
    
    """
    get the state of the ready queue in string form
    @returns a string representing the contents of the ready queue
    """
    def queueString(self):
        ans = ""
        if (self.readyQueue.Empty()):
            ans = " <empty>"
        for p  in self.readyQueue:
            ans += " "+p.id
        return "[Q{0}]".format(ans)
        