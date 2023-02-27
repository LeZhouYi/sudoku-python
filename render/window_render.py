import tkinter as tk
from config import config as cfg
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
            drawLine(canvas,cfg.colorPartLine,cfg.linePartWidth,cfg.choiceStartX,cfg.choiceStartY+cfg.areaLength*i,length=cfg.areaLength,isVertical=False)
            drawLine(canvas,cfg.colorPartLine,cfg.lineMainWidth,cfg.choiceStartX+cfg.areaLength*i,cfg.choiceStartY,length=cfg.areaLength,isVertical=True)

def renderNumberChoice(canvas:tk.Canvas,pointList:list,number:list,offset:int):
    '''
    渲染可选数
    '''
    offsetClean = offset-2
    for i  in range(9):
        point = pointList[i]
        canvas.create_rectangle(point[0]-offsetClean,point[1]-offsetClean,point[0]+offsetClean,point[1]+offsetClean,fill="white",width=0)
        if number[i]!=0:
            canvas.create_text(point[0],point[1],text=str(i+1),fill="black",font=("Purisa",30))
        else:
            canvas.create_text(point[0],point[1],text=str(i+1),fill="white",font=("Purisa",30))

def renderLatticeSelect(canvas:tk.Canvas,size:int,align:int,mainWidth:int,lattice:sd.Lattice):
    '''
    渲染格子被选中效果
    '''
    lineLength = size-2*align #线长
    latticeLength = round(lineLength/9) #格子间距
    startX = align+lattice.getRowIndex()*latticeLength
    startY = align+lattice.getCloumnIndex()*latticeLength
    canvas.create_rectangle(startX,startY,startX+latticeLength,startY+latticeLength,fill="papayawhip",outline="brown",width=3)
    #TODO：渲染数字