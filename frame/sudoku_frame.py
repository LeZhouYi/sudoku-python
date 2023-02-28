import copy
import tkinter as tk

from config import config as cfg
from config import data as dt
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
        self.mainCanvas.config(background=cfg.colorCanvasBg)
        self.mainCanvas.pack()

        #数据
        self.sudoku = sd.Sudoku()

        #渲染
        wr.drawChessboard(self.mainCanvas)

        #按键事件
        #鼠标左键
        self.mainWindow.bind("<Button-1>",eventAdaptor(mouseLeftClick,frame=self,sudoku=self.sudoku))

        self.mainWindow.mainloop() #显示窗口

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
    if event.x<=cfg.mainCanvasSize:
        lattice = sudoku.getLatticeByPoint(pointX=event.x,pointY=event.y)
        if lattice!=None:
            #清除其它格子选中效果
            wr.clearLatticeSelect(frame.mainCanvas,copy.deepcopy(dt.selectIndexs),sudoku)
            dt.selectIndexs = [lattice.latticeIndex]#单选会取消其它格子选中效果
            #渲染选中效果
            wr.renderLatticeSelect(frame.mainCanvas,lattice=lattice)
            #渲染可选数
            wr.renderNumberChoice(frame.mainCanvas,lattice.alternativeNumbers)
            return
    if event.y<=cfg.canvasAlign+cfg.areaLength:
        indexNumber = dt.isMatchNumberChoise(pointX=event.x,pointY=event.y)
        if indexNumber!=None and len(dt.selectIndexs)>0:
            #填写数字进选中的格子
            for selectIndex in dt.selectIndexs:
                sudoku.setLatticeDisplay(selectIndex,indexNumber+1)
                #渲染选中效果
                lattice = sudoku.getLatticeByIndex(selectIndex)
                wr.renderLatticeSelect(frame.mainCanvas,lattice=lattice)
        #TODO:渲染可选数点击效果