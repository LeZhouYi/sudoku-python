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
        assert isEqualOrIn(latticeIndex,0,80), {"错误":"下标不合法"}
        return self.numberMatrix[latticeIndex]

    def setLatticeDisplay(self,latticIndex:int,displayNumber:int):
        '''
        将value写入第index个格子
        '''
        self.getLatticeByIndex(latticIndex).setDisplay(displayNumber)

    def clearLattice(self,latticIndex:int):
        '''
        擦除某一格子
        '''
        lattice = self.getLatticeByIndex(latticIndex)
        if lattice.canClear():
            displayNumber = lattice.getDisplay()
            latticeRow,latticeCloumn = lattice.getLatticPoint() #格子所在位置
            lattice.clearDisplay()#擦除
            for teIndex in range(9):
                #遍历格子所在行/列，恢复当行/列的格子的可选数
                self.getLattice(latticeRow,teIndex).backChoice(displayNumber)
                self.getLattice(teIndex,latticeCloumn).backChoice(displayNumber)
            areaRowStart,areaColumnStart = getAreaStartPoint(lattice.getAreaIndex()) #宫起始坐标
            for teRow in range(3):
                for teColumn in range(3):
                    #恢复该宫内格子的可选数
                    self.getLattice(areaRowStart+teRow,areaColumnStart+teColumn).backChoice(displayNumber)

    def clearLineByIndex(self,lineIndex:int,choiceIndex:int,isRow:bool,extraIndexs:list[int]|int):
        '''
        清除某行/列格子的某可选数，不处理extraIndexs所在格子
        '''
        for teIndex in range(9):
            lattice = self.getLattice(lineIndex,teIndex) if isRow else self.getLattice(teIndex,lineIndex)
            if (isinstance(extraIndexs,int) and lattice.getLatticeIndex()==extraIndexs) or lattice.getLatticeIndex() not in extraIndexs:
                lattice.setChoiceEmpty(choiceIndex)

    def clearLineByArea(self,lineIndex:int,choiceIndex:int,isRow:bool,extraAreas:list[int]|int):
        '''
        清除某行/列格子的某可选数，不处理extraIndexs所在宫的格子
        '''
        for teIndex in range(9):
            lattice = self.getLattice(lineIndex,teIndex) if isRow else self.getLattice(teIndex,lineIndex)
            if (isinstance(extraAreas,int) and lattice.getAreaIndex()==extraAreas) or lattice.getAreaIndex() not in extraAreas:
                lattice.setChoiceEmpty(choiceIndex)

    def inferLineChoiceBase(self,lineIndex:int,isRow:bool):
        '''
        行/列可选数推测，基础
        '''
        existNumbers = self.getExistsByLine(lineIndex,isRow=isRow)#获取已填数列表，排除被标记为错误的
        #根据已填数列表排除可选数
        for teIndex in range(9):
            if isRow:
                self.getLattice(lineIndex,teIndex).clearChoiceByExists(existNumbers)
            else:
                self.getLattice(teIndex,lineIndex).clearChoiceByExists(existNumbers)

    def inferLineChoiceOnly(self,lineIndex:int,isRow:bool):
        '''
        若该行/列某一数只出现了一次，则清空该格的其它可选数
        '''
        choiceNumberCounts = self.countChoicesByLine(lineIndex,isRow=isRow)#统计当前行可选数的数量
        #若该行/列某一数只出现了一次，则清空该格的其它可选数
        for choiceIndex in range(9):
            if choiceNumberCounts[choiceIndex]==1:
                self.findClearChoice(lineIndex,choiceIndex+1,isRow=isRow)

    def inferLineChoiceCombine(self,lineIndex:int,isRow:bool):
        '''
        若该行/列某n个数只出现在n个格子，则清空那些格子那些数外的可选数
        '''
        choicePoints = self.countChoicePointsByLine(lineIndex,isRow=isRow)
        choiceIndexs = getValidIndexs(choicePoints,2,4)
        for combineCount in range(2,4+1): #遍历2到4个数组合的可能
            combineSet = getCombination(choiceIndexs,combineCount)
            if combineSet==None or len(combineSet)<1:
                continue
            for combineQueue in combineSet:
                if self.isCombineLattice(choicePoints,combineQueue): #满足组合条件
                    combinePoint = choicePoints[combineQueue[0]] #获得组合的格子
                    for latticeIndex in combinePoint:
                        self.getLatticeByIndex(latticeIndex).clearChoiceByIndexs(combineQueue)

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

    def countChoicesByLine(self,index:int,isRow:bool)->list[int]:
        '''
        统计某一行/列可选数的数量
        '''
        choiceNumberCounts = [0 for i in range(9)]
        for teIndex in range(9):
            lattice = self.getLattice(index,teIndex) if isRow else self.getLattice(teIndex,index)
            if lattice.isDisplayEmpty():
                for choiceNumber in lattice.getChoiceNumbers():
                    if choiceNumber!=NUMBER_EMPTY:
                        choiceNumberCounts[choiceNumber-1]+=1
        return choiceNumberCounts

    def getExistsByLine(self,index:int,isRow:bool)->list[int]:
        '''
        获得某一行/列所有已填的数
        '''
        existNumbers = []
        for teIndex in range(9):
            lattice = self.getLattice(index,teIndex) if isRow else self.getLattice(teIndex,index)
            if lattice.isWritten():
                existNumbers.append(lattice.getDisplay()) #记录已填
        return existNumbers

    def findClearChoice(self,index:int,choiceNumber:int,isRow:bool):
        '''
        在某一行/列找个格子的可选数存在choiceNumber的格子，清空该格子除该数外的其它可选数
        只处理匹配到的第一个格子
        '''
        for teIndex in range(9):
            lattice = self.getLattice(index,teIndex) if isRow else self.getLattice(teIndex,index)
            if choiceNumber in lattice.getChoiceNumbers():
                lattice.clearChoiceByNumber(choiceNumber)
                return

    def getExistsByArea(self,areaIndex:int)->list[int]:
        '''
        获得某一个宫内所有已填数
        '''
        existNumbers = [] #记录已存在的数字
        areaRow,areaColumn = getAreaStartPoint(areaIndex) #宫起始坐标
        for teRow in range(3):
            for teColumn in range(3):
                lattice = self.getLattice(areaRow*3+teRow,areaColumn*3+teColumn)
                if lattice.isWritten():
                    existNumbers.append(lattice.getDisplay()) #记录已存在的数字
        return existNumbers

    def inferAreaChoiceBase(self,areaIndex:int):
        '''
        宫可选数推测
        若某一宫的某一个数已填，则剩余格子的可选数排除该数
        '''
        existNumbers = self.getExistsByArea(areaIndex) #记录已存在的数字
        areaRow,areaColumn = getAreaStartPoint(areaIndex) #宫起始坐标
        for teRow in range(3):
            for teColumn in range(3):
                self.getLattice(areaRow*3+teRow,areaColumn*3+teColumn).clearChoiceByExists(existNumbers) #排除格子的可选数

    def countChoicePointsByLine(self,lineIndex:int,isRow:bool)->list:
        '''
        统计行/列内可选数出现的位置
        '''
        existNumbers = self.getExistsByLine(lineIndex,isRow=isRow)
        choicePoints = [[] for i in range(9)] #记录可选数坐标
        for teIndex in range(9):
            lattice = self.getLattice(lineIndex,teIndex) if isRow else self.getLattice(teIndex,lineIndex)
            for choiceNumber in lattice.getValidChoices():
                choicePoints[choiceNumber-1].append(lattice.getLatticeIndex())#记录当前可选数的格子位置
        #清空已填写数的位置
        for number in existNumbers:
            if number!=NUMBER_EMPTY:
                choicePoints[number-1]=[]
        return choicePoints

    def countChoicePointsByArea(self,areaIndex:int)->list:
        '''
        统计宫内可选数出现的位置
        '''
        existNumbers = self.getExistsByArea(areaIndex)
        choicePoints = [[] for i in range(9)] #记录可选数坐标
        areaRow,areaColumn = getAreaStartPoint(areaIndex) #宫起始坐标
        for teRow in range(3):
            for teColumn in range(3):
                lattice = self.getLattice(areaRow*3+teRow,areaColumn*3+teColumn)
                for choiceNumber in lattice.getValidChoices():
                    choicePoints[choiceNumber-1].append(lattice.getLatticeIndex())#记录当前可选数的格子位置
        #清空已填写数的位置
        for number in existNumbers:
            choicePoints[number-1]=[]
        return choicePoints

    def inferAreaChoiceOnly(self,areaIndex:int):
        '''
        若某一宫内某一个数只在某一格内可填，清空该格和宫外的可选数
        '''
        choicePoints = self.countChoicePointsByArea(areaIndex)
        for choiceIndex in range(9):
            choicePoint = choicePoints[choiceIndex]
            if len(choicePoint)!=1: #不只在某一格可填
                continue
            latticeIndex = choicePoint[0]
            lattice = self.getLatticeByIndex(latticeIndex)
            lattice.clearChoiceByNumber(choiceIndex+1) #清空该格子的其它数
            row,column = lattice.getLatticPoint()
            for teIndex in range(9): #清空该格子外的可选数
                rowLattice = self.getLattice(row,teIndex)
                columnLattice = self.getLattice(teIndex,column)
                if rowLattice.getLatticeIndex()!=latticeIndex: #不处理当前格子
                    rowLattice.setChoiceEmpty(choiceIndex) #只清除当前可选数
                if columnLattice.getLatticeIndex()!=latticeIndex: #不处理当前格子
                    columnLattice.setChoiceEmpty(choiceIndex)#只清除当前可选数

    def inferAreaChoiceLine(self,areaIndex:int,isRow=True):
        '''
        1、若该宫内某一可选数只占一行/列时，对应行/列的其它宫的格子排除该可选数
        2、若该宫内某一可选数只占两行/列时，且下一宫的该数亦只出现在同样的两行/列中，则对应行/列的其它宫的格子排除该可选数
        '''
        choicePoints = self.countChoicePointsByArea(areaIndex)
        for choiceIndex in range(9):
            choicePoint = choicePoints[choiceIndex]
            if isEqualOrIn(len(choicePoint),2,6):
                rowIndexChecks = isTwoRowCloumns(choicePoint,isRow=isRow)#检查是否在同一行
                #清除行
                if isEqualOrIn(len(rowIndexChecks),1):
                    self.clearLineByIndex(rowIndexChecks[0],choiceIndex,isRow=isRow,extraIndexs=choicePoint)
                elif isEqualOrIn(len(rowIndexChecks),2): #只有两行时才需要处理
                    nextAreaIndex = getNextArea(areaIndex,isRow=isRow) #获取下一宫下标
                    rowPoints = self.countChoicePointsByArea(nextAreaIndex)
                    rowPoint = rowPoints[choiceIndex]
                    if isEqualOrIn(len(rowPoint),2,6):
                        nextRowIndexChecks = isTwoRowCloumns(rowPoint,isRow=isRow)
                        if isEqualOrIn(len(nextRowIndexChecks),2) and isListContains(rowIndexChecks,nextRowIndexChecks):
                            for teRowCheck in rowIndexChecks:
                                self.clearLineByArea(teRowCheck,choiceIndex,isRow=isRow,extraAreas=[areaIndex,nextAreaIndex])

    def inferAreaChoiceCombine(self,areaIndex:int):
        '''
        若某宫某n个数只出现在n个格子，则清空那些格子那些数外的可选数
        '''
        choicePoints = self.countChoicePointsByArea(areaIndex)
        choiceIndexs = getValidIndexs(choicePoints,2,4)
        for combineCount in range(2,4+1):
            combineSet = getCombination(choiceIndexs,combineCount)
            if combineSet==None or len(combineSet)<1:
                continue
            for combineQueue in combineSet:
                if self.isCombineLattice(choicePoints,combineQueue): #满足组合条件
                    combinePoint = choicePoints[combineQueue[0]] #获得组合的格子
                    for latticeIndex in combinePoint:
                        self.getLatticeByIndex(latticeIndex).clearChoiceByIndexs(combineQueue)

