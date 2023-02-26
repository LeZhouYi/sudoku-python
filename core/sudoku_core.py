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
    alternativeNumbers = [1,2,3,4,5,6,7,8,9] #可选择的数字
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

    def getPointX(self)->int:
        '''
        返回格子的横坐标
        '''
        return self.centerX

    def getPointY(self)->int:
        '''
        返回格子的纵坐标
        '''
        return self.centerY

    def isMatch(self,pointX:int,pointY:int,offset:int)->bool:
        '''
        判断并返回当前坐标是否指向该格子
        pointX:当前横坐标
        pointY:当前纵坐标
        offset:允许范围内的误差
        '''
        diffX = pointX-self.centerX
        diffY = pointY-self.centerY
        return diffX>=-offset and diffX<=offset and diffY>=-offset and diffY <=offset

'''
数独整体数据结构
'''
class Sudoku(object):

    def __init__(self,size:int,align:int) -> None:
        '''
        size: 画布的大小
        align: 画布留出的边缘
        '''
        self.numberMatrix = []

        #初始化棋盘格子数据
        self.latticeLength = round((size-2*align)/9)
        self.centerOffset = round(self.latticeLength/2)
        for mRow in range(9):
            for mColumn in range(9):
                index = mRow*9+mColumn
                centerX = align+self.centerOffset+self.latticeLength*mRow
                centerY = align+self.centerOffset+self.latticeLength*mColumn
                self.numberMatrix.append(Lattice(centerX=centerX,centerY=centerY,latticeIndex = index))

    def getLatticeByPoint(self,pointX:int,pointY:int)->Lattice|None:
        '''
        根据画布当前的坐标返回对应的格子
        pointX:横坐标
        pointY:纵坐标
        '''
        for lattice in self.numberMatrix:
            if isinstance(lattice,Lattice) and lattice.isMatch(pointX=pointX,pointY=pointY,offset=self.centerOffset):
                return lattice
        return None

    def getCenterOffset(self)->int:
        '''
        格子半宽
        '''
        return self.centerOffset

    def getLatticeLength(self)->int:
        '''
        格子宽
        '''
        return self.latticeLength