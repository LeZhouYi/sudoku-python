import tkinter as tk

from render import window_render as wr
from core import sudoku_core as sd

class SudokuFrame(object):

    def __init__(self) -> None:

        self.mainWindow = tk.Tk()

        #基本参数
        self.mainCanvasWidth = 550
        self.mainCanvasHeight = 550
        self.windowWidth = self.mainCanvasWidth+195
        self.canvasAlign = 5

        #基本配置
        self.mainWindow.title("Soduku @Skily_leyu")
        wr.centerWindow(self.mainWindow,self.windowWidth,self.mainCanvasHeight)

        #组件
        self.mainCanvas = tk.Canvas(self.mainWindow,width=self.windowWidth,height=self.mainCanvasHeight)#主画布
        self.mainCanvas.config(background="white")
        self.mainCanvas.pack()

        #数据
        self.sudoku = sd.Sudoku(size=self.mainCanvasWidth,align=self.canvasAlign)
        self.numberChoicePoint = [] #设置可选数的点击范围
        self.baseX = self.mainCanvasWidth+self.canvasAlign#可选起始位置
        self.baseY = self.canvasAlign #可选起始位置
        self.centerOffset = self.sudoku.getCenterOffset()
        for c in range(3):
            for r in range(3):
                self.numberChoicePoint.append([self.baseX+self.centerOffset+self.sudoku.getLatticeLength()*r,
                                        self.baseY+self.centerOffset+self.sudoku.getLatticeLength()*c])

        #渲染
        wr.drawChessboard(self.mainCanvas,"black",self.mainCanvasWidth,self.canvasAlign,3,1)

        #按键事件
        #鼠标左键
        self.mainWindow.bind("<Button-1>",eventAdaptor(mouseLeftClick,frame=self,sudoku=self.sudoku))

        self.mainWindow.mainloop() #显示窗口

    def isMatchNumberChoise(self,pointX,pointY)->int|None:
        '''
        根据画布当前的坐标返回对应的可选数下标
        pointX:横坐标
        pointY:纵坐标
        '''
        for i in range(len(self.numberChoicePoint)):
            point = self.numberChoicePoint[i]
            diffX = pointX-point[0]
            diffY = pointY-point[1]
            if diffX>=-self.centerOffset and diffX<=self.centerOffset and diffY>=-self.centerOffset and diffY<=self.centerOffset:
                return i
        return None

    def getNumberChoicePoint(self)->list[int]:
        '''
        可选数控件坐标
        '''
        return self.numberChoicePoint

def eventAdaptor(fun, **kwds):
    '''
    fun:当前要绑定的方法
    kwds:要传入的额外参数，需带参数名(eg. sudoku=sudoku)
    '''
    return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)

def mouseLeftClick(event,frame:SudokuFrame,sudoku:sd.Sudoku):
    lattice = sudoku.getLatticeByPoint(pointX=event.x,pointY=event.y)
    if lattice!=None:
        #渲染可选数
        wr.renderNumberChoice(frame.mainCanvas,frame.numberChoicePoint,lattice.alternativeNumbers,frame.centerOffset)
        return
    index = frame.isMatchNumberChoise(pointX=event.x,pointY=event.y)
    if index!=None:
        print(index)