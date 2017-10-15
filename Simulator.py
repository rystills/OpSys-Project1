from enum import Enum

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
        self.algo = algo
        self.processes = list(processes)