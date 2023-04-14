#coding=utf-8

import copy
from core.sudoku_lattice import *
from core.sudoku_record import *
from core.sudoku_base import *

'''
数独整体数据结构
'''
class Sudoku(object):

    def __init__(self) -> None:
        #初始化棋盘格子数据
        self.numberMatrix = [Lattice(latticeIndex) for latticeIndex in runAll()]
        self.record = Record() #日志结构

    def getLatticeByPoint(self,pointX:int,pointY:int)->Lattice|None:
        '''
        根据画布当前的坐标返回对应的格子
        pointX:横坐标
        pointY:纵坐标
        '''
        for lattice in self.numberMatrix:
            if lattice.isMatch(pointX=pointX,pointY=pointY):
                return lattice
        return None

    def getLatticeByLine(self,rowIndex:int,columnIndex:int)->Lattice:
        '''
        返回当前下标对应的格子
        '''
        return self.getLattice(toIndex(rowIndex,columnIndex))

    def getLattice(self,latticeIndex:int)->Lattice:
        '''
        返回当前下标对应的格子
        '''
        assert isEqualOrIn(latticeIndex,0,80), {"错误":"下标不合法"}
        return self.numberMatrix[latticeIndex]

    def setLatticeDisplay(self,latticIndex:int,displayNumber:int):
        '''
        将value写入第index个格子
        '''
        if self.getLattice(latticIndex).setDisplay(displayNumber):
            self.record.addRecord(RecordContent(ACTION_INPUT_NUMBER,latticIndex,displayNumber,None))

    def clearLattice(self,latticIndex:int):
        '''
        擦除某一格子
        '''
        lattice = self.getLattice(latticIndex)
        if lattice.canClear():
            displayNumber = lattice.getDisplay()
            if lattice.clearDisplay(): #擦除
                self.record.addRecord(RecordContent(ACTION_CLEAR_NUMBER,latticIndex,displayNumber,None))

            #遍历格子所在行/列，恢复当行/列的格子的可选数
            for latticeIndex in runLine(lattice.getRowIndex(),is_Row=True):
                self.getLattice(latticeIndex).backChoice(displayNumber)
            for latticeIndex in runLine(lattice.getColumnIndex(),is_Row=False):
                self.getLattice(latticeIndex).backChoice(displayNumber)

            #恢复该宫内格子的可选数
            for latticeIndex in runArea(lattice.getAreaIndex()):
                self.getLattice(latticeIndex).backChoice(displayNumber)

    def clearLineByIndex(self,lineIndex:int,choiceIndex:int,isRow:bool,extraIndexs:list[int]|int,actionType:int):
        '''
        清除某行/列格子的某可选数，不处理extraIndexs所在格子
        '''
        for latticeIndex in runLine(lineIndex,isRow):
            lattice = self.getLattice(latticeIndex)
            if (isinstance(extraIndexs,int) and latticeIndex!=extraIndexs) or (isinstance(extraIndexs,list) and latticeIndex not in extraIndexs):
                if lattice.setChoiceEmpty(choiceIndex):
                    self.record.addRecord(RecordContent(actionType,latticeIndex,choiceIndex,{"lineIndex":lineIndex,"isRow":isRow,"extraIndexs":extraIndexs}))

    def clearLineByArea(self,lineIndex:int,choiceIndex:int,isRow:bool,extraAreas:list[int]|int,extractInfo:any):
        '''
        清除某行/列格子的某可选数，不处理extraIndexs所在宫的格子
        '''
        for latticeIndex in runLine(lineIndex,isRow):
            lattice = self.getLattice(latticeIndex)
            if (isinstance(extraAreas,int) and lattice.getAreaIndex()==extraAreas) or lattice.getAreaIndex() not in extraAreas:
                if lattice.setChoiceEmpty(choiceIndex):
                    self.record.addRecord(RecordContent(ACTION_AREA_LINE_TWO,latticeIndex,choiceIndex,{"isRow":isRow,"lineChecks":extractInfo,"extraAreas":extraAreas}))

    def inferLineChoiceBase(self,lineIndex:int,isRow:bool):
        '''
        行/列可选数推测，基础
        '''
        existNumbers = self.getExistsByLine(lineIndex,isRow=isRow)#获取已填数列表，排除被标记为错误的
        #根据已填数列表排除可选数
        for latticeIndex in runLine(lineIndex,isRow):
            lattice = self.getLattice(latticeIndex)
            clearValue = lattice.clearChoiceByExists(existNumbers)
            if not isEqualOrIn(clearValue,0):
                actionType = ACTION_ROW_LINE_BASE if isRow else ACTION_COLUMN_LINE_BASE
                self.record.addRecord(RecordContent(actionType,lineIndex,existNumbers,{"lineIndex":lineIndex,"existNumbers":existNumbers}))

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
        actionType = ACTION_ROW_COMBINE if isRow else ACTION_COLUMN_COMBINE
        for combineCount in range(2,4+1): #遍历2到4个数组合的可能
            combineSet = getCombination(choiceIndexs,combineCount)
            if combineSet==None or len(combineSet)<1:
                continue
            for combineQueue in combineSet:
                if self.isCombineLattice(choicePoints,combineQueue): #满足组合条件
                    combinePoint = choicePoints[combineQueue[0]] #获得组合的格子
                    for latticeIndex in combinePoint:
                        clearValues = self.getLattice(latticeIndex).clearChoiceByIndexs(combineQueue)
                        if not isEqualOrIn(clearValues,0):
                            self.record.addRecord(RecordContent(actionType,latticeIndex,clearValues,{"lineIndex":lineIndex,"combineQueue":combineQueue,"combinePoint":combinePoint}))

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

    def countChoicesByLine(self,lineIndex:int,isRow:bool)->list[int]:
        '''
        统计某一行/列可选数的数量
        '''
        choiceNumberCounts = [0 for i in range(9)]
        for latticeIndex in runLine(lineIndex,isRow):
            lattice = self.getLattice(latticeIndex)
            if lattice.isDisplayEmpty():
                for choiceNumber in lattice.getChoiceNumbers():
                    if not LatticeValue.isEmpty(choiceNumber):
                        choiceNumberCounts[choiceNumber-1]+=1
        return choiceNumberCounts

    def getExistsByLine(self,lineIndex:int,isRow:bool)->list[int]:
        '''
        获得某一行/列所有已填的数
        '''
        existNumbers = []
        for latticeIndex in runLine(lineIndex,isRow):
            lattice = self.getLattice(latticeIndex)
            if lattice.isWritten():
                existNumbers.append(lattice.getDisplay()) #记录已填
        return existNumbers

    def findClearChoice(self,lineIndex:int,choiceNumber:int,isRow:bool):
        '''
        在某一行/列找个格子的可选数存在choiceNumber的格子，清空该格子除该数外的其它可选数
        只处理匹配到的第一个格子
        '''
        actionType = ACTION_ROW_ONLY if isRow else ACTION_CLOUMN_ONLY
        for latticeIndex in runLine(lineIndex,isRow):
            lattice = self.getLattice(latticeIndex)
            if choiceNumber in lattice.getChoiceNumbers():
                clearValues = lattice.clearChoiceByNumber(choiceNumber)
                if not isEqualOrIn(clearValues,0):
                    self.record.addRecord(RecordContent(actionType,lattice.getLatticeIndex(),clearValues,{"lineIndex":lineIndex,"choiceNumber":choiceNumber}))
                return

    def getExistsByArea(self,areaIndex:int)->list[int]:
        '''
        获得某一个宫内所有已填数
        '''
        existNumbers = [] #记录已存在的数字
        for latticeIndex in runArea(areaIndex):
            lattice = self.getLattice(latticeIndex)
            if lattice.isWritten():
                existNumbers.append(lattice.getDisplay()) #记录已存在的数字
        return existNumbers

    def inferAreaChoiceBase(self,areaIndex:int):
        '''
        宫可选数推测
        若某一宫的某一个数已填，则剩余格子的可选数排除该数
        '''
        existNumbers = self.getExistsByArea(areaIndex) #记录已存在的数字
        for latticeIndex in runArea(areaIndex):
            lattice = self.getLattice(latticeIndex)
            clearValues = lattice.clearChoiceByExists(existNumbers) #排除格子的可选数
            if not isEqualOrIn(clearValues,0):
                self.record.addRecord(RecordContent(ACTION_AREA_BASE,lattice.getLatticeIndex(),clearValues,{"existNumbers":existNumbers,"areaIndex":areaIndex}))

    def countChoicePointsByLine(self,lineIndex:int,isRow:bool)->list:
        '''
        统计行/列内可选数出现的位置
        '''
        existNumbers = self.getExistsByLine(lineIndex,isRow=isRow)
        choicePoints = [[] for i in range(9)] #记录可选数坐标
        for latticeIndex in runLine(lineIndex,isRow):
            lattice = self.getLattice(latticeIndex)
            for choiceNumber in lattice.getValidChoices():
                choicePoints[choiceNumber-1].append(latticeIndex)#记录当前可选数的格子位置
        #清空已填写数的位置
        for number in existNumbers:
            if not LatticeValue.isEmpty(number):
                choicePoints[number-1]=[]
        return choicePoints

    def countChoicePointsByArea(self,areaIndex:int)->list:
        '''
        统计宫内可选数出现的位置
        '''
        existNumbers = self.getExistsByArea(areaIndex)
        choicePoints = [[] for i in range(9)] #记录可选数坐标
        for latticeIndex in runArea(areaIndex):
            lattice = self.getLattice(latticeIndex)
            for choiceNumber in lattice.getValidChoices():
                choicePoints[choiceNumber-1].append(latticeIndex)#记录当前可选数的格子位置
        #清空已填写数的位置
        for number in existNumbers:
            choicePoints[number-1]=[]
        return choicePoints

    def inferAreaChoiceOnly(self,areaIndex:int):
        '''
        若某一宫内某一个数只在某一格内可填，清空该格和宫外的可选数
        '''
        choicePoints = self.countChoicePointsByArea(areaIndex) #获取该宫的所有可选数
        for choiceIndex in range(9): #遍历所有可选数
            choicePoint = choicePoints[choiceIndex]
            if len(choicePoint)!=1: #不只在某一格可填的，不处理
                continue
            latticeIndex = choicePoint[0]
            lattice = self.getLattice(latticeIndex) #获取该格子下标
            clearValues = lattice.clearChoiceByNumber(choiceIndex+1) #清空该格子的其它数
            if not isEqualOrIn(clearValues,0): #非零时表示有变动
                self.record.addRecord(RecordContent(ACTION_AREA_ONLY_IN,latticeIndex,clearValues,{"choiceIndex":choiceIndex}))
            row,column = lattice.getLatticPoint()
            self.clearLineByIndex(row,choiceIndex,True,latticeIndex,ACTION_AREA_ONLY_LINE)
            self.clearLineByIndex(column,choiceIndex,False,latticeIndex,ACTION_AREA_ONLY_LINE)

    def inferAreaChoiceLine(self,areaIndex:int,isRow=True):
        '''
        1、若该宫内某一可选数只占一行/列时，对应行/列的其它宫的格子排除该可选数
        2、若该宫内某一可选数只占两行/列时，且下一宫的该数亦只出现在同样的两行/列中，则对应行/列的其它宫的格子排除该可选数
        '''
        choicePoints = self.countChoicePointsByArea(areaIndex)
        for choiceIndex in range(9):
            choicePoint = choicePoints[choiceIndex]
            if isEqualOrIn(choicePoint,2,6):
                lineChecks = isTwoRowCloumns(choicePoint,isRow=isRow)#检查是否在同一行
                #清除行
                if isEqualOrIn(lineChecks,1):
                    self.clearLineByIndex(lineChecks[0],choiceIndex,isRow=isRow,extraIndexs=choicePoint,actionType=ACTION_AREA_LINE_ONE)
                elif isEqualOrIn(lineChecks,2): #只有两行时才需要处理
                    nextAreaIndex = getNextArea(areaIndex,isRow=isRow) #获取下一宫下标
                    rowPoints = self.countChoicePointsByArea(nextAreaIndex)
                    rowPoint = rowPoints[choiceIndex]
                    if isEqualOrIn(rowPoint,2,6):
                        nextLineChecks = isTwoRowCloumns(rowPoint,isRow=isRow)
                        if isEqualOrIn(nextLineChecks,2) and isListContains(lineChecks,nextLineChecks):
                            for lineCheck in lineChecks:
                                self.clearLineByArea(lineCheck,choiceIndex,isRow=isRow,extraAreas=[areaIndex,nextAreaIndex],extractInfo = lineChecks)

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
                        lattice = self.getLattice(latticeIndex)
                        clearValues = lattice.clearChoiceByIndexs(combineQueue)
                        if not isEqualOrIn(clearValues,0):
                            self.record.addRecord(RecordContent(ACTION_AREA_COMBINE,lattice.getLatticeIndex(),clearValues,{"areaIndex":areaIndex,"combinePoint":combinePoint,"combineQueue":combineQueue}))

    def inferXWing(self,lineIndex:int,isRow:bool):
        '''
        若某一数分别在两行/列的两个格子中可填，且属同两列/行，则对应列/行影响范围内的格子排除该可选数
        '''
        if isEqualOrIn(lineIndex,8):
            return #最后一行/列，不用处理
        choicePoints=self.countChoicePointsByLine(lineIndex,isRow=isRow)
        choiceIndexs = getValidIndexs(choicePoints,2,2)
        for checkLine in range(lineIndex+1,9):
            checkPoints = self.countChoicePointsByLine(checkLine,isRow=isRow)
            for choiceIndex in choiceIndexs:
                checkPoint = copy.deepcopy(checkPoints[choiceIndex])
                if (not isEqualOrIn(checkPoint,2)) or (not isEqualOrIn(choicePoints[choiceIndex],2)):
                    continue
                checkPoint.extend(choicePoints[choiceIndex])
                checkLines = isTwoRowCloumns(checkPoint,isRow=not isRow)
                if not isEqualOrIn(checkLines,2):
                    continue
                self.clearLineByIndex(checkLines[0],choiceIndex,isRow=not isRow,extraIndexs=checkPoint,actionType=ACTION_X_WING)
                self.clearLineByIndex(checkLines[1],choiceIndex,isRow=not isRow,extraIndexs=checkPoint,actionType=ACTION_X_WING)

    def countChoicePointsByAll(self,count:int)->list[int]:
        '''
        获取对应可选数字剩余为count的格子的下标
        '''
        choicePoints = []
        for latticeIndex in runAll():
            if isEqualOrIn(self.getLattice(latticeIndex).getValidChoices(),count):
                choicePoints.append(latticeIndex)
        return choicePoints

    def isTwoAreas(self,combineQueue:list)->list[int]:
        areaIndexs = []
        for latticeIndex in combineQueue:
            lattice = self.getLattice(latticeIndex)
            if lattice.getAreaIndex() not in areaIndexs:
                areaIndexs.append(lattice.getAreaIndex())
        return areaIndexs

    def getXYWingChoice(self,combineQueue:list[int],isRow:bool)->dict:
        xyWingInfo = {}
        lattices = [self.getLattice(latticeIndex) for latticeIndex in combineQueue]
        lineIndexs = [lattice.getRowIndex() for lattice in lattices] if isRow else [lattice.getRowIndex() for lattice in lattices]
        xyWingInfo["mainLine"] = lineIndexs[0] if lineIndexs[0]==lineIndexs[1] or lineIndexs[0]==lineIndexs[2] else lineIndexs[1] #获得主线

    def inferXYWing(self):
        '''
        使用XYWING推测
        '''
        choicePoints = self.countChoicePointsByAll(2) #获取下标仅为2的格子
        combineQueueSet = getCombination(choicePoints,3) #获取所有3*3组合可能
        for combineQueue in combineQueueSet:
            if self.isCombineLattice(choicePoints,combineQueue):
                rowLines = isTwoRowCloumns(combineQueue,isRow=True) #判断是否分属两行
                columnlines = isTwoRowCloumns(combineQueue,isRow=False)#判断是否分属两列
                areaIndexs = self.isTwoAreas(combineQueue) #判断所属宫
                if isEqualOrIn(areaIndexs,1): #在同一宫，属宫内组合的情况
                    continue
                elif isEqualOrIn(rowLines,1) or isEqualOrIn(columnlines,1): #在同一行/列，属行内组合情况
                    continue
                elif isEqualOrIn(rowLines,2) and isEqualOrIn(areaIndexs,2): #两行+两宫的情况
                    pass
                elif isEqualOrIn(columnlines,2) and isEqualOrIn(areaIndexs,2): #两列+两宫的情况
                    pass
                elif isEqualOrIn(columnlines,2) and isEqualOrIn(rowLines,2) and isEqualOrIn(areaIndexs,3):
                    pass

    def isEmptyRecord(self)->bool:
        '''
        判断记录是否为空
        '''
        return self.record.isEmpty()

    def getRecordText(self,index:int=-1)->str:
        '''
        获取操作记录文本
        '''
        return self.record.getRecordInfo(index)

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

def isEqualOrIn(input:list|int,value:int,maxValue:int=None)->bool:
    '''
    判断列表长度是否符合，若maxlength==None，则判断与length是否相等，否则判断范围是否在[length,maxLength]
    '''
    size = input if isinstance(input,int) else len(input)
    if maxValue == None:
        return size==value
    return size>=value and size<=maxValue;

def getValidIndexs(choicePoints:list,minSize:int,maxSize:int)->list[int]:
    '''
    记录有效数字下标
    '''
    choiceIndexs = [] #记录有效数字
    for choiceIndex in range(9):
        choicePoint = choicePoints[choiceIndex]
        if isEqualOrIn(choicePoint,minSize,maxSize):
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