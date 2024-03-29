#coding=utf-8

import tkinter as tk
from time import sleep
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
        drawLine(canvas,cfg.colorMainLine,cfg.lineMainWidth,cfg.canvasAlign-1,cfg.canvasAlign+cfg.areaLength*i,length=cfg.lineLength+2,isVertical=False)
        drawLine(canvas,cfg.colorMainLine,cfg.lineMainWidth,cfg.canvasAlign+cfg.areaLength*i,cfg.canvasAlign-1,length=cfg.lineLength+2,isVertical=True)
    #格线绘制
    for i in range(10):
        if i%3!=0:
            drawLine(canvas,cfg.colorPartLine,cfg.linePartWidth,cfg.canvasAlign-1,cfg.canvasAlign+cfg.latticeLength*i,length=cfg.lineLength+2,isVertical=False)
            drawLine(canvas,cfg.colorPartLine,cfg.linePartWidth,cfg.canvasAlign+cfg.latticeLength*i,cfg.canvasAlign-1,length=cfg.lineLength+2,isVertical=True)
    #可选数界面
    for i in range(2):
        drawLine(canvas,cfg.colorMainLine,cfg.lineMainWidth,cfg.choiceStartX-1,cfg.choiceStartY+cfg.areaLength*i,length=cfg.areaLength+2,isVertical=False)
        drawLine(canvas,cfg.colorMainLine,cfg.lineMainWidth,cfg.choiceStartX+cfg.areaLength*i,cfg.choiceStartY-1,length=cfg.areaLength+2,isVertical=True)
    for i in range(4):
        if i%3!=0:
            drawLine(canvas,cfg.colorPartLine,cfg.linePartWidth,cfg.choiceStartX-1,cfg.choiceStartY+cfg.latticeLength*i,length=cfg.areaLength+2,isVertical=False)
            drawLine(canvas,cfg.colorPartLine,cfg.linePartWidth,cfg.choiceStartX+cfg.latticeLength*i,cfg.choiceStartY-1,length=cfg.areaLength+2,isVertical=True)
    #控件界面
    for i  in range(3):
        drawLine(canvas,cfg.colorMainLine,cfg.lineMainWidth,cfg.ctrlStartX+i*cfg.ctrlLength,cfg.ctrlStartY-1,cfg.ctrlHeight*cfg.ctrlFloorAmout+2,isVertical=True)
    for i in range(cfg.ctrlFloorAmout+1):
        drawLine(canvas,cfg.colorMainLine,cfg.lineMainWidth,cfg.ctrlStartX-1,cfg.ctrlStartY+i*cfg.ctrlHeight,cfg.areaLength+2,isVertical=False)
    #控件文本
    renderCtrl(canvas,cfg.ctrlBlockedIndex,None)
    renderCtrl(canvas,cfg.ctrlClearIndex,None)
    renderCtrl(canvas,cfg.ctrlInferIndex,None)
    renderCtrl(canvas,cfg.ctrlInfoIndex,None)
    renderCtrl(canvas,cfg.ctrlBeforeIndex,None)
    renderCtrl(canvas,cfg.ctrlNextIndex,None)
    #操作记录界面
    canvas.create_rectangle(cfg.recordStartX,cfg.recordStartY,cfg.recordStartX+cfg.recordWidth,cfg.recordStartY+cfg.recordHeight,fill=cfg.colorCanvasBg,width=cfg.lineMainWidth,outline=cfg.colorMainLine)

def renderNumberChoice(canvas:tk.Canvas,number:list[int],isBlocked:bool):
    '''
    渲染可选数
    '''
    offsetClean = cfg.latticeOffset-2
    color = cfg.colorFontUnable if isBlocked else cfg.colorFont
    for i  in range(9):
        point = dt.numberChoicePoints[i]
        canvas.create_rectangle(point[0]-offsetClean,point[1]-offsetClean,point[0]+offsetClean,point[1]+offsetClean,fill=cfg.colorCanvasBg,width=0)
        if number[i]!=0:
            canvas.create_text(point[0],point[1],text=str(i+1),fill=color,font=cfg.fontNumber)
        else:
            canvas.create_text(point[0],point[1],text=str(i+1),fill=cfg.colorFontUnable,font=cfg.fontNumber)

