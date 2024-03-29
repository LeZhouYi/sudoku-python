#coding=utf-8

import copy
import threading
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
        self.recordIndex = -1

        #渲染
        wr.drawChessboard(self.mainCanvas)

        #按键事件
        self.mainWindow.bind("<ButtonPress-1>",eventAdaptor(clickMouseLeft,frame=self,sudoku=self.sudoku))#鼠标左键
        self.mainWindow.bind("<KeyPress-1>",eventAdaptor(clickNumber,frame=self,sudoku=self.sudoku,number=1))#按1
        self.mainWindow.bind("<KeyPress-2>",eventAdaptor(clickNumber,frame=self,sudoku=self.sudoku,number=2))#按2
        self.mainWindow.bind("<KeyPress-3>",eventAdaptor(clickNumber,frame=self,sudoku=self.sudoku,number=3))#按3
        self.mainWindow.bind("<KeyPress-4>",eventAdaptor(clickNumber,frame=self,sudoku=self.sudoku,number=4))#按4
        self.mainWindow.bind("<KeyPress-5>",eventAdaptor(clickNumber,frame=self,sudoku=self.sudoku,number=5))#按5
        self.mainWindow.bind("<KeyPress-6>",eventAdaptor(clickNumber,frame=self,sudoku=self.sudoku,number=6))#按6
        self.mainWindow.bind("<KeyPress-7>",eventAdaptor(clickNumber,frame=self,sudoku=self.sudoku,number=7))#按7
        self.mainWindow.bind("<KeyPress-8>",eventAdaptor(clickNumber,frame=self,sudoku=self.sudoku,number=8))#按8
        self.mainWindow.bind("<KeyPress-9>",eventAdaptor(clickNumber,frame=self,sudoku=self.sudoku,number=9))#按9

        chess = [0,0,0,9,6,5,7,0,3,
            0,0,6,0,2,0,0,4,9,
            9,0,3,0,4,8,0,2,0,
            7,6,1,8,9,0,4,0,0,
            0,9,0,5,1,6,0,0,0,
            0,0,5,0,0,4,9,6,1,
            1,4,0,6,5,0,2,0,8,
            0,3,0,0,8,0,0,0,4,
            0,0,8,4,0,9,0,0,0]
        # chess = [0,0,6,8,0,0,0,0,4,
        #     0,1,0,0,0,2,3,0,0,
        #     3,0,0,0,4,0,1,0,0,
        #     6,9,0,0,0,0,0,0,0,
        #     0,0,0,4,0,7,0,0,0,
        #     0,0,0,0,0,0,0,7,6,
        #     0,0,1,0,3,0,0,0,7,
        #     0,0,4,5,0,0,0,2,0,
        #     9,0,0,0,0,8,4,0,0]
        for i in range(81):
            if chess[i]!=0:
                self.sudoku.setDisplay(i,chess[i])
        reRenderAllLattice(self,self.sudoku)
        self.mainWindow.mainloop() #显示窗口

    def isFirst(self)->bool:
        '''当前显示的日志是否为第一条'''
        if self.recordIndex==0 or self.sudoku.isEmptyRecord():
            return True
        if self.sudoku.getRecordText(self.recordIndex-1)=="":
            return True
        return False

    def isLast(self)->bool:
        '''当前显示的日志是否为最后一条'''
        if self.recordIndex==-1 or self.sudoku.isEmptyRecord():
            return True
        if self.sudoku.getRecordText(self.recordIndex+1)=="":
            return True
        return False

    def beforeRecord(self):
        '''上一条记录'''
        if not self.isFirst():
            self.recordIndex-=1

    def nextRecord(self):
        '''下一条记录'''
        if not self.isLast():
            self.recordIndex+=1

    def initRecord(self):
        '''初始化当前显示记录'''
        self.recordIndex = -1

    def getCanvas(self)->tk.Canvas:
        return self.mainCanvas

##----------------------------InterFace------------------------------------##
def threadOrder(before:threading.Thread,after:threading.Thread):
    '''
    使before线程在after线程之前执行
    '''
    before.start()
    before.join()
    after.start()

def eventAdaptor(fun, **kwds):
    '''
    fun:当前要绑定的方法
    kwds:要传入的额外参数，需带参数名(eg. sudoku=sudoku)
    '''
    return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)

##----------------------------Core Logic----------------------------------##

def clickMouseLeft(event,frame:SudokuFrame,sudoku:sd.Sudoku):
    '''
    鼠标左键点击事件
    '''
    if event.x<=cfg.mainCanvasSize:
        clickLattice(event,frame,sudoku) #点击在格子区域
    if event.y<=cfg.canvasAlign+cfg.areaLength:
        clickChoice(event,frame,sudoku) #点击在可选数区域
    else:
        clickControl(event,frame,sudoku)
    reRenderRecord(frame,sudoku)

