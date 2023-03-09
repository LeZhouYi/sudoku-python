import threading
from config import data as dt
from config import config as cfg

STATUS_EMPTY = 0 #未填入数字
STATUS_WRITTEN = 1 #已填入数字
STATUS_BLOCKED = 2 #已填入数字且锁定，表示不可更改
STATUS_EMPTY_CHOICE = 3 #未填入数字但已无可选数
STATUS_EXIST_1 = 4 #已填入数字但与其它数字冲突，对应状态=1转换而来的错误
STATUS_EXIST_2 = 5 #已填入数字但与其它数字冲突，对应状态=2转换而来的错误
'''
格子的基本数据结构
'''
class Lattice(object):

    def __init__(self,latticeIndex:int) -> None:
        '''
        centerX #格子相对画布所处位置的中心的X坐标
        centerY #格子相对画布所处位置的中心的Y坐标
        latticeIndex #第几个格子
        '''
        self.latticeIndex = latticeIndex #第几个格子
        self.rowIndex = int(latticeIndex/9) #第几行[0-8]
        self.columnIndex = round(latticeIndex%9) #第几列[0-8]
        self.lock = threading.Lock()
        self.alternativeNumbers = [1,2,3,4,5,6,7,8,9] #可选择的数字,若该数字不可选，则为0
        self.displayNumber = 0 #展示的数字
        self.status = STATUS_EMPTY #表示当前格子的状态

    def getPaintMethod(self)->list[int]:
        #0代表画粗，1代表画细
        methods = [[0,1],[1,1],[1,0]]
        paintMethod = methods[self.rowIndex%3]
        paintMethod.extend(methods[self.columnIndex%3])
        return paintMethod

    def isMatch(self,pointX:int,pointY:int)->bool:
        '''
        判断并返回当前坐标是否指向该格子
        pointX:当前横坐标
        pointY:当前纵坐标
        offset:允许范围内的误差
        '''
        diffX = pointX-dt.latticePoints[self.latticeIndex][0]
        diffY = pointY-dt.latticePoints[self.latticeIndex][1]
        return diffX>=-cfg.latticeOffset and diffX<=cfg.latticeOffset and diffY>=-cfg.latticeOffset and diffY <=cfg.latticeOffset

    def getRowIndex(self)->int:
        return self.rowIndex
    def getColumnIndex(self)->int:
        return self.columnIndex

    def getLatticeIndex(self)->int:
        return self.latticeIndex

    def getAlternativeNumbers(self)->list[int]:
        return self.alternativeNumbers

    def isBlocked(self)->bool:
        return self.status==STATUS_BLOCKED or self.status==STATUS_EXIST_2

    def canBlocked(self)->bool:
        return self.status==STATUS_WRITTEN or self.status==STATUS_EXIST_1

    def canClear(self)->bool:
        return self.status==STATUS_WRITTEN or self.status==STATUS_EXIST_1

    def isWritten(self)->bool:
        return self.status==STATUS_WRITTEN or self.status==STATUS_BLOCKED

    def setBlock(self):
        if self.status==STATUS_WRITTEN:
            with self.lock:
                self.status = STATUS_BLOCKED
        elif self.status==STATUS_EXIST_1:
            with self.lock:
                self.status = STATUS_EXIST_2

    def setUnlock(self):
        if self.status==STATUS_EXIST_2:
            with self.lock:
                self.status = STATUS_EXIST_1
        elif self.status==STATUS_BLOCKED:
            with self.lock:
                self.status = STATUS_WRITTEN

    def clearDisplay(self):
        if self.canClear():
            with self.lock:
                self.displayNumber=0
                self.alternativeNumbers=[1,2,3,4,5,6,7,8,9]
                self.status=STATUS_EMPTY

    def setDisplay(self,value:int):
        if not self.isBlocked():
            with self.lock:
                self.displayNumber = value #设置显示的数字
                self.alternativeNumbers = [0,0,0,0,0,0,0,0,0] #清空可选数
                #TODO:更新当前格子状态，如正常/错误等
                self.status = STATUS_WRITTEN
            #TODO:如错误，执行错误的渲染

    def backChoiceNumber(self,number:int):
        if number>=1 and number<=9:
            if self.status==STATUS_EMPTY or self.status==STATUS_EMPTY_CHOICE:
                with self.lock:
                    self.alternativeNumbers[number-1]=number

    def getDisplayNumber(self)->int:
        return self.displayNumber

    def clearChoiceByList(self,existNumbers=list[int]):
        '''
        清除可选数
        '''
        with self.lock:
            for i in range(9):
                if self.displayNumber!=0:
                    self.alternativeNumbers[i]=0
                elif i+1 in existNumbers:
                    self.alternativeNumbers[i]=0
    def clearChoiceByNumber(self,number:int):
        '''
        清空该数外的可选数
        '''
        if number>=1 and number<=9 and self.displayNumber==0:
            with self.lock:
                self.alternativeNumbers=[0,0,0,0,0,0,0,0,0]
                self.alternativeNumbers[number-1]=number

