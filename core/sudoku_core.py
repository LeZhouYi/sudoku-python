import copy
from core.sudoku_lattice import *

'''
数独整体数据结构
'''
class Sudoku(object):

    def __init__(self) -> None:
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

    def getLattice(self,rowIndex:int,columnIndex:int)->Lattice:
        '''
        返回当前下标对应的格子
        '''
        latticeIndex = rowIndex*9+columnIndex
        return self.getLatticeByIndex(latticeIndex)

    def getLatticeByIndex(self,latticeIndex:int)->Lattice:
        '''
        返回当前下标对应的格子
        '''
        assert latticeIndex>=0 and latticeIndex <81, {"错误":"下标不合法"}
        return self.numberMatrix[latticeIndex]

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
            latticeRow,latticeCloumn = lattice.getLatticPoint() #格子所在位置
            lattice.clearDisplay()#擦除
            for teIndex in range(9):
                #遍历格子所在行/列，恢复当行/列的格子的可选数
                self.getLattice(latticeRow,teIndex).backChoiceNumber(displayNumber)
                self.getLattice(teIndex,latticeCloumn).backChoiceNumber(displayNumber)
            areaRowStart,areaColumnStart = self.getAreaStartPoint(lattice.getAreaIndex()) #宫起始坐标
            for teRow in range(3):
                for teColumn in range(3):
                    #恢复该宫内格子的可选数
                    self.getLattice(areaRowStart+teRow,areaColumnStart+teColumn).backChoiceNumber(displayNumber)

    def inferLineChoice(self,lineIndex:int,isRow:bool):
        '''
        1、行/列可选数推测，基础
        2、若该行/列某一数只出现了一次，则清空该格的其它可选数
        '''
        existNumbers = self.getExistNumbersByLine(lineIndex,isRow=isRow)#获取已填数列表，排除被标记为错误的
        #根据已填数列表排除可选数
        for teIndex in range(9):
            if isRow:
                self.getLattice(lineIndex,teIndex).clearChoiceByList(existNumbers)
            else:
                self.getLattice(teIndex,lineIndex).clearChoiceByList(existNumbers)

        choiceNumberCounts = self.countChoiceNumbersByLine(lineIndex,isRow=isRow)#统计当前行可选数的数量
        #若该行/列某一数只出现了一次，则清空该格的其它可选数
        for choiceIndex in range(9):
            if choiceNumberCounts[choiceIndex]==1:
                self.findClearChoice(lineIndex,choiceIndex+1,isRow=isRow)
        choicePoints = self.countChoicePointsByLine(lineIndex,isRow=isRow)
        choiceIndexs = [] #记录有效数字
        for choiceIndex in range(9):
            choicePoint = choicePoints[choiceIndex]
            if len(choicePoint)>=2 and len(choicePoint)<=4:
                choiceIndexs.append(choiceIndex)
        for combineCount in range(2,4+1):
            combineSet = getCombination(choiceIndexs,combineCount)
            if combineSet!=None and len(combineSet)>=1:
                for combineQueue in combineSet:
                    if self.isCombineLattice(choicePoints,combineQueue): #满足组合条件
                        combinePoint = choicePoints[combineQueue[0]] #获得组合的格子
                        for latticeIndex in combinePoint:
                            lattice = self.getLatticeByIndex(latticeIndex)
                            for choiceIndex in range(9):
                                if choiceIndex not in combineQueue:
                                    lattice.setAlternativeNumberEmpty(choiceIndex)

    def isCombineLattice(self,choicePoints:list,combineQueue:list[int])->bool:
        '''
        判断当前的组合是否满足n,n组合的条件，即n格内只有n个数可填
        '''
        combineCount = len(combineQueue)
        latticeIndexs = []
        for combineIndex in combineQueue:
            for latticeIndex in choicePoints[combineIndex]:
                if latticeIndex not in latticeIndexs:
                    latticeIndexs.append(latticeIndex)
        return len(latticeIndexs)==combineCount

    def countChoiceNumbersByLine(self,index:int,isRow:bool)->list[int]:
        '''
        统计某一行/列可选数的数量
        '''
        choiceNumberCounts = [0 for i in range(9)]
        for teIndex in range(9):
            lattice = self.getLattice(index,teIndex) if isRow else self.getLattice(teIndex,index)
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
            lattice = self.getLattice(index,teIndex) if isRow else self.getLattice(teIndex,index)
            if lattice.isWritten():
                existNumbers.append(lattice.getDisplayNumber()) #记录已填
        return existNumbers

    def findClearChoice(self,index:int,choiceNumber:int,isRow:bool):
        '''
        在某一行/列找个格子的可选数存在choiceNumber的格子，清空该格子除该数外的其它可选数
        只处理匹配到的第一个格子
        '''
        for teIndex in range(9):
            lattice = self.getLattice(index,teIndex) if isRow else self.getLattice(teIndex,index)
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
                lattice = self.getLattice(areaRow*3+teRow,areaColumn*3+teColumn)
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
                self.getLattice(areaRow*3+teRow,areaColumn*3+teColumn).clearChoiceByList(existNumbers) #排除格子的可选数

    def countChoicePointsByLine(self,lineIndex:int,isRow:bool)->list:
        '''
        统计行/列内可选数出现的位置
        '''
        existNumbers = [] #记录已存在数
        choicePoints = [[] for i in range(9)] #记录可选数坐标
        for teIndex in range(9):
            lattice = self.getLattice(lineIndex,teIndex) if isRow else self.getLattice(teIndex,lineIndex)
            if lattice.isWritten():
                    existNumbers.append(lattice.getDisplayNumber())
            else:
                alternativeNumbers = lattice.getAlternativeNumbers()
                for choiceIndex in range(9):
                    if alternativeNumbers[choiceIndex]!=NUMBER_EMPTY:
                        choicePoints[choiceIndex].append(lattice.getLatticeIndex())#记录当前可选数的格子位置
        #清空已填写数的位置
        for number in existNumbers:
            if number!=NUMBER_EMPTY:
                choicePoints[number-1]=[]
        return choicePoints

    def countChoicePointsByArea(self,areaIndex:int)->list:
        '''
        统计宫内可选数出现的位置
        '''
        existNumbers = [] #记录已存在数
        choicePoints = [[] for i in range(9)] #记录可选数坐标
        areaRow,areaColumn = self.getAreaStartPoint(areaIndex) #宫起始坐标
        for teRow in range(3):
            for teColumn in range(3):
                lattice = self.getLattice(areaRow*3+teRow,areaColumn*3+teColumn)
                if lattice.isWritten():
                    existNumbers.append(lattice.getDisplayNumber())
                else:
                    alternativeNumbers = lattice.getAlternativeNumbers()
                    for choiceIndex in range(9):
                        if alternativeNumbers[choiceIndex]!=NUMBER_EMPTY:
                            choicePoints[choiceIndex].append(lattice.getLatticeIndex())#记录当前可选数的格子位置
        #清空已填写数的位置
        for number in existNumbers:
            if number!=NUMBER_EMPTY:
                choicePoints[number-1]=[]
        return choicePoints

    def inferLatticeChoice(self,areaIndex:int):
        '''
        若某一宫内某一个数只在某一格内可填，清空该格和宫外的可选数
        '''
        choicePoints = self.countChoicePointsByArea(areaIndex)
        for choiceIndex in range(9):
            choicePoint = choicePoints[choiceIndex]
            if len(choicePoint)==1: #只在某一格可填
                latticeIndex = choicePoint[0]
                lattice = self.getLatticeByIndex(latticeIndex)
                lattice.clearChoiceByNumber(choiceIndex+1) #清空该格子的其它数
                row,column = lattice.getLatticPoint()
                for teIndex in range(9): #清空该格子外的可选数
                    rowLatticeIndex = row*9 + teIndex #计算行相关的格子下标
                    columnLatticeIndex = teIndex*9 + column #计算列相关的格子下标
                    if rowLatticeIndex!= latticeIndex: #不处理当前格子
                        self.getLatticeByIndex(rowLatticeIndex).setAlternativeNumberEmpty(choiceIndex) #只清除当前可选数
                    if columnLatticeIndex!=latticeIndex: #不处理当前格子
                        self.getLatticeByIndex(columnLatticeIndex).setAlternativeNumberEmpty(choiceIndex)#只清除当前可选数

    def inferAreaExtra(self,areaIndex:int):
        '''
        1、若该宫内某一可选数只占一行/列时，对应行/列的其它宫的格子排除该可选数
        2、若该宫内某一可选数只占两行/列时，且下一宫的该数亦只出现在同样的两行/列中，则对应行/列的其它宫的格子排除该可选数
        '''
        choicePoints = self.countChoicePointsByArea(areaIndex)
        for choiceIndex in range(9):
            choicPoint = choicePoints[choiceIndex]
            #若该宫内某一可选数只占一行/列时，对应行/列的其它宫的格子排除该可选数
            #若该宫内某一可选数只占两行/列时，且下一宫的该数亦只出现在同样的两行/列中，则对应行/列的其它宫的格子排除该可选数
            if len(choicPoint)>=2 and len(choicPoint)<=6:
                rowIndexChecks = self.isSameTwoRows(choicPoint)#检查是否在同一行
                #清除行
                if len(rowIndexChecks)==1:
                    for cloumnIndex in range(9):
                        latticeIndex = rowIndexChecks[0]*9+cloumnIndex
                        if latticeIndex not in choicPoint:
                            self.getLatticeByIndex(latticeIndex).setAlternativeNumberEmpty(choiceIndex)
                elif len(rowIndexChecks)==2: #只有两行时才需要处理
                    nextAreaIndex = self.getNextArea(areaIndex,isRow=True) #获取下一宫下标
                    rowPoints = self.countChoicePointsByArea(nextAreaIndex)
                    rowPoint = rowPoints[choiceIndex]
                    if len(rowPoint)>=2 and len(rowPoint)<=6:
                        nextRowIndexChecks = self.isSameTwoRows(rowPoint)
                        if len(nextRowIndexChecks)==2 and nextRowIndexChecks[0] in rowIndexChecks and nextRowIndexChecks[1] in rowIndexChecks:
                            for teRowCheck in rowIndexChecks:
                                for teColumn in range(9):
                                    latticeIndex = teRowCheck*9+teColumn
                                    lattice = self.getLatticeByIndex(latticeIndex)
                                    if lattice.getAreaIndex() not in [areaIndex,nextAreaIndex]:
                                        lattice.setAlternativeNumberEmpty(choiceIndex)

                columnIndexChecks = self.isSameTwoColumns(choicPoint)#检查是否在同一列
                #清除列
                if len(columnIndexChecks)==1:
                    for rowIndex in range(9):
                        latticeIndex = rowIndex*9+columnIndexChecks[0]
                        if latticeIndex not in choicPoint:
                            self.getLatticeByIndex(latticeIndex).setAlternativeNumberEmpty(choiceIndex)
                elif len(columnIndexChecks)==2: #只有两行时才需要处理
                    nextAreaIndex = self.getNextArea(areaIndex,isRow=False) #获取下一宫下标
                    columnPoints = self.countChoicePointsByArea(nextAreaIndex)
                    columnPoint = columnPoints[choiceIndex]
                    if len(columnPoint)>=2 and len(columnPoint)<=6:
                        nextColumnIndexChecks = self.isSameTwoColumns(columnPoint)
                        if len(nextColumnIndexChecks)==2 and nextColumnIndexChecks[0] in columnIndexChecks and nextColumnIndexChecks[1] in columnIndexChecks:
                            for teColumnCheck in columnIndexChecks:
                                for teRow in range(9):
                                    latticeIndex = teRow*9+teColumnCheck
                                    lattice = self.getLatticeByIndex(latticeIndex)
                                    if lattice.getAreaIndex() not in [areaIndex,nextAreaIndex]:
                                        lattice.setAlternativeNumberEmpty(choiceIndex)

    def getNextArea(self,areaIndex:int,isRow:bool)->int:
        '''
        获得当宫的下一行/列的宫
        '''
        areaRow,areaColumn = self.getAreaStartPoint(areaIndex) #宫起始坐标
        if isRow:
            return areaRow*3+(areaColumn+1)%3
        else:
            return ((areaRow+1)%3)*3+areaColumn

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