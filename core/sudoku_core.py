#coding=utf-8

import copy
from core.sudoku_lattice import *
from core.sudoku_record import *
from core.sudoku_base import *

class Sudoku(object):
    '''数独整体数据结构'''

    def __init__(self) -> None:
        #初始化棋盘格子数据
        self.numberMatrix = [Lattice(latticeIndex) for latticeIndex in runAll()]
        self.record = Record() #日志结构

    def addRecord(self,actionType:int,index:int,valueList:list[int]|int,extract:any)->None:
        '''添加操作日志'''
        self.record.addRecord(RecordContent(actionType,index,valueList,extract))

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

    def getLattice(self,latticeIndex:int)->Lattice:
        '''
        返回当前下标对应的格子
        '''
        assert isBetween(latticeIndex,0,80), {"错误":"下标不合法"}
        return self.numberMatrix[latticeIndex]

    def setDisplay(self,latticIndex:int,displayNumber:int):
        '''将value写入第index个格子'''
        if self.getLattice(latticIndex).setDisplay(displayNumber):
            self.addRecord(ACTION_INPUT_NUMBER,latticIndex,displayNumber,None)

    def clearLattice(self,latticIndex:int):
        '''擦除某一格子'''
        lattice = self.getLattice(latticIndex)
        if lattice.canClear():
            displayNumber = lattice.getDisplay()
            if lattice.clearDisplay(): #擦除
                self.addRecord(ACTION_CLEAR_NUMBER,latticIndex,displayNumber,None)

            #遍历格子所在行/列，恢复当行/列的格子的可选数
            for latticeIndex in lattice.runLine(isRow=True):
                self.getLattice(latticeIndex).backChoice(displayNumber)
            for latticeIndex in lattice.runLine(isRow=False):
                self.getLattice(latticeIndex).backChoice(displayNumber)

            #恢复该宫内格子的可选数
            for latticeIndex in lattice.runArea():
                self.getLattice(latticeIndex).backChoice(displayNumber)

    def clearLineByIndex(self,lineIndex:int,choiceIndex:int,isRow:bool,extraIndexs:list[int]|int,actionType:int):
        '''清除某行/列格子的某可选数，不处理extraIndexs所在格子'''
        for latticeIndex in runLine(lineIndex,isRow):
            if not isEqualOrIn(latticeIndex,extraIndexs):
                if self.getLattice(latticeIndex).setChoiceEmpty(choiceIndex):
                    self.addRecord(actionType,latticeIndex,choiceIndex,{"lineIndex":lineIndex,"isRow":isRow,"extraIndexs":extraIndexs})

    def clearLineByArea(self,lineIndex:int,choiceIndex:int,isRow:bool,extraAreas:list[int]|int,extractInfo:any):
        '''清除某行/列格子的某可选数，不处理extraIndexs所在宫的格子'''
        for latticeIndex in runLine(lineIndex,isRow):
            if not isEqualOrIn(toArea(latticeIndex),extraAreas):
                if self.getLattice(latticeIndex).setChoiceEmpty(choiceIndex):
                    self.addRecord(ACTION_AREA_LINE_TWO,latticeIndex,choiceIndex,{"isRow":isRow,"lineChecks":extractInfo,"extraAreas":extraAreas})

    def inferLineChoiceBase(self,lineIndex:int,isRow:bool):
        '''行/列可选数推测，基础'''
        existNumbers = self.getExistsByLine(lineIndex,isRow=isRow)#获取已填数列表，排除被标记为错误的
        #根据已填数列表排除可选数
        for latticeIndex in runLine(lineIndex,isRow):
            clearValues = self.getLattice(latticeIndex).clearExistChoices(existNumbers)
            if not isLenEqual(clearValues,0):
                actionType = ACTION_ROW_LINE_BASE if isRow else ACTION_COLUMN_LINE_BASE
                self.addRecord(actionType,lineIndex,existNumbers,{"lineIndex":lineIndex,"existNumbers":existNumbers})

    def inferLineChoiceOnly(self,lineIndex:int,isRow:bool):
        '''若该行/列某一数只出现了一次，则清空该格的其它可选数'''
        choiceNumberCounts = self.countChoicesByLine(lineIndex,isRow=isRow)#统计当前行可选数的数量
        #若该行/列某一数只出现了一次，则清空该格的其它可选数
        for choiceIndex in range(9):
            if choiceNumberCounts[choiceIndex]==1:
                self.findClearChoice(lineIndex,choiceIndex+1,isRow=isRow)

    def inferLineChoiceCombine(self,lineIndex:int,isRow:bool):
        '''若该行/列某n个数只出现在n个格子，则清空那些格子那些数外的可选数'''
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
                        clearValues = self.getLattice(latticeIndex).clearNoListChoices(combineQueue)
                        if not isLenEqual(clearValues,0):
                            self.addRecord(actionType,latticeIndex,clearValues,{"lineIndex":lineIndex,"combineQueue":combineQueue,"combinePoint":combinePoint})

    def isCombineLattice(self,choicePoints:list,combineQueue:list[int])->bool:
        '''判断当前的组合是否满足n,n组合的条件，即n格内只有n个数可填'''
        combineCount = len(combineQueue)
        latticeIndexs = []
        for combineIndex in combineQueue:
            for latticeIndex in choicePoints[combineIndex]:
                if latticeIndex not in latticeIndexs:
                    latticeIndexs.append(latticeIndex)
        return len(latticeIndexs)==combineCount

    def countChoicesByLine(self,lineIndex:int,isRow:bool)->list[int]:
        '''统计某一行/列可选数的数量'''
        choiceNumberCounts = [0 for i in range(9)]
        for latticeIndex in runLine(lineIndex,isRow):
            lattice = self.getLattice(latticeIndex)
            if lattice.isDisplayEmpty():
                for choiceNumber in lattice.getChoices():
                    if not LatticeValue.isEmpty(choiceNumber):
                        choiceNumberCounts[choiceNumber-1]+=1
        return choiceNumberCounts

    def getExistsByLine(self,lineIndex:int,isRow:bool)->list[int]:
        '''获得某一行/列所有已填的数'''
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
            if choiceNumber in lattice.getChoices():
                clearValues = lattice.clearOtherChoices(choiceNumber)
                if not isLenEqual(clearValues,0):
                    self.addRecord(actionType,latticeIndex,clearValues,{"lineIndex":lineIndex,"choiceNumber":choiceNumber})
                return

    def getExistsByArea(self,areaIndex:int)->list[int]:
        '''获得某一个宫内所有已填数'''
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
            clearValues = lattice.clearExistChoices(existNumbers) #排除格子的可选数
            if not isLenEqual(clearValues,0):
                self.addRecord(ACTION_AREA_BASE,latticeIndex,clearValues,{"existNumbers":existNumbers,"areaIndex":areaIndex})

    def countChoicePointsByLine(self,lineIndex:int,isRow:bool)->list:
        '''统计行/列内可选数出现的位置'''
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
        '''统计宫内可选数出现的位置'''
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
        '''若某一宫内某一个数只在某一格内可填，清空该格和宫外的可选数'''
        choicePoints = self.countChoicePointsByArea(areaIndex) #获取该宫的所有可选数
        for choiceIndex in range(9): #遍历所有可选数
            choicePoint = choicePoints[choiceIndex]
            if len(choicePoint)!=1: #不只在某一格可填的，不处理
                continue
            latticeIndex = choicePoint[0]
            lattice = self.getLattice(latticeIndex) #获取该格子下标
            clearValues = lattice.clearOtherChoices(choiceIndex+1) #清空该格子的其它数
            if not isLenEqual(clearValues,0): #非零时表示有变动
                self.addRecord(ACTION_AREA_ONLY_IN,latticeIndex,clearValues,{"choiceIndex":choiceIndex})
            self.clearLineByIndex(lattice.getRow(),choiceIndex,True,latticeIndex,ACTION_AREA_ONLY_LINE)
            self.clearLineByIndex(lattice.getColumn(),choiceIndex,False,latticeIndex,ACTION_AREA_ONLY_LINE)

    def inferAreaChoiceLine(self,areaIndex:int,isRow=True):
        '''
        1、若该宫内某一可选数只占一行/列时，对应行/列的其它宫的格子排除该可选数
        2、若该宫内某一可选数只占两行/列时，且下一宫的该数亦只出现在同样的两行/列中，则对应行/列的其它宫的格子排除该可选数
        '''
        choicePoints = self.countChoicePointsByArea(areaIndex)
        for choiceIndex in range(9):
            choicePoint = choicePoints[choiceIndex]
            if isLenBetween(choicePoint,2,6):
                lineChecks = isTwoRowCloumns(choicePoint,isRow=isRow)#检查是否在同一行
                #清除行
                if isLenEqual(lineChecks,1):
                    self.clearLineByIndex(lineChecks[0],choiceIndex,isRow=isRow,extraIndexs=choicePoint,actionType=ACTION_AREA_LINE_ONE)
                elif isLenEqual(lineChecks,2): #只有两行时才需要处理
                    nextAreaIndex = nextArea(areaIndex,isRow=isRow) #获取下一宫下标
                    rowPoints = self.countChoicePointsByArea(nextAreaIndex)
                    rowPoint = rowPoints[choiceIndex]
                    if isLenBetween(rowPoint,2,6):
                        nextLineChecks = isTwoRowCloumns(rowPoint,isRow=isRow)
                        if isLenEqual(nextLineChecks,2) and isListContains(lineChecks,nextLineChecks):
                            for lineCheck in lineChecks:
                                self.clearLineByArea(lineCheck,choiceIndex,isRow=isRow,extraAreas=[areaIndex,nextAreaIndex],extractInfo = lineChecks)

    def inferAreaChoiceCombine(self,areaIndex:int):
        '''若某宫某n个数只出现在n个格子，则清空那些格子那些数外的可选数'''
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
                        clearValues = self.getLattice(latticeIndex).clearNoListChoices(combineQueue)
                        if not isLenEqual(clearValues,0):
                            self.addRecord(ACTION_AREA_COMBINE,latticeIndex,clearValues,{"areaIndex":areaIndex,"combinePoint":combinePoint,"combineQueue":combineQueue})

    def inferXWing(self,lineIndex:int,isRow:bool):
        '''若某一数分别在两行/列的两个格子中可填，且属同两列/行，则对应列/行影响范围内的格子排除该可选数'''
        if lineIndex == 8:
            return #最后一行/列，不用处理
        choicePoints=self.countChoicePointsByLine(lineIndex,isRow=isRow)
        choiceIndexs = getValidIndexs(choicePoints,2,2)
        for checkLine in range(lineIndex+1,9):
            checkPoints = self.countChoicePointsByLine(checkLine,isRow=isRow)
            for choiceIndex in choiceIndexs:
                checkPoint = copy.deepcopy(checkPoints[choiceIndex])
                if (not isLenEqual(checkPoint,2)) or (not isLenEqual(choicePoints[choiceIndex],2)):
                    continue
                checkPoint.extend(choicePoints[choiceIndex])
                checkLines = isTwoRowCloumns(checkPoint,isRow=not isRow)
                if not isLenEqual(checkLines,2):
                    continue
                self.clearLineByIndex(checkLines[0],choiceIndex,isRow=not isRow,extraIndexs=checkPoint,actionType=ACTION_X_WING)
                self.clearLineByIndex(checkLines[1],choiceIndex,isRow=not isRow,extraIndexs=checkPoint,actionType=ACTION_X_WING)

    def countChoicePointsByAll(self,count:int)->list[int]:
        '''获取对应可选数字剩余为count的格子的下标'''
        choicePoints = []
        for latticeIndex in runAll():
            if isLenEqual(self.getLattice(latticeIndex).getValidChoices(),count):
                choicePoints.append(latticeIndex)
        return choicePoints

    def isTwoAreas(self,combineQueue:list)->list[int]:
        '''计算并统计当前格子所在宫下标'''
        areaIndexs = []
        for latticeIndex in combineQueue:
            areaIndex = toArea(latticeIndex)
            if areaIndex not in areaIndexs:
                areaIndexs.append(areaIndex)
        return areaIndexs

    def getXYWingChoice(self,combineQueue:list[int],isRow:bool)->dict:
        xyWingInfo = {}
        lattices = [self.getLattice(latticeIndex) for latticeIndex in combineQueue]
        lineIndexs = [lattice.getRow() for lattice in lattices] if isRow else [lattice.getRow() for lattice in lattices]
        xyWingInfo["mainLine"] = lineIndexs[0] if lineIndexs[0]==lineIndexs[1] or lineIndexs[0]==lineIndexs[2] else lineIndexs[1] #获得主线

    def inferXYWing(self):
        '''使用XYWING推测'''
        choicePoints = self.countChoicePointsByAll(2) #获取下标仅为2的格子
        combineQueueSet = getCombination(choicePoints,3) #获取所有3*3组合可能
        for combineQueue in combineQueueSet:
            if self.isCombineLattice(choicePoints,combineQueue):
                rowLines = isTwoRowCloumns(combineQueue,isRow=True) #判断是否分属两行
                columnlines = isTwoRowCloumns(combineQueue,isRow=False)#判断是否分属两列
                areaIndexs = self.isTwoAreas(combineQueue) #判断所属宫
                if isLenEqual(areaIndexs,1): #在同一宫，属宫内组合的情况
                    continue
                elif isLenEqual(rowLines,1) or isLenEqual(columnlines,1): #在同一行/列，属行内组合情况
                    continue
                elif isLenEqual(rowLines,2) and isLenEqual(areaIndexs,2): #两行+两宫的情况
                    pass
                elif isLenEqual(columnlines,2) and isLenEqual(areaIndexs,2): #两列+两宫的情况
                    pass
                elif isLenEqual(columnlines,2) and isLenEqual(rowLines,2) and isLenEqual(areaIndexs,3):
                    pass

    def isEmptyRecord(self)->bool:
        '''判断记录是否为空'''
        return self.record.isEmpty()

    def getRecordText(self,index:int=-1)->str:
        '''获取操作记录文本'''
        return self.record.getRecordInfo(index)