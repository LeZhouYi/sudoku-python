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

    displayNumber = 0 #展示的数字
    alternativeNumbers = [] #可选择的数字
    status = STATUS_EMPTY #表示当前格子的状态
    isSelected = False #表示当前格子是否被选中

    def __init__(self,centerX:int,centerY:int,latticeIndex:int) -> None:
        '''
        centerX #格子相对画布所处位置的中心的X坐标
        centerY #格子相对画布所处位置的中心的Y坐标
        latticeIndex #第几个格子
        '''
        self.centerX = centerX #格子相对画布所处位置的中心的X坐标
        self.centerY = centerY #格子相对画布所处位置的中心的Y坐标
        self.latticeIndex = latticeIndex #第几个格子
        self.rowIndex = round(latticeIndex/9) #第几行[0-8]
        self.coloumnIndex = latticeIndex%9 #第几列[0-8]

'''
数独整体数据结构
'''
class Sudoku(object):

    def __init__(self) -> None:
        pass