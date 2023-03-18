from core.sudoku_lattice import *

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
        for teRow in range(9):
            for teColumn in range(9):
                lattiecIndex = teRow*9+teColumn
                self.numberMatrix.append(Lattice(latticeIndex = lattiecIndex))

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

    def getLatticeByIndex(self,index:int)->Lattice:
        '''
        返回当前下标对应的格子
        '''
        assert index>=0 and index <81, {"错误":"下标不合法"}
        return self.numberMatrix[index]

    def setLatticeDisplay(self,latticIndex:int,displayNumber:int):
        '''
        将value写入第index个格子
        '''
        self.getLatticeByIndex(latticIndex).setDisplayNumber(displayNumber)

    def clearLattice(self,latticIndex:int):
        '''
        擦除某一格子
        '''
        lattice = self.getLatticeByIndex(latticIndex)
        if lattice.canClear():
            displayNumber = lattice.getDisplayNumber()
            latticeRow = lattice.getRowIndex() #格子所在行/列
            latticeCloumn = lattice.getColumnIndex() #格子所在列
            lattice.clearDisplay()#擦除
            for teIndex in range(9):
                #遍历格子所在行/列，恢复当行/列的格子的可选数
                self.getLatticeByIndex(latticeRow*9+teIndex).backChoiceNumber(displayNumber)
                self.getLatticeByIndex(teIndex*9+latticeCloumn).backChoiceNumber(displayNumber)
            areaRowStart = lattice.getStartAreaRow() #计算宫起始行坐标
            areaColumnStart = lattice.getStartAreaColumn() #计算宫起如列坐标
            for teRow in range(3):
                for teColumn in range(3):
                    #恢复该宫内格子的可选数
                    self.getLatticeByIndex((areaRowStart+teRow)*9+(areaColumnStart+teColumn)).backChoiceNumber(displayNumber)

    def inferRowChoice(self,rowIndex:int):
        '''
        1、行可选数推测，基础
        2、若该行某一数只出现了一次，则清空该格的其它可选数
        '''
        existNumbers = self.getExistNumbersByLine(rowIndex,isRow=True)#获取已填数列表，排除被标记为错误的
        #根据已填数列表排除可选数
        for teColumn in range(9):
            latticeIndex = rowIndex*9+teColumn
            self.getLatticeByIndex(latticeIndex).clearChoiceByList(existNumbers)

        choiceNumberCounts = self.countChoiceNumbersByLine(rowIndex,isRow=True)#统计当前行可选数的数量
        #若该行某一数只出现了一次，则清空该格的其它可选数
        for choiceIndex in range(9):
            if choiceNumberCounts[choiceIndex]==1:
                self.findClearChoice(rowIndex,choiceIndex+1,isRow=True)

    def countChoiceNumbersByLine(self,index:int,isRow:bool)->list[int]:
        '''
        统计某一行/列可选数的数量
        '''
        choiceNumberCounts = [0 for i in range(9)]
        for teIndex in range(9):
            latticeIndex = index*9+teIndex if isRow else teIndex*9+index #计算格子下标
            lattice = self.getLatticeByIndex(latticeIndex)
            if lattice.isDisplayEmpty():
                for choiceNumber in lattice.getAlternativeNumbers():
                    if choiceNumber!=NUMBER_EMPTY:
                        choiceNumberCounts[choiceNumber-1]+=1
        return choiceNumberCounts

    def getExistNumbersByLine(self,index:int,isRow:bool)->list[int]:
        '''
        获得某一行/列所有已填的数
        '''
        existNumbers = []
        for teIndex in range(9):
            latticeIndex = index*9+teIndex if isRow else index+teIndex*9 #计算格子下标
            lattice = self.getLatticeByIndex(latticeIndex)
            if lattice.isWritten():
                existNumbers.append(lattice.getDisplayNumber()) #记录已填
        return existNumbers

    def inferColumnChoice(self,columnIndex:int):
        '''
        1、列可选数推测
        2、若该列某一数只出现了一次，则清空该格的其它可选数
        '''
        existNumbers = self.getExistNumbersByLine(columnIndex,isRow=False)#获取已填数列表，排除被标记为错误的
        #根据已填数列表排除可选数
        for i in range(9):
            self.getLatticeByIndex(columnIndex+i*9).clearChoiceByList(existNumbers)

        choiceNumberCounts = self.countChoiceNumbersByLine(columnIndex,isRow=False)#统计当前列可选数的数量
        #若该列某一数只出现了一次，则清空该格的其它可选数
        for choiceIndex in range(9): #遍历所有的数的统计
            if choiceNumberCounts[choiceIndex]==1: #唯一可填
                self.findClearChoice(columnIndex,choiceIndex+1,isRow=False)#清除该格子除该数外的可选数

    def findClearChoice(self,index:int,choiceNumber:int,isRow:bool):
        '''
        在某一行/列找个格子的可选数存在choiceNumber的格子，清空该格子除该数外的其它可选数
        只处理匹配到的第一个格子
        '''
        for teIndex in range(9):
            latticeIndex = index*9+teIndex if isRow else teIndex*9+index
            lattice = self.getLatticeByIndex(latticeIndex)
            if choiceNumber in lattice.getAlternativeNumbers():
                lattice.clearChoiceByNumber(choiceNumber)
                return

    def getAreaStartPoint(self,areaIndex:int)->tuple:
        '''
        获得该宫的起始坐标
        '''
        return (int(areaIndex/3),int(areaIndex%3))

    def getExistNumbersByArea(self,areaIndex:int)->list[int]:
        '''
        获得某一个宫内所有已填数
        '''
        existNumbers = [] #记录已存在的数字
        areaRow,areaColumn = self.getAreaStartPoint(areaIndex) #宫起始坐标
        for teRow in range(3):
            for teColumn in range(3):
                index = (areaRow*3+teRow)*9+(areaColumn*3+teColumn) #计算格子坐标
                lattice = self.getLatticeByIndex(index)
                if lattice.isWritten():
                    existNumbers.append(lattice.getDisplayNumber()) #记录已存在的数字
        return existNumbers

    def inferAreaChoice(self,areaIndex:int):
        '''
        宫可选数推测
        若某一宫的某一个数已填，则剩余格子的可选数排除该数
        '''
        existNumbers = self.getExistNumbersByArea(areaIndex) #记录已存在的数字
        areaRow,areaColumn = self.getAreaStartPoint(areaIndex) #宫起始坐标
        for teRow in range(3):
            for teColumn in range(3):
                latticeIndex = (areaRow*3+teRow)*9+(areaColumn*3+teColumn) #计算格子坐标
                self.getLatticeByIndex(latticeIndex).clearChoiceByList(existNumbers) #排除格子的可选数

    def inferLatticeChoice(self,areaIndex:int):
        '''
        若某一宫内某一个数只在某一格内可填，清空该格和宫外的可选数
        '''
        areaRow,areaColumn = self.getAreaStartPoint(areaIndex) #宫起始坐标
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
                lattice = self.getLatticeByIndex(choiceLattice[i])
                lattice.clearChoiceByNumber(i+1) #清空该格子的其它数
                column = lattice.getColumnIndex() #获取格子的列数
                row = lattice.getRowIndex() #获取格子的行数
                for teIndex in range(9): #清空该格子外的可选数
                    rowLatticeIndex = row*9 + teIndex #计算行相关的格子下标
                    columnLatticeIndex = teIndex*9 + column #计算列相关的格子下标
                    if rowLatticeIndex!= choiceLattice[i]: #不处理当前格子
                        self.getLatticeByIndex(rowLatticeIndex).clearChoiceByList([i+1]) #只清除当前可选数
                    if columnLatticeIndex!=choiceLattice[i]: #不处理当前格子
                        self.getLatticeByIndex(columnLatticeIndex).clearChoiceByList([i+1])#只清除当前可选数

    def inferAreaExtra(self,areaIndex:int):
        '''
        1、若该宫内某一可选数只占一行/列时，对应行/列的其它宫的格子排除该可选数
        2、若该宫内某一可选数只占两行/列时，且下一宫的该数亦只出现在同样的两行/列中，则对应行/列的其它宫的格子排除该可选数
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
        #若该宫内某一可选数只占一行/列时，对应行/列的其它宫的格子排除该可选数
        for i in range(9):
            if choiceCounts[i]==2 or choiceCounts[i]==3:
                #检查是否在同一行
                rowIndexCheck = self.isSameRow(choicePoints[i])
                #清除行
                if rowIndexCheck!=-1:
                    for cloumnIndex in range(9):
                        latticeIndex = rowIndexCheck*9+cloumnIndex
                        if latticeIndex not in choicePoints[i]:
                            self.numberMatrix[latticeIndex].clearChoiceByList([i+1])
                #检查是否在同一列
                columnIndexCheck = self.isSameColumn(choicePoints[i])
                #清除列
                if columnIndexCheck!=-1:
                    for rowIndex in range(9):
                        latticeIndex = rowIndex*9+columnIndexCheck
                        if latticeIndex not in choicePoints[i]:
                            self.numberMatrix[latticeIndex].clearChoiceByList([i+1])
        #若该宫内某一可选数只占一行/列时，对应行/列的其它宫的格子排除该可选数
        for i in range(9):
            if choiceCounts[i]>=2 and choiceCounts[i]<=6:
                rowIndexChecks = self.isSameTwoRows(choicePoints[i])
                if len(rowIndexChecks)==2: #只有两行时才需要处理
                    nextAreaIndex = self.getNextArea(areaIndex,isRow=True) #获取下一宫下标
                    nextRowIndex = self.getOtherRowCloumn(rowIndexChecks) #获取另一行
                    isExistNumber = True
                    for nextIndex in range(9):
                        latticeIndex = nextRowIndex*9+nextIndex #计算格子下标
                        lattice = self.getLatticeByIndex(latticeIndex)


    def getNextArea(self,areaIndex:int,isRow:bool)->int:
        '''
        获得当宫的下一行/列的宫
        '''
        areaRow,areaColumn = self.getAreaStartPoint(areaIndex) #宫起始坐标
        if isRow:
            return areaRow*3+(areaColumn+1)%3
        else:
            return ((areaRow+1)%3)*3+areaColumn

    def isSameRow(self,indexList:list[int])->int:
        '''判断是否在同一行'''
        if indexList==None or len(indexList)==0:
            return -1
        rowIndex = int(indexList[0]/9)
        for index in indexList:
            if rowIndex!=int(index/9):
                return -1
        return rowIndex

    def isSameColumn(self,indexList:list[int])->int:
        '''判断是否在同一列'''
        if indexList==None or len(indexList)==0:
            return -1
        columnIndex = int(indexList[0]%9)
        for index in indexList:
            if columnIndex!=int(index%9):
                return -1
        return columnIndex

    def isSameTwoRows(self,indexList:list[int])->list[int]:
        '''判断是否在同两行'''
        if indexList==None or len(indexList)==0:
            return []
        rowIndexs = []
        for index in indexList:
            rowIndex = int(index/9)
            if rowIndex not in rowIndexs:
                if len(rowIndexs)<=2:
                    rowIndexs.append(rowIndex)
                else:
                    return []
        return rowIndexs

    def isSameTwoColumns(self,indexList:list[int])->list[int]:
        '''判断是否在同两列'''
        if indexList==None or len(indexList)==0:
            return []
        cloumnIndexs = []
        for index in indexList:
            columnIndex = int(index%9)
            if columnIndex not in cloumnIndexs:
                if len(cloumnIndexs)<=2:
                    cloumnIndexs.append(columnIndex)
                else:
                    return []
        return cloumnIndexs

    def getOtherRowCloumn(self,indexList:list[int])->int:
        '''获取其它行/列'''
        if len(indexList)==2:
            areaIndex = int(indexList[0]/3) #0,1,2
            return (areaIndex*3+1)*3-indexList[0]-indexList[1]
        else:
            return -1

def getCombination(numberList:list[int],combineCount:int)->list:
    '''
    一、返回给定集合的组合集，若combineCount=2，则为两两组合不重复的集
    1，存储所有组合可能的集为combineList
    2，存储当前遍历下标的集为indexList，且len=组合数，初始值为0，1，2依次递增
    3，开始循环，直至indexList(0)=数集长度-组合数；
    4，将当前indexList所指的数作为一次组合添加进combineList中。
    5，执行indexList的自增
    6，循环结束，将当前indexList所指的数作为一次组合添加进combineList中，
    7，返回组合集combineList

    二，indexList的自增
    1，开始循环，从0到组合减1，变量名为time
    2，若当前位的下标值指的不是最后一位，且后一位的下标不等于当前下标值+1，则自增；后续的下标值为当前值递增
    3，若是最后一位，则访问前一位
    '''
    if len(numberList)<combineCount: #不符合组合条件
        return None
    if combineCount<=1: #已组合或不用组合
        return copy.deepcopy(numberList)
    combineList = []
    indexList = [i for i in range(combineCount)]
    while indexList[0]<len(numberList)-combineCount:
        combineList.append([numberList[i] for i in indexList])
        #indexList自增
        tIndex = combineCount-1 #index当前处理的下标
        while tIndex>=0:
            if tIndex == combineCount-1: #最后一项
                if indexList[tIndex]< len(numberList)-1:
                    indexList[tIndex]+=1 #自增成功
                    break
                else:
                    tIndex-=1 #自增失败，切换至上一个下标处理
            else: #非最后一项
                if indexList[tIndex]<indexList[tIndex+1]-1: #可自增
                    teIndexValue = indexList[tIndex]
                    for addIndex in range(combineCount-tIndex):
                        indexList[tIndex+addIndex]=teIndexValue+1+addIndex #当前及后续下标顺序递增
                    break
                else: #不可自增
                    tIndex-=1
    combineList.append([numberList[i] for i in indexList])
    return combineList