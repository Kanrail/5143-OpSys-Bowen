import matplotlib.pyplot as plt
import random
import sys
import os
import numpy as np

class page_frame(object):
    """
	Class name: page_frame
	List of functions: __init__, resetLastAccess, incLastAccess, getLastAccess, incAccessCount,
                        getFLoaded, setFLoaded, getMemInstruction
	Description: Holds all of the data for a page frame for use in both physical and virtual memory
	"""
    def __init__(self, **kwargs):
        """
		Name: __init__
		Input: kwargs
		Output: None
		Description: Sets initial variables in use by the many other functions. Takes in the process cycle
                    time and assigns that to when the program was first loaded into memory (firstLoaded).
	"""
        self.last_access = 0    # time stamp
        self.access_count = 0   # sum of accesses
        if 'memInstruction' in kwargs: #pID and virtual mem address
            self.memInstruction = kwargs['memInstruction']
        if 'processCycle' in kwargs:
            self.firstLoaded = int(kwargs['processCycle'])
        else:
            self.firstLoaded = 0

    def resetLastAccess (self):
        self.last_access = 0

    def incLastAccess (self):
        self.last_access += 1

    def getLastAccess (self):
        return self.last_access

    def incAccessCount (self):
        self.access_count += 1

    def getAccessCount (self):
        return self.access_count

    def getFLoaded (self):
        return self.firstLoaded

    def setFLoaded (self, pCycle):
        self.firstLoaded = pCycle

    def getMemInstruction(self):
        return self.memInstruction

class physical_memory(object):
    """
	Class name: physical_memory
	List of functions: __init__, incPageFaultTotal, getPageFaultTotal, newPCycle, loadPFrame
	Description: Simulates a virtual memory of size equal to mem_size. 
	"""
    def __init__(self,mem_size):
        self.mem_size = int(mem_size)
        self.pageFaultTotal = 0

        self.mem_table = {}        # dictionary of page_frames
        self.pCycleNum = -1

    def incPageFaultTotal (self):
        """
		Name: inPageFaultTotal
		Input: None
		Output: None
		Description: Increments when a page fault has been detected in when loading a new page frame
                    into physical memory.
		"""
        self.pageFaultTotal += 1

    def getPageFaultTotal (self):
        """
		Name: getPageFaultTotal
		Input: None
		Output: pageFaultTotal (int)
		Description: Returns the total number of page faults for final print of the simulation.
		"""
        return self.pageFaultTotal

    def newPCycle (self): #new process cycle
        """
		Name: newPCycle
		Input: None
		Output: None
		Description: Represents a new processor cycle as a new page frame is processed to be loaded
                    into memory. pCycleNum indicates the process cycle time counter and iterates through
                    the memory table adding 1 to the last access time of each 
		"""
        self.pCycleNum+=1
        for instruction in self.mem_table:
            self.mem_table[instruction].incLastAccess()

    def loadPFrame (self,pFrame, **kwargs):
        """
		Name: loadPFrame
		Input: kwargs
		Output: Boolean or memInstruct(str)
		Description: 
		"""
        memInstruct = pFrame.getMemInstruction() #gets the string of the instruction
        if 'replacementType' in kwargs: #populates the replacement type for the load
            replacementType = kwargs['replacementType']
        if memInstruct in self.mem_table: #if the instruction is already in physical memory
            self.mem_table[memInstruct].incAccessCount()
            self.mem_table[memInstruct].resetLastAccess()
            return True
        elif len(self.mem_table) < self.mem_size: #if physical memory isn't full
            pFrame.setFLoaded(self.pCycleNum)
            self.mem_table[memInstruct] = pFrame
            self.mem_table[memInstruct].incAccessCount()
            self.incPageFaultTotal()
            return False
        else: #replace via specified scheme in replacementType
            replacedPFrame = ''
            self.incPageFaultTotal()
            if replacementType == 'fInfOut': #First in first out
                for instruction in self.mem_table:
                    if replacedPFrame == '': #If at beginning of search for replacement
                        replacedPFrame = self.mem_table[instruction]
                    else:
                        if self.mem_table[instruction].getFLoaded() < replacedPFrame.getFLoaded():
                            replacedPFrame = self.mem_table[instruction]
            elif replacementType == 'LRU': #Least Recently Used
                for instruction in self.mem_table:
                    if replacedPFrame == '': #If at beginning of search for replacement
                        replacedPFrame = self.mem_table[instruction]
                    else:
                        if self.mem_table[instruction].getLastAccess() > replacedPFrame.getLastAccess():
                            replacedPFrame = self.mem_table[instruction]
            elif replacementType == 'LFU': #Least Frequently Used
                for instruction in self.mem_table:
                    if replacedPFrame == '': #If at beginning of search for replacement
                        replacedPFrame = self.mem_table[instruction]
                    else:
                        if self.mem_table[instruction].getAccessCount() <  replacedPFrame.getAccessCount():
                            replacedPFrame = self.mem_table[instruction]
            elif replacementType == 'random': #Random Replacement
                randomChoice = random.choice(list(self.mem_table.items()))
                replacedPFrame = randomChoice[1]
            del self.mem_table[replacedPFrame.getMemInstruction()] #Removes instruction to be replaced
            pFrame.setFLoaded(self.pCycleNum) #Marks the time the new instruction is loaded into memory
            self.mem_table[memInstruct] = pFrame #Places new instruction into memory
            return memInstruct #return the string of the process as confirmation of completion

