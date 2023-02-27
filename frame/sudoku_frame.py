import tkinter as tk

from config import config as cfg
from render import window_render as wr
from core import sudoku_core as sd

class SudokuFrame(object):

    def __init__(self) -> None:

        self.mainWindow = tk.Tk()

        #基本配置
        self.mainWindow.title(cfg.windowTitle)
        wr.centerWindow(self.mainWindow,cfg.windowWidth,cfg.windowHeight)

        #组件
        self.mainCanvas = tk.Canvas(self.mainWindow,width=cfg.windowWidth,height=cfg.windowHeight)#主画布
        self.mainCanvas.config(background=cfg.ColorCanvasBg)
        self.mainCanvas.pack()

        #数据
        self.sudoku = sd.Sudoku(size=self.mainCanvasWidth,align=self.canvasAlign)

        #渲染
        wr.drawChessboard(self.mainCanvas)

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
        #清除其它格子选中效果:
        frame.selectIndexs = [lattice.latticeIndex]#单选会取消其它格子选中效果
        #渲染选中效果
        wr.renderLatticeSelect(frame.mainCanvas,frame.mainCanvasWidth,frame.canvasAlign,3,lattice=lattice)
        #渲染可选数
        wr.renderNumberChoice(frame.mainCanvas,frame.numberChoicePoint,lattice.alternativeNumbers,frame.centerOffset)
        return
    index = frame.isMatchNumberChoise(pointX=event.x,pointY=event.y)
    if index!=None:
        print(index)