def isListContains(contains:list,checks:list)->bool:
    '''
    判断checks中的每一项是否出现在contains中
    '''
    if checks==None or len(checks)<1:
        return False
    for item in checks:
        if item not in contains:
            return False
    return True

def isEqualOrIn(input:int,value:int,maxValue:int=None)->bool:
    '''
    判断列表长度是否符合，若maxlength==None，则判断与length是否相等，否则判断范围是否在[length,maxLength]
    '''
    if maxValue == None:
        return input==value
    return input>=value and input<=maxValue;

def getValidIndexs(choicePoints:list,minSize:int,maxSize:int)->list[int]:
    '''
    记录有效数字下标
    '''
    choiceIndexs = [] #记录有效数字
    for choiceIndex in range(9):
        choicePoint = choicePoints[choiceIndex]
        if isEqualOrIn(len(choicePoint),minSize,maxSize):
            choiceIndexs.append(choiceIndex)
    return choiceIndexs

def getAreaStartPoint(areaIndex:int)->tuple:
    '''
    获得该宫的起始坐标
    '''
    return (int(areaIndex/3),int(areaIndex%3))

def getNextArea(areaIndex:int,isRow:bool)->int:
    '''
    获得当宫的下一行/列的宫
    '''
    areaRow,areaColumn = getAreaStartPoint(areaIndex) #宫起始坐标
    if isRow:
        return areaRow*3+(areaColumn+1)%3
    else:
        return ((areaRow+1)%3)*3+areaColumn


def isTwoRowCloumns(indexList:list[int],isRow:bool)->list[int]:
    '''判断是否在同两行/列并返回'''
    if indexList==None or len(indexList)==0:
        return []
    countIndexs = []
    for index in indexList:
        countIndex = int(index/9) if isRow else int(index%9)
        if countIndex not in countIndexs:
            countIndexs.append(countIndex)
    return countIndexs

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