def renderCtrlClick(canvas:tk.Canvas,index:int):
    '''
    渲染操作键被点击的效果
    '''
    startX = cfg.ctrlStartX+cfg.ctrlLength*int(index%2)
    startY = cfg.ctrlStartY+cfg.ctrlHeight*int(index/2)
    canvas.create_rectangle(startX,startY,startX+cfg.ctrlLength,startY+cfg.ctrlHeight,fill=cfg.colorSelectBg,width=cfg.lineMainWidth,outline=cfg.colorSelectLine)
    sleep(cfg.timeClick*2)

def renderChoiceClick(canvas:tk.Canvas,index:int):
    '''
    渲染可选数控件被点击的效果
    '''
    #渲染格子、背景
    rowIndex,cloumnIndex = int(index/3),index%3
    startX = cfg.choiceStartX+cloumnIndex*cfg.latticeLength
    startY = cfg.choiceStartY+rowIndex*cfg.latticeLength
    canvas.create_rectangle(startX,startY,startX+cfg.latticeLength,startY+cfg.latticeLength,fill=cfg.colorSelectBg,width=cfg.lineMainWidth,outline=cfg.colorSelectLine)
    #渲染数字
    point = dt.numberChoicePoints[index]
    canvas.create_text(point[0],point[1],text=str(index+1),fill=cfg.colorFontSelect,font=cfg.fontNumber)
    sleep(cfg.timeClick)
    #复原
    paintMethods = [[0,1],[1,1],[1,0]]
    paintMethod = paintMethods[rowIndex]
    paintMethod.extend(paintMethods[cloumnIndex])
    canvas.create_rectangle(startX,startY,startX+cfg.latticeLength,startY+cfg.latticeLength,fill=cfg.colorCanvasBg,width=cfg.lineMainWidth,outline=cfg.colorCanvasBg)
    canvas.create_line(startX-1,startY,startX+cfg.latticeLength+1,startY,fill=dt.colorList[paintMethod[0]],width=dt.widthList[paintMethod[0]])
    canvas.create_line(startX-1,startY+cfg.latticeLength,startX+cfg.latticeLength+1,startY+cfg.latticeLength,fill=dt.colorList[paintMethod[1]],width=dt.widthList[paintMethod[1]])
    canvas.create_line(startX,startY-1,startX,startY+cfg.latticeLength+1,fill=dt.colorList[paintMethod[2]],width=dt.widthList[paintMethod[2]])
    canvas.create_line(startX+cfg.latticeLength,startY-1,startX+cfg.latticeLength,startY+cfg.latticeLength+1,fill=dt.colorList[paintMethod[3]],width=dt.widthList[paintMethod[3]])
    # canvas.create_text(point[0],point[1],text=str(index+1),fill=cfg.colorFont,font=cfg.fontNumber)

def renderRecord(canvas:tk.Canvas,text:str=None):
    '''
    渲染日志记录页面
    '''
    canvas.create_rectangle(cfg.recordStartX,cfg.recordStartY,cfg.recordStartX+cfg.recordWidth,cfg.recordStartY+cfg.recordHeight,fill=cfg.colorCanvasBg,width=cfg.lineMainWidth,outline=cfg.colorMainLine)
    if text != None:
        canvas.create_text(cfg.recordPoint[0],cfg.recordPoint[1],text=text,font=cfg.fontRecord,fill=cfg.colorFontRecord)

def renderDisplayNumber(canvas:tk.Canvas,lattice:sd.Lattice):
    '''
    渲染数字
    '''
    number = lattice.getDisplay()
    point = dt.latticePoints[lattice.getIndex()]
    if number!=0:
        color = cfg.colorFontBlock if lattice.isBlocked() else cfg.colorFont
        canvas.create_text(point[0],point[1],text=str(number),fill=color,font=cfg.fontNumber)
    if not dt.isInfo:
        return #不显示提示
    #显示提示
    numberChoices = lattice.getChoices()
    for c in range(3):
        for r in range(3):
            index = c*3+r
            if numberChoices[index]!=0:
                canvas.create_text(point[0]+cfg.infoOffset+cfg.infoLength*(r-1),point[1]+cfg.infoOffset+cfg.infoLength*(c-1),text=numberChoices[index],font=cfg.fontInfo,fill=cfg.colorFontInfo)

def renderLatticeSelect(canvas:tk.Canvas,lattice:sd.Lattice):
    '''
    渲染格子被选中效果
    '''
    startX = cfg.canvasAlign+lattice.getColumn()*cfg.latticeLength
    startY = cfg.canvasAlign+lattice.getRow()*cfg.latticeLength
    canvas.create_rectangle(startX,startY,startX+cfg.latticeLength,startY+cfg.latticeLength,fill=cfg.colorSelectBg,outline=cfg.colorSelectLine,width=cfg.lineMainWidth)
    #渲染数字
    renderDisplayNumber(canvas,lattice)

