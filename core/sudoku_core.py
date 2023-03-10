import threading
import copy
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
        初始化
        '''
        self.latticeIndex = latticeIndex #第几个格子
        self.rowIndex = int(latticeIndex/9) #第几行[0-8]
        self.columnIndex = round(latticeIndex%9) #第几列[0-8]
        self.lock = threading.Lock()
        self.alternativeNumbers = [i+1 for i in range(9)] #可选择的数字,若该数字不可选，则为0
        self.displayNumber = 0 #展示的数字
        self.status = STATUS_EMPTY #表示当前格子的状态

    def getPaintMethod(self)->list[int]:
        '''
        返回该格子四条边的渲染方式
        0代表画粗，1代表画细
        '''
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
        '''
        返回格子的行数
        '''
        return self.rowIndex

    def getColumnIndex(self)->int:
        '''
        返回格子的列数
        '''
        return self.columnIndex

    def getLatticeIndex(self)->int:
        '''
        返回格子的整体下标
        '''
        return self.latticeIndex

    def getAlternativeNumbers(self)->list[int]:
        '''
        返回格子当前的可选数
        '''
        return self.alternativeNumbers

    def isBlocked(self)->bool:
        '''
        True=当前格子被锁定
        '''
        return self.status==STATUS_BLOCKED or self.status==STATUS_EXIST_2

    def canBlocked(self)->bool:
        '''
        True=当前格子可以被锁定
        '''
        return self.status==STATUS_WRITTEN or self.status==STATUS_EXIST_1

    def canClear(self)->bool:
        '''
        True=当前格子可以被擦除
        '''
        return self.status==STATUS_WRITTEN or self.status==STATUS_EXIST_1

    def isWritten(self)->bool:
        '''
        True=当前格子可以被写入数字
        '''
        return self.status==STATUS_WRITTEN or self.status==STATUS_BLOCKED

    def setBlock(self):
        '''
        锁定当前格子
        '''
        if self.status==STATUS_WRITTEN: #写入正确的数时
            with self.lock:
                self.status = STATUS_BLOCKED
        elif self.status==STATUS_EXIST_1: #写入错误的数时
            with self.lock:
                self.status = STATUS_EXIST_2

    def setUnlock(self):
        '''
        解锁当前格子
        '''
        if self.status==STATUS_EXIST_2: #锁定的数是错误时
            with self.lock:
                self.status = STATUS_EXIST_1
        elif self.status==STATUS_BLOCKED: #锁定的数是正确时
            with self.lock:
                self.status = STATUS_WRITTEN

    def clearDisplay(self):
        '''
        擦除当前格子写入的数
        '''
        if self.canClear():
            with self.lock:
                self.displayNumber=0 #擦除
                self.alternativeNumbers=[i+1 for i in range(9)] #恢复可选数
                self.status=STATUS_EMPTY #更新状态

    def setDisplay(self,value:int):
        '''
        为当前格子写入数字
        '''
        if not self.isBlocked():
            with self.lock:
                self.displayNumber = value #设置显示的数字
                self.alternativeNumbers = [0 for i in range(9)] #清空可选数
                self.status = STATUS_WRITTEN #更新状态

    def backChoiceNumber(self,number:int):
        '''
        将某个可选数添加回当前格子的可选数列表中
        '''
        if number>=1 and number<=9:
            if self.status==STATUS_EMPTY or self.status==STATUS_EMPTY_CHOICE:
                with self.lock:
                    self.alternativeNumbers[number-1]=number

    def getDisplayNumber(self)->int:
        '''
        返回当前格子被写入的数
        '''
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
                self.alternativeNumbers=[0 for i in range(9)]
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
        '''
        返回当前下标对应的格子
        '''
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
        '''
        擦除某一格子
        '''
        if index>=0 and index<81: #判断下标是否合法
            lattice = self.numberMatrix[index]
            if lattice.canClear():
                number = lattice.getDisplayNumber()
                rowIndex = lattice.getRowIndex() #格子所在行
                cloumnIndex = lattice.getColumnIndex() #格子所在列
                self.numberMatrix[index].clearDisplay()#擦除
                for i in range(9):
                    #遍历格子所在行/列，恢复当行/列的格子的可选数
                    self.numberMatrix[rowIndex*9+i].backChoiceNumber(number)
                    self.numberMatrix[i*9+cloumnIndex].backChoiceNumber(number)
                areaRow = int(rowIndex/3)*3 #计算宫起始行坐标
                areaColumn = int(cloumnIndex/3)*3 #计算宫起如列坐标
                for r in range(3):
                    for c in range(3):
                        #恢复该宫内格子的可选数
                        self.numberMatrix[(areaRow+r)*9+(areaColumn+c)].backChoiceNumber(number)

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
        若某一宫的某一个数已填，则剩余格子的可选数排除该数
        '''
        existNumbers = [] #记录已存在的数字
        areaRow = int(areaIndex/3) #宫起始行坐标
        areaColumn = int(areaIndex%3) #宫起始列坐标
        for r in range(3):
            for c in range(3):
                index = (areaRow*3+r)*9+(areaColumn*3+c) #计算格子坐标
                lattice = self.getLatticeByIndex(index)
                if lattice!=None and lattice.isWritten():
                    existNumbers.append(lattice.getDisplayNumber()) #记录已存在的数字
        for r in range(3):
            for c in range(3):
                index = (areaRow*3+r)*9+(areaColumn*3+c) #计算格子坐标
                self.numberMatrix[index].clearChoiceByList(existNumbers) #排除格子的可选数

    def inferLatticeChoice(self,areaIndex:int):
        '''
        若某一宫内某一个数只在某一格内可填，清空该格和宫外的可选数
        '''
        areaRow = int(areaIndex/3)
        areaColumn = int(areaIndex%3)
        choiceNumbers = [0 for i in range(9)] #记录唯一可填的数
        choiceLattice = [-1 for i in range(9)] #记录唯一可填的数的格子的下标
        for r in range(3):
            for c in range(3):
                index = (areaRow*3+r)*9+(areaColumn*3+c) #计算当前格子Index
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

    def inferAreaExtra(self,areaIndex:int):
        '''
        1、若该宫内某一可选数只占一行/列时，对应行/列的其它宫的格子排除该可选数
        2、若该宫内某一可选数只占两行/列时，且其它宫该可选数亦只占相同的两行/列时，则剩余的宫中剩余那行/列外的格子的该可选数排除
        3、若该宫内2/3/4/5/6/7/8的格子的可选数<=2/3/4/5/6/7/8时，清除其它格子的该可选数
        3a、若<=8,则最后一格为必填，会被推断出来而不用如此处理。若<=7，则剩作两格满足<=2的情况而不用如此处理。
        3b、同理只需要处理<=4的情况，<=5/6/7会由<=4/3/2的情况推断出
        3c、若处理<=2情况，只需要判定可填位置<=2的格子，同理<=3/4只需要判定<=3/4可填位置的格子
        3d、判断<=2,则从所有<=2的数集中尽可能选所有的两两组合，判断是否位置<=2;其余同理
        3e、选取组合的方法(假定为2):设位置集为array(length>=2)，从集中选任意一个，与剩余的两两组合。排除第一次选取的那个后，再取任意一个，与剩余的两两组合，直至集数=1或=0
        3f、可用递归处理，或考虑非递法实现
        '''
        choiceCounts = [0 for i in range(9)] #记录某可选数的数量
        choicePoints = [[] for i in range(9)] #记录某可选数的坐标
        areaRow = int(areaIndex/3) #宫起始行坐标
        areaColumn = int(areaIndex%3) #宫起始列坐标
        for r in range(3): #统计可选数数量及对应坐标
            for c in range(3):
                index = (areaRow*3+r)*9+(areaColumn*3+c) #计算当前格子Index
                lattice = self.getLatticeByIndex(index)
                if lattice!=None:
                    if lattice.isWritten(): #已写入，不记录该数
                        choiceCounts[lattice.getDisplayNumber()-1]=-1
                    else:
                        numberChoices = lattice.getAlternativeNumbers()
                        for i in range(9):
                            if numberChoices[i]!=0 and choiceCounts[i]!=-1:
                                choiceCounts[i]+=1 #计数+1
                                choicePoints[i].append(lattice.getLatticeIndex()) #记录坐标
        #Point1,Point
        for i in range(9):
            if choiceCounts[i]==2 or choiceCounts[i]==3:
                pass
                #检查是否在同一行/列
                #清除行/列
            elif choiceCounts[i]>=4 and choiceCounts[i]<=6:
                #检查是否在同两行/列
                #获取判断剩两宫并清除
                pass

def getCombination(numberList:list[int],combineCount:int)->list|None:
    '''
    返回给定集合的组合集，若combineCount=2，则为两两组合不重复的集
    '''
    if len(numberList)<combineCount: #不符合组合条件
        return None
    if combineCount<=1: #已组合或不用组合
        return copy.deepcopy(numberList)
    combineList = []
    hasSelected = [] #当前已被选取的数
    canSelectedStack = [copy.deepcopy(numberList)]
    while len(canSelectedStack)>0:
        selectStack = copy.deepcopy(canSelectedStack[-1])
        hasSelected.append(selectStack[0])