def clickControl(event,frame:SudokuFrame,sudoku:sd.Sudoku):
    '''
    点击操作键事件
    '''
    index = dt.isMatchControl(event.x,event.y)
    if dt.hasSelect():
        lattice = sudoku.getLattice(dt.selectIndexs[0])
        if index==cfg.ctrlBlockedIndex: #锁定，解锁
            if lattice.canBlocked():
                lattice.setBlock() #锁定
                reRenderLatticeSelect(frame,sudoku)#渲染格子
                paintCtrlClick(frame,sudoku,ctrlIndex=cfg.ctrlBlockedIndex)#点击效果
            elif lattice.isBlocked():
                lattice.setUnlock()#解锁
                reRenderLatticeSelect(frame,sudoku)#渲染格子
                paintCtrlClick(frame,sudoku,ctrlIndex=cfg.ctrlBlockedIndex)#点击效果
            return
        elif index==cfg.ctrlClearIndex: #擦除
            if lattice.canClear():
                sudoku.clearLattice(lattice.getIndex())#擦除
                reRenderLatticeSelect(frame,sudoku)#渲染格子
                paintCtrlClick(frame,sudoku,ctrlIndex=cfg.ctrlClearIndex)#点击效果
                reRenderNumberChoice(frame,sudoku)#渲染可选数
            return
    if index ==cfg.ctrlInferIndex: #推断
        frame.initRecord()
        if dt.updateRunInfer():
            paintCtrlClick(frame,sudoku,ctrlIndex=cfg.ctrlInferIndex)#点击效果
            clickInfer(event,frame,sudoku)
    elif index == cfg.ctrlInfoIndex: #提示
        dt.updateInfo()
        paintCtrlClick(frame,sudoku,ctrlIndex=cfg.ctrlInfoIndex)#点击效果
        reRenderAllLattice(frame,sudoku)#重新渲染所有格子
    elif index == cfg.ctrlBeforeIndex: #上一步
        if not frame.isFirst():
            frame.beforeRecord()
            reRenderRecord(frame,sudoku)
        paintCtrlClick(frame,sudoku,ctrlIndex=cfg.ctrlBeforeIndex)#点击效果
    elif index == cfg.ctrlNextIndex: #下一页
        if not frame.isLast():
            frame.nextRecord()
            reRenderRecord(frame,sudoku)
        paintCtrlClick(frame,sudoku,ctrlIndex=cfg.ctrlNextIndex)#点击效果
    reRenderRecord(frame,sudoku)

def clickLattice(event,frame:SudokuFrame,sudoku:sd.Sudoku):
    '''
    点击格子事件
    '''
    lattice = sudoku.getLatticeByPoint(pointX=event.x,pointY=event.y)
    if lattice!=None:
        if not dt.isSelectOnly(lattice.getIndex()):
            reClearLatticeSelect(frame,sudoku)#清除其它格子选中效果
        dt.setSelect(lattice.getIndex())#单选会取消其它格子选中效果
        reRenderLatticeSelect(frame,sudoku)#渲染选中效果
        reRenderNumberChoice(frame,sudoku)#渲染可选数
        reRenderCtrl(frame,sudoku)#渲染操作键是否可用

def clickChoice(event,frame:SudokuFrame,sudoku:sd.Sudoku):
    '''
    点击可选数事件
    '''
    indexNumber = dt.isMatchNumberChoise(pointX=event.x,pointY=event.y)
    if indexNumber!=None and len(dt.selectIndexs)>0:
        #填写数字进选中的格子
        for selectIndex in dt.selectIndexs:
            sudoku.setDisplay(selectIndex,indexNumber+1)
        reRenderLatticeSelect(frame,sudoku)#渲染选中效果
        paintChoiceClick(frame,sudoku,indexNumber)#渲染点击效果
        reRenderCtrl(frame,sudoku)#渲染操作键是否可用
    reRenderRecord(frame,sudoku)

def clickNumber(event,frame:SudokuFrame,sudoku:sd.Sudoku,number:int):
    '''
    按数字键，输入数字
    '''
    if number>=1 and number<=9  and len(dt.selectIndexs)>0:
        #填写数字进选中的格子
        for selectIndex in dt.selectIndexs:
            sudoku.setDisplay(selectIndex,number)
        reRenderLatticeSelect(frame,sudoku)#渲染选中效果
        reRenderNumberChoice(frame,sudoku)#渲染可选区域
        reRenderCtrl(frame,sudoku)#渲染操作键是否可用
    reRenderRecord(frame,sudoku)

def clickInfer(event,frame:SudokuFrame,sudoku:sd.Sudoku):
    '''
    推测
    '''
    for index in range(9):
        sudoku.inferLineChoiceBase(index,isRow=True)
        sudoku.inferLineChoiceBase(index,isRow=False)
        sudoku.inferLineChoiceCombine(index,isRow=True)
        sudoku.inferLineChoiceCombine(index,isRow=False)
        sudoku.inferLineChoiceOnly(index,isRow=True)
        sudoku.inferLineChoiceOnly(index,isRow=False)
        sudoku.inferAreaChoiceBase(index)
        sudoku.inferAreaChoiceLine(index,isRow=True)
        sudoku.inferAreaChoiceLine(index,isRow=False)
        sudoku.inferAreaChoiceOnly(index)
        sudoku.inferAreaChoiceCombine(index)
        sudoku.inferXWing(index,isRow=True)
        sudoku.inferXWing(index,isRow=False)
    sudoku.inferXYWing()
    reRenderAllLattice(frame,sudoku)#重新渲染所有格子
    dt.unlockInfer()
    reRenderRecord(frame,sudoku)