def myargs(sysargs):
	"""
	Name: myargs
	Input: sysargs
	Output: args
	Description: Reads in the directory from command line.
		e.g. "python driver.py directory="./MemTest"
	"""
    args = {}

    for val in sysargs[1:]:
        k,v = val.split('=')
        args[k] = v
    return args

if __name__=='__main__':

    args = myargs(sys.argv) #Get the directory from command line

    if not 'directory' in args: #If directory wasn't in the command, error and exit program
        usage("Error: directory not on command line...")
        sys.exit()

    path = args['directory']

    try:
        for r, d, f in os.walk(path): #Traverses everything in specified directory
            for file in f: #For each file in that directory
                name, ext = file.split('.') #Removes the .dat from end of file name
               #Parses the filename (sim #, number of processes, virt mem size, physical memory size)
		s, run, np1, vm, pm = name.split('_') 
                instList = [] #Instruction List
                fileOpen = open(path+'/'+file, 'r')
                fifoTotal, LRUTotal, LFUTotal, randTotal = 0,0,0,0
                for line in fileOpen: #Reads in every line in the file if more than one
                    for word in line.split(): #splits each instruction and appends them to the list
                        instList.append(word)
                for i in range(4): #Iterates 4 times, once for each replacement algorithm
                    physMem = physical_memory(pm)
                    tempInstList = instList
                    virtMem = {}
                    if i == 0: #First in First out
                        replaceType = 'fInfOut'
                        print(replaceType)
                    elif i == 1: # Least Recently Used
                        replaceType = 'LRU'
                        print(replaceType)
                    elif i == 2: #Least Frequently Used
                        replaceType = 'LFU'
                        print(replaceType)
                    else: #Random Replacement
                        replaceType = 'random'
                        print(replaceType)
                    for instruction in tempInstList: #Runs through each instruction
                        physMem.newPCycle() #New processor cycle
                        if instruction not in virtMem: #Loads instruction into virtual memory
                            virtMem[instruction] = page_frame(memInstruction=instruction)
                        else:
                            pass
                        returnType = physMem.loadPFrame(virtMem[instruction], replacementType=replaceType)
                        if isinstance(returnType, bool):
                            pass#Is either already in pm, or loaded into empty pm slot
                        elif isinstance(returnType, str):
                            pass#This is where virtual memory would vbit would be updated, moved out of pm
                    if i == 0: #First in First out total output
                        fifoTotal = physMem.getPageFaultTotal()
                        print (fifoTotal)
                    elif i == 1: #Least Recently Used total output
                        LRUTotal = physMem.getPageFaultTotal()
                        print (LRUTotal)
                    elif i == 2: #Least Frequently Used total output
                        LFUTotal = physMem.getPageFaultTotal()
                        print (LFUTotal)
                    else: #Random total output
                        randomTotal = physMem.getPageFaultTotal()
                        print (randomTotal)
                #print pyplot of results for that file here
                replaceTypes = ('FIFO', 'LRU', 'LFU', 'Random')
                totals = [int(fifoTotal),int(LRUTotal),int(LFUTotal),int(randomTotal)]
                y_pos = np.arange(len(replaceTypes))
                plt.ylabel('# of Page Faults')
                plt.xlabel('Replacement Scheme')
                plt.bar(y_pos, totals,align="center",alpha=.5)
                plt.tight_layout(pad=4)
                plt.xticks(y_pos,replaceTypes)
                plt.title('Simulation ' + file)
                #plt.show()
                plt.savefig(file+'.png')
		plt.clf() #Clears plot buffer between runs

            #Will repeat for every file in given directory
    except: #If any errors at all occur
        print("Something went wrong. Please try again with a valid directory.")
        pass
