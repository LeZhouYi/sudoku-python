import threading
import copy
from config import data as dt
from config import config as cfg

NUMBER_EMPTY = 0 #表示格子未填数时的空值

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
        self.rowIndex = int(self.getLatticeIndex()/9) #第几行[0-8]
        self.columnIndex = int(self.getLatticeIndex()%9) #第几列[0-8]
        self.areaIndex = int(self.getRowIndex()/3)*3+int(self.getColumnIndex()/3)#第几宫
        self.lock = threading.Lock()
        self.choiceNumbers = [i+1 for i in range(9)] #可选择的数字,若该数字不可选，则为0
        self.displayNumber = NUMBER_EMPTY #展示的数字
        self.status = STATUS_EMPTY #表示当前格子的状态

    def getLatticPoint(self)->tuple:
        '''
        返回格子所在坐标
        '''
        return (self.rowIndex,self.columnIndex)

    def getAreaIndex(self)->int:
        '''
        获取所在宫下标
        '''
        return self.areaIndex

    def getPaintMethod(self)->list[int]:
        '''
        返回该格子四条边的渲染方式
        0代表画粗，1代表画细
        '''
        methods = [[0,1],[1,1],[1,0]]
        paintMethod = methods[self.getRowIndex()%3]
        paintMethod.extend(methods[self.getColumnIndex()%3])
        return paintMethod

    def isMatch(self,pointX:int,pointY:int)->bool:
        '''
        判断并返回当前坐标是否指向该格子
        pointX:当前横坐标
        pointY:当前纵坐标
        offset:允许范围内的误差
        '''
        diffX = pointX-dt.latticePoints[self.getLatticeIndex()][0]
        diffY = pointY-dt.latticePoints[self.getLatticeIndex()][1]
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

    def getChoiceNumbers(self)->list[int]:
        '''
        返回格子当前的可选数
        '''
        return self.choiceNumbers

    def getValidChoices(self)->list[int]:
        '''
        返回格子当前可用的可选数
        '''
        choices = []
        if not self.isWritten():
            for choice in self.choiceNumbers:
                if choice != NUMBER_EMPTY:
                    choices.append(choice)
        return choices

    def isBlocked(self)->bool:
        '''
        True=当前格子被锁定
        '''
        return self.isStatusEqual(STATUS_BLOCKED) or self.isStatusEqual(STATUS_EXIST_2)

    def canBlocked(self)->bool:
        '''
        True=当前格子可以被锁定
        '''
        return self.isStatusEqual(STATUS_WRITTEN) or self.isStatusEqual(STATUS_EXIST_1)

    def canClear(self)->bool:
        '''
        True=当前格子可以被擦除
        '''
        return self.isStatusEqual(STATUS_WRITTEN) or self.isStatusEqual(STATUS_EXIST_1)

    def isWritten(self)->bool:
        '''
        True=当前格子可以被写入数字
        '''
        return self.isStatusEqual(STATUS_WRITTEN) or self.isStatusEqual(STATUS_BLOCKED)

    def setStatus(self,status:int):
        '''设定状态'''
        with self.lock:
            self.status=status

    def isStatusEqual(self,status)->bool:
        '''判定当前状态是否相符'''
        return self.status==status

    def setBlock(self):
        '''
        锁定当前格子
        '''
        if self.isStatusEqual(STATUS_WRITTEN): #写入正确的数时
            self.setStatus(STATUS_BLOCKED)
        elif self.isStatusEqual(STATUS_EXIST_1): #写入错误的数时
            self.setStatus(STATUS_EXIST_2)

    def setUnlock(self):
        '''
        解锁当前格子
        '''
        if self.isStatusEqual(STATUS_EXIST_2): #锁定的数是错误时
            self.setStatus(STATUS_EXIST_1)
        elif self.isStatusEqual(STATUS_BLOCKED): #锁定的数是正确时
            self.setStatus(STATUS_WRITTEN)

    def clearDisplay(self)->bool:
        '''
        擦除当前格子写入的数
        '''
        if self.canClear():
            self.setDisplay(NUMBER_EMPTY) #擦除
            self.initChoices() #恢复可选数
            self.setStatus(STATUS_EMPTY) #更新状态
            return True
        return False

    def initChoices(self):
        '''
        初始化可选数
        '''
        with self.lock:
            self.choiceNumbers=[i+1 for i in range(9)]

    def clearChoices(self):
        '''
        清空可选数
        '''
        with self.lock:
            self.choiceNumbers = [NUMBER_EMPTY for i in range(9)]

    def setDisplay(self,displayNumber:int)->bool:
        '''
        为当前格子写入数字
        '''
        if not self.isBlocked():
            with self.lock:
                self.displayNumber = displayNumber  #设置显示的数字
            self.clearChoices() #清空可选数
            self.setStatus(STATUS_WRITTEN) #更新状态
            return True #输入成功
        return False #输入失败

    def backChoice(self,numberChoice:int):
        '''
        将某个可选数添加回当前格子的可选数列表中
        '''
        if numberChoice>=1 and numberChoice<=9:
            if self.isStatusEqual(STATUS_EMPTY) or self.isStatusEqual(STATUS_EMPTY_CHOICE):
                with self.lock:
                    self.choiceNumbers[numberChoice-1]=numberChoice

    def getDisplay(self)->int:
        '''
        返回当前格子被写入的数
        '''
        return self.displayNumber

    def isDisplayEmpty(self)->bool:
        '''
        判断当前是否未填入数
        '''
        return self.displayNumber==NUMBER_EMPTY

    def setChoiceEmpty(self,choiceIndex:int)->bool:
        '''
        清除特定可选数
        '''
        assert choiceIndex>=0 and choiceIndex<9
        if self.isInChoices(choiceIndex):
            with self.lock:
                self.choiceNumbers[choiceIndex]=NUMBER_EMPTY
            return True
        return False

    def clearChoiceByExists(self,existNumbers=list[int])->list[int]:
        '''
        清除列表所述的可选数
        '''
        clearValues = []
        for choiceIndex in range(9):
            if self.isDisplayEmpty() and (choiceIndex+1 in existNumbers) and self.isInChoices(choiceIndex):
                clearValues.append(choiceIndex+1)
                self.setChoiceEmpty(choiceIndex)
        return clearValues

    def clearChoiceByNumber(self,numberChoice:int)->list[int]:
        '''
        清空该数外的可选数
        '''
        clearValues = copy.deepcopy(self.getValidChoices())
        if numberChoice>=1 and numberChoice<=9 and self.isDisplayEmpty() and len(clearValues)>1:
            self.clearChoices()
            self.backChoice(numberChoice)
            clearValues.remove(numberChoice)
            return clearValues
        return []

    def clearChoiceByIndexs(self,choiceIndexs:list[int])->list[int]:
        '''
        根据下标清除不在choiceIndexs内的可选数
        '''
        clearValues = []
        for choiceIndex in range(9):
            if choiceIndex not in choiceIndexs and self.isInChoices(choiceIndex):
                self.setChoiceEmpty(choiceIndex)
                clearValues.append(choiceIndex+1)
        return clearValues

    def isInChoices(self,choiceIndex)->bool:
        return choiceIndex+1 in self.choiceNumbers