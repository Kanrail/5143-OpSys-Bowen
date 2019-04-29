import matplotlib.pyplot as plt
import random
import sys
import os
import numpy as np

class page_frame(object):
    def __init__(self, **kwargs):
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
    def __init__(self,mem_size):
        self.mem_size = int(mem_size)
        self.pageFaultTotal = 0

        self.mem_table = {}        # dictionary of page_frames
        self.pCycleNum = -1

    def incPageFaultTotal (self):
        self.pageFaultTotal += 1

    def getPageFaultTotal (self):
        return self.pageFaultTotal

    def newPCycle (self): #new process cycle
        self.pCycleNum+=1
        for instruction in self.mem_table:
            self.mem_table[instruction].incLastAccess()

    def loadPFrame (self,pFrame, **kwargs):
        #self.testNum+=1
        memInstruct = pFrame.getMemInstruction()
        if 'replacementType' in kwargs:
            replacementType = kwargs['replacementType']
        if memInstruct in self.mem_table: #if the instruction is already in physical memory
            #print('Mem in table')
            self.mem_table[memInstruct].incAccessCount()
            self.mem_table[memInstruct].resetLastAccess()
            return True
        elif len(self.mem_table) < self.mem_size: #if physical memory isn't full
            #print('Mem Not full')
            pFrame.setFLoaded(self.pCycleNum)
            self.mem_table[memInstruct] = pFrame
            self.mem_table[memInstruct].incAccessCount()
            self.incPageFaultTotal()
            return False
        else: #replace via specified scheme in replacementType
            replacedPFrame = ''
            self.incPageFaultTotal()
            if replacementType == 'fInfOut':
                for instruction in self.mem_table:
                    if replacedPFrame == '':
                        replacedPFrame = self.mem_table[instruction]
                    else:
                        if self.mem_table[instruction].getFLoaded() < replacedPFrame.getFLoaded():
                            replacedPFrame = self.mem_table[instruction]
            elif replacementType == 'LRU':
                for instruction in self.mem_table:
                    if replacedPFrame == '':
                        replacedPFrame = self.mem_table[instruction]
                    else:
                        if self.mem_table[instruction].getLastAccess() > replacedPFrame.getLastAccess():
                            replacedPFrame = self.mem_table[instruction]
            elif replacementType == 'LFU':
                for instruction in self.mem_table:
                    if replacedPFrame == '':
                        replacedPFrame = self.mem_table[instruction]
                    else:
                        if self.mem_table[instruction].getAccessCount() <  replacedPFrame.getAccessCount():
                            replacedPFrame = self.mem_table[instruction]
            elif replacementType == 'random':
                randomChoice = random.choice(list(self.mem_table.items()))
                replacedPFrame = randomChoice[1]
            del self.mem_table[replacedPFrame.getMemInstruction()]
            pFrame.setFLoaded(self.pCycleNum)
            self.mem_table[memInstruct] = pFrame
            return memInstruct

def myargs(sysargs):
    args = {}

    for val in sysargs[1:]:
        k,v = val.split('=')
        args[k] = v
    return args

if __name__=='__main__':

    args = myargs(sys.argv)

    if not 'directory' in args:
        usage("Error: directory not on command line...")
        sys.exit()

    path = args['directory']

    #try:
    for r, d, f in os.walk(path):
        for file in f:
            name, ext = file.split('.')
            s, run, np1, vm, pm = name.split('_')
            instList = []
            fileOpen = open(path+'/'+file, 'r')
            fifoTotal, LRUTotal, LFUTotal, randTotal = 0,0,0,0
            for line in fileOpen:
                for word in line.split():
                    instList.append(word)
            for i in range(4):
                physMem = physical_memory(pm)
                tempInstList = instList
                virtMem = {}
                if i == 0:
                    replaceType = 'fInfOut'
                    print(replaceType)
                elif i == 1:
                    replaceType = 'LRU'
                    print(replaceType)
                elif i == 2:
                    replaceType = 'LFU'
                    print(replaceType)
                else:
                    replaceType = 'random'
                    print(replaceType)
                for instruction in tempInstList:
                    physMem.newPCycle()
                    if instruction not in virtMem:
                        virtMem[instruction] = page_frame(memInstruction=instruction)
                    else:
                        #virtMem[instruction].incAccessCount()
                        pass
                    returnType = physMem.loadPFrame(virtMem[instruction], replacementType=replaceType)
                    if isinstance(returnType, bool):
                        pass#Is either already in pm, or loaded into empty pm slot
                    elif isinstance(returnType, str):
                        pass#This is where virtual memory would vbit would be updated, moved out of pm
                if i == 0:
                    fifoTotal = physMem.getPageFaultTotal()
                    print (fifoTotal)
                elif i == 1:
                    LRUTotal = physMem.getPageFaultTotal()
                    print (LRUTotal)
                elif i == 2:
                    LFUTotal = physMem.getPageFaultTotal()
                    print (LFUTotal)
                else:
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

        #Will repeat for every file in given directory
    #except:
    #    print("something fucked up")
    #    pass
