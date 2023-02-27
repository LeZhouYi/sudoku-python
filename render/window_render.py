import tkinter as tk
from config import config as cfg
from config import data as dt
from core import sudoku_core as sd

def centerWindow(window:tk.Tk,width:int,height:int):
    '''
    使当前的窗口居中
    window:当前窗体
    width:当前窗体的宽
    heigth:当前窗体的高
    '''
    maxWindowWidth,maxWindowHeight = window.winfo_screenwidth(),window.winfo_screenheight()
    centerWindowSize = f'{width}x{height}+{round((maxWindowWidth-width)/2)}+{round((maxWindowHeight-height)/2)}'
    window.geometry(centerWindowSize)

def drawLine(canvas:tk.Canvas,color:str,width:int,x:int,y:int,length:int,isVertical:bool):
    '''
    绘制一条横线/竖线
    canvas: 当前画布
    color: 直线颜色
    width: 直线粗细
    x:起点x坐标
    y:起点y坐标
    isVertical:true=竖线,Fasle=横线
    '''
    endX = x if isVertical else x+length
    endY = y+length if isVertical else y
    canvas.create_line(x,y,endX,endY,fill=color,width=width)

def drawChessboard(canvas:tk.Canvas):
    '''
    绘制基本的布局
    '''
    #宫线绘制
    for i in range(4):
        drawLine(canvas,cfg.colorMainLine,cfg.lineMainWidth,cfg.canvasAlign,cfg.canvasAlign+cfg.areaLength*i,length=cfg.lineLength,isVertical=False)
        drawLine(canvas,cfg.colorMainLine,cfg.lineMainWidth,cfg.canvasAlign+cfg.areaLength*i,cfg.canvasAlign,length=cfg.lineLength,isVertical=True)
    #格线绘制
    for i in range(10):
        if i%3!=0:
            drawLine(canvas,cfg.colorPartLine,cfg.linePartWidth,cfg.canvasAlign,cfg.canvasAlign+cfg.latticeLength*i,length=cfg.lineLength,isVertical=False)
            drawLine(canvas,cfg.colorPartLine,cfg.linePartWidth,cfg.canvasAlign+cfg.latticeLength*i,cfg.canvasAlign,length=cfg.lineLength,isVertical=True)
    #可选数界面
    for i in range(2):
        drawLine(canvas,cfg.colorMainLine,cfg.lineMainWidth,cfg.choiceStartX,cfg.choiceStartY+cfg.areaLength*i,length=cfg.areaLength,isVertical=False)
        drawLine(canvas,cfg.colorMainLine,cfg.lineMainWidth,cfg.choiceStartX+cfg.areaLength*i,cfg.choiceStartY,length=cfg.areaLength,isVertical=True)
    for i in range(4):
        if i%3!=0:
            drawLine(canvas,cfg.colorPartLine,cfg.linePartWidth,cfg.choiceStartX,cfg.choiceStartY+cfg.latticeLength*i,length=cfg.areaLength,isVertical=False)
            drawLine(canvas,cfg.colorPartLine,cfg.linePartWidth,cfg.choiceStartX+cfg.latticeLength*i,cfg.choiceStartY,length=cfg.areaLength,isVertical=True)

def renderNumberChoice(canvas:tk.Canvas,number:list[int]):
    '''
    渲染可选数
    '''
    offsetClean = cfg.latticeOffset-2
    for i  in range(9):
        point = dt.numberChoicePoints[i]
        canvas.create_rectangle(point[0]-offsetClean,point[1]-offsetClean,point[0]+offsetClean,point[1]+offsetClean,fill=cfg.colorCanvasBg,width=0)
        if number[i]!=0:
            canvas.create_text(point[0],point[1],text=str(i+1),fill=cfg.colorFont,font=cfg.fontNumber)
        else:
            canvas.create_text(point[0],point[1],text=str(i+1),fill=cfg.colorFontUnable,font=cfg.fontNumber)

def renderLatticeSelect(canvas:tk.Canvas,lattice:sd.Lattice):
    '''
    渲染格子被选中效果
    '''
    startX = cfg.canvasAlign+lattice.getCloumnIndex()*cfg.latticeLength
    startY = cfg.canvasAlign+lattice.getRowIndex()*cfg.latticeLength
    canvas.create_rectangle(startX,startY,startX+cfg.latticeLength,startY+cfg.latticeLength,fill=cfg.colorSelectBg,outline=cfg.colorSelectLine,width=cfg.lineMainWidth)
    #TODO：渲染数字

def clearLatticeSelect(canvas:tk.Canvas,indexs:list,sudoku:sd.Sudoku):
    '''
    清除选中效果
    '''
    widthList = [cfg.lineMainWidth,cfg.linePartWidth]
    colorList = [cfg.colorMainLine,cfg.colorPartLine]
    for index in indexs:
        lattice = sudoku.getLatticeByIndex(index)
        if lattice==None:
            continue
        startX = cfg.canvasAlign+lattice.getCloumnIndex()*cfg.latticeLength
        startY = cfg.canvasAlign+lattice.getRowIndex()*cfg.latticeLength
        canvas.create_rectangle(startX,startY,startX+cfg.latticeLength,startY+cfg.latticeLength,fill=cfg.colorCanvasBg,outline=cfg.colorCanvasBg,width=cfg.lineMainWidth)
        paintMethod = lattice.getPaintMethod()
        canvas.create_line(startX-1,startY,startX+cfg.latticeLength+1,startY,fill=colorList[paintMethod[0]],width=widthList[paintMethod[0]])
        canvas.create_line(startX-1,startY+cfg.latticeLength,startX+cfg.latticeLength+1,startY+cfg.latticeLength,fill=colorList[paintMethod[1]],width=widthList[paintMethod[1]])
        canvas.create_line(startX,startY-1,startX,startY+cfg.latticeLength+1,fill=colorList[paintMethod[2]],width=widthList[paintMethod[2]])
        canvas.create_line(startX+cfg.latticeLength,startY-1,startX+cfg.latticeLength,startY+cfg.latticeLength+1,fill=colorList[paintMethod[3]],width=widthList[paintMethod[3]])
        #TODO：渲染数字