def clearLatticeSelect(canvas:tk.Canvas,indexs:list,sudoku:sd.Sudoku):
    '''
    清除选中效果
    '''
    for index in indexs:
        lattice = sudoku.getLattice(index)
        if lattice==None:
            continue
        startX = cfg.canvasAlign+lattice.getColumn()*cfg.latticeLength
        startY = cfg.canvasAlign+lattice.getRow()*cfg.latticeLength
        canvas.create_rectangle(startX,startY,startX+cfg.latticeLength,startY+cfg.latticeLength,fill=cfg.colorCanvasBg,outline=cfg.colorCanvasBg,width=cfg.lineMainWidth)
        paintMethod = lattice.getPaintMethod()
        canvas.create_line(startX-1,startY,startX+cfg.latticeLength+1,startY,fill=dt.colorList[paintMethod[0]],width=dt.widthList[paintMethod[0]])
        canvas.create_line(startX-1,startY+cfg.latticeLength,startX+cfg.latticeLength+1,startY+cfg.latticeLength,fill=dt.colorList[paintMethod[1]],width=dt.widthList[paintMethod[1]])
        canvas.create_line(startX,startY-1,startX,startY+cfg.latticeLength+1,fill=dt.colorList[paintMethod[2]],width=dt.widthList[paintMethod[2]])
        canvas.create_line(startX+cfg.latticeLength,startY-1,startX+cfg.latticeLength,startY+cfg.latticeLength+1,fill=dt.colorList[paintMethod[3]],width=dt.widthList[paintMethod[3]])
        #渲染数字
        renderDisplayNumber(canvas,lattice)

def renderCtrl(canvas:tk.Canvas,ctrlIndex:int,extraInfo:any=None):
    '''
    渲染控制键
    '''
    startX = cfg.ctrlStartX + int(ctrlIndex%2)*cfg.ctrlLength
    startY = cfg.ctrlStartY + int(ctrlIndex/2)*cfg.ctrlHeight
    canvas.create_rectangle(startX,startY,startX+cfg.ctrlLength,startY+cfg.ctrlHeight,fill=cfg.colorCanvasBg,width=cfg.lineMainWidth,outline=cfg.colorMainLine)
    textContent = getTextContent(ctrlIndex,extraInfo)
    canvas.create_text(dt.ctrlPoints[ctrlIndex][0],dt.ctrlPoints[ctrlIndex][1],text=textContent["text"],fill=textContent["textColor"],font=cfg.fontCtrl)

def getTextContent(ctrlIndex:int,extraInfo:any=None)->dict:
    '''
    返回控件的文本
    '''
    content = {}
    if ctrlIndex == cfg.ctrlBlockedIndex:
        content["text"] = cfg.textUnLock if isInDict(extraInfo,"isBlocked") and extraInfo["isBlocked"] else cfg.textBlocked
        content["textColor"] = cfg.colorFont if ((isInDict(extraInfo,"canBlock") and isInDict(extraInfo,"isBlocked"))
                                    and (extraInfo["canBlock"] or extraInfo["isBlocked"])) else cfg.colorFontUnable
    elif ctrlIndex == cfg.ctrlClearIndex:
        content["text"] = cfg.textClear
        content["textColor"] = cfg.colorFont if isInDict(extraInfo,"canClear") and extraInfo["canClear"] else cfg.colorFontUnable
    elif ctrlIndex == cfg.ctrlInferIndex:
        content["text"] = cfg.textInfer
        content["textColor"] = cfg.colorFont if not dt.isRunInfer else cfg.colorFontUnable
    elif ctrlIndex == cfg.ctrlInfoIndex:
        content["text"] = cfg.textInfo
        content["textColor"] = cfg.colorFont
    elif ctrlIndex == cfg.ctrlBeforeIndex:
        content["text"] = cfg.textBefore
        content["textColor"] = cfg.colorFont if isInDict(extraInfo,"isFirst") and (not extraInfo["isFirst"]) else cfg.colorFontUnable
    elif ctrlIndex == cfg.ctrlNextIndex:
        content["text"] = cfg.textNext
        content["textColor"] = cfg.colorFont if isInDict(extraInfo,"isLast") and (not extraInfo["isLast"]) else cfg.colorFontUnable
    return content

def isInDict(dictData:dict,key:str)->bool:
    return dictData!=None and key in dictData