##-----------------------------Render----------------------------------###
def reRenderRecord(frame:SudokuFrame,sudoku:sd.Sudoku):
    '''重绘操作日志'''
    if not sudoku.isEmptyRecord():
        recordText = sudoku.getRecordText(frame.recordIndex)
        if recordText != "":
            threading.Thread(target=wr.renderRecord,args=[frame.getCanvas(),recordText],daemon=False).start()

def paintCtrlClick(frame:SudokuFrame,sudoku:sd.Sudoku,ctrlIndex:int):
    '''点击操作键的渲染流程'''
    threadClick = threading.Thread(target=wr.renderCtrlClick,args=[frame.getCanvas(),ctrlIndex],daemon=False)#渲染点击效果
    threadCtrl = threading.Thread(target=reRenderCtrl,args=[frame,sudoku],daemon=False)#渲染操作键是否可用
    threading.Thread(target=threadOrder,args=[threadClick,threadCtrl],daemon=False).start()#顺序执行

def paintChoiceClick(frame:SudokuFrame,sudoku:sd.Sudoku,indexNumber:int):
    '''点击可选数区域的渲染流程'''
    threadClick = threading.Thread(target= wr.renderChoiceClick,args=[frame.getCanvas(),indexNumber],daemon=False)#渲染可选数点击效果
    threadChoice = threading.Thread(target=reRenderNumberChoice,args=[frame,sudoku],daemon=False)#更新可选数
    threading.Thread(target=threadOrder,args=[threadClick,threadChoice],daemon=False).start()#顺序执行

def reRenderAllLattice(frame:SudokuFrame,sudoku:sd.Sudoku):
    '''重新渲染所有格子'''
    for i in range(81):
        if i not in dt.selectIndexs:
            threading.Thread(target=wr.clearLatticeSelect,args=[frame.getCanvas(),[i],sudoku],daemon=False).start()
    reRenderLatticeSelect(frame,sudoku)

def reRenderLatticeSelect(frame:SudokuFrame,sudoku:sd.Sudoku):
    '''重新渲染选中的格子的效果'''
    with dt.selectLock:
        indexs = copy.deepcopy(dt.selectIndexs)
    for selectIndex in indexs:
        #渲染选中效果
        lattice = sudoku.getLattice(selectIndex)
        threading.Thread(target=wr.renderLatticeSelect,args=[frame.getCanvas(),lattice],daemon=False).start()

def reClearLatticeSelect(frame:SudokuFrame,sudoku:sd.Sudoku):
    '''清除选中的格子的效果'''
    with dt.selectLock:
        threading.Thread(target=wr.clearLatticeSelect,args=[frame.getCanvas(),copy.deepcopy(dt.selectIndexs),sudoku],daemon=False).start()

def reRenderCtrl(frame:SudokuFrame,sudoku:sd.Sudoku):
    '''重新渲染操作键'''
    if len(dt.selectIndexs)>0:
        lattice = sudoku.getLattice(dt.selectIndexs[0])
        if lattice!=None:
            threading.Thread(target=wr.renderCtrl,args=[frame.getCanvas(),cfg.ctrlBlockedIndex,{"isBlocked":lattice.isBlocked(),"canBlock":lattice.canBlocked()}]
                            ,daemon=False).start()
            threading.Thread(target=wr.renderCtrl,args=[frame.getCanvas(),cfg.ctrlClearIndex,{"canClear":lattice.canClear()}],daemon=False).start()
    threading.Thread(target=wr.renderCtrl,args=[frame.getCanvas(),cfg.ctrlInferIndex],daemon=False).start()
    threading.Thread(target=wr.renderCtrl,args=[frame.getCanvas(),cfg.ctrlInfoIndex],daemon=False).start()
    threading.Thread(target=wr.renderCtrl,args=[frame.getCanvas(),cfg.ctrlBeforeIndex,{"isFirst":frame.isFirst()}],daemon=False).start()
    threading.Thread(target=wr.renderCtrl,args=[frame.getCanvas(),cfg.ctrlNextIndex,{"isLast":frame.isLast()}],daemon=False).start()

def reRenderNumberChoice(frame:SudokuFrame,sudoku:sd.Sudoku):
    '''重新渲染可选数区域'''
    if len(dt.selectIndexs)>0:
        lattice = sudoku.getLattice(dt.selectIndexs[0])
        if lattice!=None:
            threading.Thread(target=wr.renderNumberChoice,args=[frame.getCanvas(),lattice.getChoices(),lattice.isBlocked()],daemon=False).start()