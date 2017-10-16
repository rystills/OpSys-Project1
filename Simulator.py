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
    FinishBurst = 1
    FinishBlocked = 2
    FinishSlice = 3
    SwitchIn = 4
    SwitchOut = 5
    Arrive = 6
    
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
    override the less-than operator for priority queue sorting based on event time
    @param other: the Event we are comparing ourselves to
    """
    def __lt__(self, other):
        #first we compare times
        if (self.time != other.time):
            return self.time < other.time
        #when time is the same, we compare event priority
        if (self.eType != other.eType):
            return self.eType.value < other.eType.value
        #when events are the same, we compare PID
        return self.process.pid < other.process.pid

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
        self.events = queue.PriorityQueue()
        
        #initialize the ReadyQueue depending on the selected algorithm
        if (self.algo == Algorithm.SRT):
            self.ReadyQueue = queue.PriorityQueue() 
        #begin the simulation
        self.run()
        
    """
    show the stop message when this algorithm begins
    """
    def showStartMessage(self):
        #remove 'Algorithm.' from the algorithm name
        print("time {0}ms: Simulator started for {1} {2}".format(self.t, self.algo.name, self.queueString())) 
        
    """
    show the stop message when this algorithm finishes
    """
    def showStopMessage(self):
        #remove 'Algorithm.' from the algorithm name, and subtract 1 from time since we increment time 1 final time on completion
        print("time {0}ms: Simulator ended for {1}".format(self.t,self.algo.name),end='')
        
    """
    add an event with the specified time and type for the specified process to the event queue
    @param eventType: the type of event to add
    @param time: the time at which the event will occur
    @param process: the process to which the event corresponds
    """
    def addEvent(self,eventType, time, process):
        self.events.put(Event(eventType,time,process))
    
    """preempt the running process, switching it with the current process
    @param event: the event corresponding to the process which will preempt the running process
    """
    def preempt(self, event):
        #switch the current running process out and the preempting process in
        self.addEvent(EventType.SwitchOut, self.t + self.t_cs//2, self.currRunning)
        self.addEvent(EventType.SwitchIn, self.t + self.t_cs, event.process)
        #remove the finishBurst event corresponding to the current process since it has been preempted
        for e in self.events.queue:
            if (e.eType == EventType.FinishBurst):
                #update the time remaining for our running event to reflect the actual time left, then remove the finish event
                self.currRunning.timeRemaining = e.time - self.t
                self.events.queue.remove(e)
                break;
            
        #now set currRunning to the preempting event
        self.currRunning = event.process      
  
    """
    add either a FinishSlice event or a FinishBurst event, depending on the current algo and the time remaining in the corresponding process
    @param event: the event we are currently processing
    """      
    def addProcessFinishEvent(self, event):
        #if we are in Round Robin mode and the time slice is less than the process remaining time, we interrupt after the timeslice
        if (self.algo == Algorithm.RR and self.t_slice < event.process.timeRemaining):
            self.addEvent(EventType.FinishSlice, self.t + self.t_slice, event.process)
        else:
            self.addEvent(EventType.FinishBurst, self.t + event.process.timeRemaining, event.process)   
    
    """
    when a process arrives, display that information and either add it to the ready queue or preempt the running process
    @param event: @param event: the event containing information about the process that just arrived
    """
    def handleArrive(self,event):
        p = event.process
        if (self.algo == Algorithm.SRT and self.currRunning != None and p.cpuBurstTime < self.currRunning.timeRemaining):
            print("time {0}ms: Process {1} arrived and will preempt {2} {3}".format(self.t, p.pid, self.currRunning.pid, self.queueString()))
            self.preempt(event)
        else:
            self.ReadyQueue.put(p)
            print("time {0}ms: Process {1} arrived and added to ready queue {2}".format(self.t, p.pid, self.queueString()))
            
    """
    when a process finishes its timeslice, add a switch out event unless there are no processes on the ready queue
    @param event: the event containing information about the process that just finished its time slice
    """
    def handleFinishSlice(self,event):
        self.currRunning.timeRemaining -= self.t_slice
        #if there are no processes in the ready queue, we take the next time slice
        if (self.ReadyQueue.empty()):
            print("time {0}ms: Time slice expired; no preemption because ready queue is empty {1}".format(
                self.t,self.queueString()))
            self.addProcessFinishEvent(event)
        else:
            print("time {0}ms: Time slice expired; process {1} preempted with {2}ms to go {3}".format(
                self.t,self.currRunning.pid,self.currRunning.timeRemaining, self.queueString()))
        
            #add an event for when the current process is done switching out
            self.addEvent(EventType.SwitchOut, self.t + self.t_cs//2, self.currRunning)
            self.currRunning.state = State.Blocked
            #finally, update the current running process to indicate that nothing is running
            self.currRunning = None
    
    """
    when a process finishes its burst, add a switch out event
    """
    def handleFinishBurst(self):
        self.currRunning.timeRemaining = 0
        self.currRunning.numBursts-=1
        if (self.currRunning.numBursts == 0):
            print("time {0}ms: Process {1} terminated {2}".format(self.t, self.currRunning.pid, self.queueString()))
        else:
            print("time {0}ms: Process {1} completed a CPU burst; {2} burst{3} to go {4}".format( 
                    self.t, self.currRunning.pid, self.currRunning.numBursts, "" if self.currRunning.numBursts==1 else "s", self.queueString()))
            print("time {0}ms: Process {1} switching out of CPU; will block on I/O until time {2}ms {3}".format( 
                    self.t, self.currRunning.pid, self.t+self.t_cs//2+self.currRunning.ioTime, self.queueString()))
        
        #add an event for when the current process is done switching out
        self.addEvent(EventType.SwitchOut, self.t + self.t_cs//2, self.currRunning)
        self.currRunning.state = State.Blocked
        #finally, update the current running process to indicate that nothing is running
        self.currRunning = None
        
    """
    when a process finishes switching out, add an io block event
    @param event: the event containing information about the process that just switched out
    """
    def handleSwitchOut(self, event):
        #once all bursts are finished, after switching out, the process should be destroyed
        if (event.process.numBursts == 0):
            self.processes.remove(event.process)
        else:
            #if time remaining is 0, we should begin io and set time remaining to the new burst time
            if (event.process.timeRemaining == 0):
                event.process.timeRemaining = event.process.cpuBurstTime
                self.addEvent(EventType.FinishBlocked, self.t + event.process.ioTime, event.process)
            else:
                #if time remaining is not 0, we simply return to the ready queue
                event.process.state = State.Ready
                self.ReadyQueue.put(event.process)
        
    """
    when a process is finished with io blocking, add it back to the ready queue
    @param event: the event containing information about the process that just finished io blocking
    """
    def handleFinishBlocked(self, event):
        p = event.process
        p.state = State.Ready
        if (self.algo == Algorithm.SRT and self.currRunning != None and p.timeRemaining < self.currRunning.timeRemaining):
            print("time {0}ms: Process {1} completed I/O and will preempt {2} {3}".format(self.t, p.pid, self.currRunning.pid, self.queueString()))
            self.preempt(event)
        else:
            self.ReadyQueue.put(p)
            print("time {0}ms: Process {1} completed I/O; added to ready queue {2}".format(self.t, p.pid, self.queueString()))
        
    """
    when a process is switched in, we display that information and add a new event for its completion time
    @param event: the event containing information about the process that just switched in
    """
    def handleSwitchIn(self,event):
        print("time {0}ms: Process {1} started using the CPU {2}{3}".format(
            self.t, self.currRunning.pid, "" if self.currRunning.timeRemaining == self.currRunning.cpuBurstTime else 
            "with " + str(self.currRunning.timeRemaining) + "ms remaining ",self.queueString()))
        self.addProcessFinishEvent(event)
        
    """
    get how much context switch time is remaining to switch the current running process out, if any
    @returns the amount of time until the current context switch out finishes, or 0 if no context switch out is currently happening
    """
    def switchOutRemainingTime(self):
        for e in self.events.queue:
            if (e.eType == EventType.SwitchOut):
                #we found a switch out event: return the difference between the current time and the event time
                return e.time - self.t
        return 0

    """
    check the ready queue for a process to switch in if no process is currently running
    """    
    def updateReadyQueue(self):
        #make sure nothing is running or switching out, and the queue is not empty
        if (self.currRunning == None and not self.ReadyQueue.empty() and self.switchOutRemainingTime() == 0):
            #grab the next event from the ready queue and set it to the running state
            self.currRunning = self.ReadyQueue.get()
            self.currRunning.state = State.Running
            self.addEvent(EventType.SwitchIn, self.t + self.t_cs//2, self.currRunning) 
    
    """
    process the specified event, calling the corresponding helper method
    @param event: the event to process
    """
    def processEvent(self, event):
        #process arrive event type
        if (event.eType == EventType.Arrive):
            self.handleArrive(event)
        #process switch in event type
        elif (event.eType == EventType.SwitchIn):
            self.handleSwitchIn(event)
        #process switch out event type
        elif (event.eType == EventType.SwitchOut):
            self.handleSwitchOut(event)
        #process finish blocked event type
        elif (event.eType == EventType.FinishBlocked):
            self.handleFinishBlocked(event)
        #process finish burst event type
        elif (event.eType == EventType.FinishBurst):
            self.handleFinishBurst()
        #process finish slice event type
        elif (event.eType == EventType.FinishSlice):
            self.handleFinishSlice(event)

    """
    run this simulation
    """
    def run(self):
        self.showStartMessage()
        #populate the event queue with the arrival event for all processes
        for p in self.processes:
            self.addEvent(EventType.Arrive,p.arrivalTime, p)
            
        #jump from event to event
        while(not self.events.empty()):
            #get the current event and update time
            currEvent = self.events.get()
            self.t = currEvent.time
            
            #process the current event
            self.processEvent(currEvent)
                
            #check the ready queue once all same-time events have finished, pulling in a new process if nothing is running now
            if (len(self.events.queue) == 0 or self.events.queue[0].time != self.t):
                self.updateReadyQueue()
            
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