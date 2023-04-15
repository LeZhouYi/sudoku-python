#coding=utf-8
import copy

class LatticeStatus(object):
    '''格子状态'''

    EMPTY = 0 #表示格子为空，正常状态
    WRITTEN = 1 #已填入数字，正常状态
    BLOCKED = 2 #已填入数字且锁定，表示不可更改,正常状态
    EMPTY_CHOICE = 3 #未填入数字但可选数为空，非正常状态
    EXIST_WRITTEN = 4 #已填入数字但与其它数字冲突，对应状态=1转换而来的错误
    EXIST_BLOCKED = 5 #已填入数字但与其它数字冲突，对应状态=2转换而来的错误

    @classmethod
    def empty(cls)->int:
        '''表示格子为空，正常状态'''
        return cls.EMPTY

    @classmethod
    def isEmpty(cls,status:int)->bool:
        '''判断当前状态是否为EMPTY状态'''
        return status==cls.EMPTY

    @classmethod
    def written(cls)->int:
        '''表示已填入数字，正常状态'''
        return cls.WRITTEN

    @classmethod
    def isWritten(cls,status:int)->bool:
        '''判断当前状态是否为WRITTED状态'''
        return status==cls.WRITTEN

    @classmethod
    def blocked(cls)->int:
        '''表示已填入数字且锁定，表示不可更改,正常状态'''
        return cls.BLOCKED

    @classmethod
    def isBlocked(cls,status:int)->bool:
        '''判断当前状态是否为BLOCKED状态'''
        return status==cls.BLOCKED

    @classmethod
    def emptyChoice(cls)->int:
        '''表示未填入数字但可选数为空，非正常状态'''
        return cls.EMPTY_CHOICE

    @classmethod
    def isEmptyChoice(cls,status:int)->bool:
        '''判断当前状态是否为EMPTY_CHOICE状态'''
        return status==cls.EMPTY_CHOICE

    @classmethod
    def existWritten(cls)->int:
        '''表示已填入数字但与其它数字冲突，对应状态=1转换而来的错误'''
        return cls.EXIST_WRITTEN

    @classmethod
    def isExistWritten(cls,status:int)->bool:
        '''判断当前状态是否为EXIST_WRITTEN状态'''
        return status==cls.EXIST_WRITTEN

    @classmethod
    def existBlocked(cls)->int:
        '''表示已填入数字但与其它数字冲突，对应状态=2转换而来的错误'''
        return cls.EXIST_BLOCKED

    @classmethod
    def isExistBlocked(cls,status:int)->bool:
        '''判断当前状态是否为EXIST_BLOCKED状态'''
        return status==cls.EXIST_BLOCKED


class LatticeValue(object):
    '''格子填入/展示的值'''

    NUMBER_EMPTY = 0 #空值

    @classmethod
    def isEmpty(cls,value:int)->bool:
        '''判断当前状态是否为EMPTY'''
        return value == cls.NUMBER_EMPTY

    @classmethod
    def empty(cls)->int:
        '''表示当前没有填入任何数字'''
        return cls.NUMBER_EMPTY

def toRow(latticeIndex:int)->int:
    '''给定格子下标，返回格子所在行数'''
    return int(latticeIndex/9)

def toColumn(latticeIndex:int)->int:
    '''给定格子下标，返回格子所在列数'''
    return int(latticeIndex%9)

def toArea(latticeIndex:int)->int:
    '''给定格子下标，返回格子所在宫下标'''
    return int(toRow(latticeIndex)/3)*3+int(toColumn(latticeIndex)/3)

def toIndex(row:int,column)->int:
    '''给定行数和列数，返回格子下标'''
    return row*9+column

def runAll()->int:
    '''遍历所有格子下标'''
    return [i for i in range(81)]

def runLine(lineIndex:int, isRow:bool)->list[int]:
    '''给定行/列数，返回所在行/列的所有格子下标'''
    return [toIndex(lineIndex,teIndex) for teIndex in range(9)] if isRow else [toIndex(teIndex,lineIndex) for teIndex in range(9)]

def runArea(areaIndex:int)->list[int]:
    '''给定宫下标，返回所在宫的所有格子下标'''
    rowStart,columnStart = int(areaIndex/3)*3,int(areaIndex%3)*3
    indexs = []
    for r in range(3):
        for c in range(3):
            indexs.append(toIndex(rowStart+r,columnStart+c))
    return indexs

def nextArea(areaIndex:int,isRow:bool)->int:
    '''获得当宫的下一行/列的宫下标'''
    areaRow,areaColumn = int(areaIndex/3),int(areaIndex%3) #宫起始坐标
    return areaRow*3+(areaColumn+1)%3 if isRow else ((areaRow+1)%3)*3+areaColumn

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

def isLenEqual(inList:list,length:int)->bool:
    '''列表的长度是否相等'''
    return len(inList)==length

def isLenBetween(inList:list,minLength:int,maxLength:int)->bool:
    '''列表长度是否在范围内'''
    return len(inList)>=minLength and len(inList)<=maxLength

def isBetween(value:int,minValue:int,maxValue:int)->bool:
    '''是否在范围内'''
    return value>=minValue and value<=maxValue

def getValidIndexs(choicePoints:list,minSize:int,maxSize:int)->list[int]:
    '''记录有效数字下标'''
    choiceIndexs = [] #记录有效数字
    for choiceIndex in range(9):
        choicePoint = choicePoints[choiceIndex]
        if isLenBetween(choicePoint,minSize,maxSize):
            choiceIndexs.append(choiceIndex)
    return choiceIndexs

def isListContains(contains:list,checks:list)->bool:
    '''判断checks中的每一项是否出现在contains中'''
    if checks==None or len(checks)<1:
        return False
    for item in checks:
        if item not in contains:
            return False
    return True

def isTwoRowCloumns(indexList:list[int],isRow:bool)->list[int]:
    '''判断是否在同两行/列并返回'''
    if indexList==None or len(indexList)==0:
        return []
    countIndexs = []
    for index in indexList:
        countIndex = toRow(index) if isRow else toColumn(index)
        if countIndex not in countIndexs:
            countIndexs.append(countIndex)
    return countIndexs

def isEqualOrIn(value:int,checks:int|list):
    '''
    若checks为Int，则判断是否相等
    若checks为list，则判断value是否在list中
    '''
    return (isinstance(checks,int) and value==checks) or (isinstance(checks,list) and value in checks)