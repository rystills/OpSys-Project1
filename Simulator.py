from enum import Enum
import queue
from Process import State
import copy

"""
Algorithm is a simple enum containing each of the algorithms covered by our simulation
"""
class Algorithm(Enum):
    FCFS = 1
    SRT = 2
    RR = 3
   
"""
EventType is a simple enum containing each of the potential EventTypes that may occur in our simulation
""" 
class EventType(Enum):
    Arrive = 1
    FinishBurst = 2
    
"""
the event class is responsible for holding information about events that will occur at calculated points in time
"""
class Event():
    """
    event constructor: create a new event with the specified time, type, and process
    @param type: the EventType for this event
    @param time: the time (in milliseconds) at which this event will occur
    @param proc: the process to which this event corresponds
    """
    def __init__(self,eType,time,proc):
        self.eType = eType
        self.time = time
        self.process = proc

"""
The Simulator class is responsible for emulating our CPU, Running through the input processes using the selected algorithm
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
        self.processes = copy.deepcopy(processes)
        #hard-coded context switch time (in milliseconds) as specified in the project requirements
        self.t_cs = 8
        #hard-coded time (in milliseconds) for a single time-slice
        self.t_slice = 70
        #number of processes to simulate - stored in a static variable as specified in the project requirements
        self.n = len(self.processes)
        #t stores the current time (in milliseconds) and is iterated for each step of the simulation
        self.t = 0
        #ReadyQueue defines a Queue of processes in the Ready state (able to begin their CPU burst)
        self.ReadyQueue = queue.Queue()
        #currRunning holds the process which is currently using the CPU
        self.currRunning = None
        #maintain a queue of events so we only need to iterate to happenings rather than going over each and every ms 
        self.events = queue.Queue()
        
        #initialize the ReadyQueue depending on the selected algorithm
        if (self.algo == Algorithm.SRT):
            self.ReadyQueue = queue.PriorityQueue() 
        self.run()
        
    """
    show the stop message when this algorithm begins
    """
    def showStartMessage(self):
        #remove 'Algorithm.' from the algorithm name
        print("time {0}ms: Simulator started for {1} {2}".format(self.t, str(self.algo).split('.')[1], self.queueString())) 
        
    """
    show the stop message when this algorithm finishes
    """
    def showStopMessage(self):
        #remove 'Algorithm.' from the algorithm name, and subtract 1 from time since we increment time 1 final time on completion
        print("time {0}ms: Simulator ended for {1}".format(self.t-1,str(self.algo).split('.')[1]))
        
    """
    add an event with the specified time and type for the specified process to the event queue
    """
    def addEvent(self,eventType, time, process):
        self.events.put(Event(eventType,time,process))
    
    """
    run this simulation
    """
    def run(self):
        self.showStartMessage()
        currSlice = 70
        for p in self.processes:
            self.addEvent(EventType.Arrive,p.arrivalTime, p)
            
        while (len(self.processes) > 0):
            self.timeChange = 1
            #Check for process arrival
            for p in self.processes:
                if (p.arrivalTime == self.t):
                    if (self.algo == Algorithm.SRT and self.currRunning != None and p.cpuBurstTime < self.currRunning.timeRemaining):
                        print("time {0}ms: Process {1} arrived and will preempt {2} {3}".format(self.t, p.pid, self.currRunning.id, self.queueString()))
                    else:
                        self.ReadyQueue.put(p)
                        print("time {0}ms: Process {1} arrived and added to ready queue {2}".format(self.t, p.pid, self.queueString()))
            
            #Check if the current Running process is done
            if (self.currRunning != None):
                self.currRunning.timeRemaining-=1
                #If the current process is done with it's CPU burst context switch it out
                if (self.currRunning.timeRemaining == 0):                    
                    if (self.currRunning.numBursts == 0):
                        print("time {0}ms: Process {1} terminated {2}".format(self.t, self.currRunning.pid, self.queueString()))
                        self.processes.remove(self.currRunning)
                    else:
                        print("time {0}ms: Process {1} completed a CPU burst; {2} burst{3} to go {4}".format( 
                                self.t, self.currRunning.pid, self.currRunning.numBursts, "" if self.currRunning.numBursts==1 else "s", self.queueString()))
                        print("time {0}ms: Process {1} switching out of CPU; will block on I/O until time {2}ms {3}".format( 
                                self.t, self.currRunning.pid, self.t+self.t_cs//2+self.currRunning.ioTime, self.queueString()))
                        self.currRunning.state = State.Blocked
                        #add half of the context switch time to the io time as we'll be subtracting that at the end of this update
                        self.currRunning.timeRemaining = self.currRunning.ioTime + self.t_cs//2
                    
                    self.currRunning = None
                    self.t += self.t_cs//2 #Half the time of a context switch is bringing in the process
                    self.timeChange += self.t_cs//2
            
            #TODO handle other algorithms with possible preemptions
            #Context switch in a process if possible and necessary
            if (self.currRunning == None and not self.ReadyQueue.empty()):
                #TODO this might not be handling background IO properly during a context switch
                self.currRunning = self.ReadyQueue.get()
                self.currRunning.state = State.Running
                self.currRunning.timeRemaining = self.currRunning.cpuBurstTime
                self.currRunning.numBursts-=1
                self.t += self.t_cs//2 #Half the time of a context switch is bringing in the process
                self.timeChange += self.t_cs//2
                print("time {0}ms: Process {1} started using the CPU {2}".format(self.t, self.currRunning.pid, self.queueString()))
            
            for p in (proc for proc in sorted(self.processes) if proc.state == State.Blocked):
                #account for context switches, where time has shifted by more than 1 ms
                p.timeRemaining -= self.timeChange
                if (p.timeRemaining < 1):
                    p.state = State.Ready
                    self.ReadyQueue.put(p)
                    print("time {0}ms: Process {1} completed I/O; added to ready queue {2}".format(self.t + p.timeRemaining + 1, p.pid, self.queueString()))
            self.t+=1
            
        self.showStopMessage()
        
    """
    get the state of the ready queue in string form
    @returns a string representing the contents of the ready queue
    """
    def queueString(self):
        ans = ""
        if (self.ReadyQueue.empty()):
            ans = " <empty>"
        for p  in self.ReadyQueue.queue:
            ans += " "+p.pid
        return "[Q{0}]".format(ans)