'''
数独整体数据结构
'''
class Sudoku(object):

    def __init__(self) -> None:
        '''
        size: 画布的大小
        align: 画布留出的边缘
        '''
        self.numberMatrix = []
        #初始化棋盘格子数据
        for mRow in range(9):
            for mColumn in range(9):
                index = mRow*9+mColumn
                self.numberMatrix.append(Lattice(latticeIndex = index))

    def getLatticeByPoint(self,pointX:int,pointY:int)->Lattice|None:
        '''
        根据画布当前的坐标返回对应的格子
        pointX:横坐标
        pointY:纵坐标
        '''
        for lattice in self.numberMatrix:
            if isinstance(lattice,Lattice) and lattice.isMatch(pointX=pointX,pointY=pointY):
                return lattice
        return None

    def getLatticeByIndex(self,index:int)->Lattice|None:
        if index>=0 and index <81:
            return self.numberMatrix[index]
        return None

    def setLatticeDisplay(self,index:int,value:int):
        '''
        将value写入第index个格子
        '''
        if index>=0 and index < 81:
            self.numberMatrix[index].setDisplay(value)

    def clearLattice(self,index:int):
        if index>=0 and index<81:
            lattice = self.numberMatrix[index]
            if lattice.canClear():
                number = lattice.getDisplayNumber()
                rowIndex = lattice.getRowIndex()
                cloumnIndex = lattice.getColumnIndex()
                self.numberMatrix[index].clearDisplay()
                for i in range(9):
                    self.numberMatrix[rowIndex*9+i].backChoiceNumber(number)
                    self.numberMatrix[i*9+cloumnIndex].backChoiceNumber(number)
                startRow = int(rowIndex/3)*3
                startColumn = int(cloumnIndex/3)*3
                for r in range(3):
                    for c in range(3):
                        self.numberMatrix[(startRow+r)*9+(startColumn+c)].backChoiceNumber(number)

    def inferRowChoice(self,rowIndex:int):
        '''
        行可选数推测
        '''
        existNumbers = []
        #获取已填数列表，排除被标记为错误的
        for i in range(9):
            lattice = self.getLatticeByIndex(rowIndex*9+i)
            if lattice!=None and lattice.isWritten():
                existNumbers.append(lattice.getDisplayNumber())
        #根据已填数列表排除可选数
        for i in range(9):
            self.numberMatrix[rowIndex*9+i].clearChoiceByList(existNumbers)

    def inferColumnChoice(self,cloumnIndex:int):
        '''
        列可选数推测
        '''
        existNumbers = []
        #获取已填数列表，排除被标记为错误的
        for i in range(9):
            lattice = self.getLatticeByIndex(cloumnIndex+i*9)
            if lattice!=None and lattice.isWritten():
                existNumbers.append(lattice.getDisplayNumber())
        #根据已填数列表排除可选数
        for i in range(9):
            self.numberMatrix[cloumnIndex+i*9].clearChoiceByList(existNumbers)

    def inferAreaChoice(self,areaIndex:int):
        '''
        宫可选数推测
        '''
        existNumbers = []
        startRow = int(areaIndex/3)
        startColumn = int(areaIndex%3)
        for r in range(3):
            for c in range(3):
                index = (startRow*3+r)*9+(startColumn*3+c)
                lattice = self.getLatticeByIndex(index)
                if lattice!=None and lattice.isWritten():
                    existNumbers.append(lattice.getDisplayNumber())
        for r in range(3):
            for c in range(3):
                index = (startRow*3+r)*9+(startColumn*3+c)
                self.numberMatrix[index].clearChoiceByList(existNumbers)

    def inferLatticeChoice(self,areaIndex:int):
        '''
        若某一宫内某一个数只在某一格内可填，清空该格和宫外的可选数
        '''
        startRow = int(areaIndex/3)
        startColumn = int(areaIndex%3)
        choiceNumbers = [0,0,0,0,0,0,0,0,0] #记录唯一可填的数
        choiceLattice = [-1,-1,-1,-1,-1,-1,-1,-1,-1] #记录唯一可填的数的格子的下标
        for r in range(3):
            for c in range(3):
                index = (startRow*3+r)*9+(startColumn*3+c) #计算当天格子Index
                lattice = self.getLatticeByIndex(index)
                if lattice!=None:
                    if lattice.isWritten(): #若有已填数，则该宫内不会有该可选数
                        choiceLattice[lattice.getDisplayNumber()-1]=-1
                    else:
                        alternativeNumbers = lattice.getAlternativeNumbers()
                        for numberIndex in range(9): #第一次标记，记录格子下标以后续跟踪
                            if alternativeNumbers[numberIndex]==0:
                                continue
                            if choiceNumbers[numberIndex]!=alternativeNumbers[numberIndex]:
                                choiceNumbers[numberIndex]=alternativeNumbers[numberIndex]
                                choiceLattice[numberIndex]=lattice.getLatticeIndex()#记录格子下标
                            else:
                                choiceLattice[numberIndex]=-1
        for i in range(9):
            if choiceLattice[i]!=-1:
                self.numberMatrix[choiceLattice[i]].clearChoiceByNumber(i+1) #清空该格子的其它数
                column = self.numberMatrix[choiceLattice[i]].getColumnIndex() #获取格子的列数
                row = self.numberMatrix[choiceLattice[i]].getRowIndex() #获取格子的行数
                for teIndex in range(9): #清空该格子外的可选数
                    rowLatticeIndex = row*9 + teIndex #计算行相关的格子下标
                    columnLatticeIndex = teIndex*9 + column #计算列相关的格子下标
                    if rowLatticeIndex!= choiceLattice[i]: #不处理当前格子
                        self.numberMatrix[rowLatticeIndex].clearChoiceByList([i+1]) #只清楚当前可选数
                    if columnLatticeIndex!=choiceLattice[i]: #不处理当前格子
                        self.numberMatrix[columnLatticeIndex].clearChoiceByList([i+1])#只清楚当前可选数