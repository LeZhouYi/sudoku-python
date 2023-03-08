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
    canvas.create_text(dt.ctrlPoints[cfg.ctrlBlockedIndex][0],dt.ctrlPoints[cfg.ctrlBlockedIndex][1],text=cfg.textBlocked,fill=cfg.colorFont,font=cfg.fontCtrl)
    canvas.create_text(dt.ctrlPoints[cfg.ctrlClearIndex][0],dt.ctrlPoints[cfg.ctrlClearIndex][1],text=cfg.textClear,fill=cfg.colorFontUnable,font=cfg.fontCtrl)
    canvas.create_text(dt.ctrlPoints[cfg.ctrlInferIndex][0],dt.ctrlPoints[cfg.ctrlInferIndex][1],text=cfg.textInfer,fill=cfg.colorFont,font=cfg.fontCtrl)
    canvas.create_text(dt.ctrlPoints[cfg.ctrlInfoIndex][0],dt.ctrlPoints[cfg.ctrlInfoIndex][1],text=cfg.textInfo,fill=cfg.colorFont,font=cfg.fontCtrl)

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
    startX = cfg.ctrlStartX+cfg.ctrlLength*(index%2)
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

def renderDisplayNumber(canvas:tk.Canvas,lattice:sd.Lattice):
    '''
    渲染数字
    '''
    number = lattice.getDisplayNumber()
    point = dt.latticePoints[lattice.getLatticeIndex()]
    if number!=0:
        color = cfg.colorFontBlock if lattice.isBlocked() else cfg.colorFont
        canvas.create_text(point[0],point[1],text=str(number),fill=color,font=cfg.fontNumber)
    if not dt.isInfo:
        return #不显示提示
    #显示提示
    numberChoices = lattice.getAlternativeNumbers()
    for c in range(3):
        for r in range(3):
            index = c*3+r
            if numberChoices[index]!=0:
                canvas.create_text(point[0]+cfg.infoOffset+cfg.infoLength*(r-1),point[1]+cfg.infoOffset+cfg.infoLength*(c-1),text=numberChoices[index],font=cfg.fontInfo,fill=cfg.colorFontInfo)

def renderLatticeSelect(canvas:tk.Canvas,lattice:sd.Lattice):
    '''
    渲染格子被选中效果
    '''
    startX = cfg.canvasAlign+lattice.getColumnIndex()*cfg.latticeLength
    startY = cfg.canvasAlign+lattice.getRowIndex()*cfg.latticeLength
    canvas.create_rectangle(startX,startY,startX+cfg.latticeLength,startY+cfg.latticeLength,fill=cfg.colorSelectBg,outline=cfg.colorSelectLine,width=cfg.lineMainWidth)
    #渲染数字
    renderDisplayNumber(canvas,lattice)

def clearLatticeSelect(canvas:tk.Canvas,indexs:list,sudoku:sd.Sudoku):
    '''
    清除选中效果
    '''
    for index in indexs:
        lattice = sudoku.getLatticeByIndex(index)
        if lattice==None:
            continue
        startX = cfg.canvasAlign+lattice.getColumnIndex()*cfg.latticeLength
        startY = cfg.canvasAlign+lattice.getRowIndex()*cfg.latticeLength
        canvas.create_rectangle(startX,startY,startX+cfg.latticeLength,startY+cfg.latticeLength,fill=cfg.colorCanvasBg,outline=cfg.colorCanvasBg,width=cfg.lineMainWidth)
        paintMethod = lattice.getPaintMethod()
        canvas.create_line(startX-1,startY,startX+cfg.latticeLength+1,startY,fill=dt.colorList[paintMethod[0]],width=dt.widthList[paintMethod[0]])
        canvas.create_line(startX-1,startY+cfg.latticeLength,startX+cfg.latticeLength+1,startY+cfg.latticeLength,fill=dt.colorList[paintMethod[1]],width=dt.widthList[paintMethod[1]])
        canvas.create_line(startX,startY-1,startX,startY+cfg.latticeLength+1,fill=dt.colorList[paintMethod[2]],width=dt.widthList[paintMethod[2]])
        canvas.create_line(startX+cfg.latticeLength,startY-1,startX+cfg.latticeLength,startY+cfg.latticeLength+1,fill=dt.colorList[paintMethod[3]],width=dt.widthList[paintMethod[3]])
        #渲染数字
        renderDisplayNumber(canvas,lattice)

def renderCtrlBlock(canvas:tk.Canvas,isBlocked:bool,canBlock:bool):
    '''
    渲染锁定、解锁操作键
    '''
    startX= cfg.ctrlStartX
    startY = cfg.ctrlStartY
    canvas.create_rectangle(startX,startY,startX+cfg.ctrlLength,startY+cfg.ctrlHeight,fill=cfg.colorCanvasBg,width=cfg.lineMainWidth,outline=cfg.colorMainLine)
    text = cfg.textUnLock if isBlocked else cfg.textBlocked
    textColor = cfg.colorFont if canBlock or isBlocked else cfg.colorFontUnable
    canvas.create_text(dt.ctrlPoints[cfg.ctrlBlockedIndex][0],dt.ctrlPoints[cfg.ctrlBlockedIndex][1],text=text,fill=textColor,font=cfg.fontCtrl)

def renderCtrlClear(canvas:tk.Canvas,canClear:bool):
    '''
    渲染擦除键
    '''
    startX= cfg.ctrlStartX+cfg.ctrlLength
    startY = cfg.ctrlStartY
    canvas.create_rectangle(startX,startY,startX+cfg.ctrlLength,startY+cfg.ctrlHeight,fill=cfg.colorCanvasBg,width=cfg.lineMainWidth,outline=cfg.colorMainLine)
    textColor = cfg.colorFont if canClear else cfg.colorFontUnable
    canvas.create_text(dt.ctrlPoints[cfg.ctrlClearIndex][0],dt.ctrlPoints[cfg.ctrlClearIndex][1],text=cfg.textClear,fill=textColor,font=cfg.fontCtrl)

def renderCtrlInfer(canvas:tk.Canvas):
    '''
    渲染推测键
    '''
    startX= cfg.ctrlStartX
    startY = cfg.ctrlStartY+cfg.ctrlHeight
    canvas.create_rectangle(startX,startY,startX+cfg.ctrlLength,startY+cfg.ctrlHeight,fill=cfg.colorCanvasBg,width=cfg.lineMainWidth,outline=cfg.colorMainLine)
    textColor = cfg.colorFont if not dt.isRunInfer else cfg.colorFontUnable
    canvas.create_text(dt.ctrlPoints[cfg.ctrlInferIndex][0],dt.ctrlPoints[cfg.ctrlInferIndex][1],text=cfg.textInfer,fill=textColor,font=cfg.fontCtrl)

def renderCtrlInfo(canvas:tk.Canvas):
    '''
    渲染提示键
    '''
    startX= cfg.ctrlStartX+cfg.ctrlLength
    startY = cfg.ctrlStartY+cfg.ctrlHeight
    canvas.create_rectangle(startX,startY,startX+cfg.ctrlLength,startY+cfg.ctrlHeight,fill=cfg.colorCanvasBg,width=cfg.lineMainWidth,outline=cfg.colorMainLine)
    textColor = cfg.colorFont
    canvas.create_text(dt.ctrlPoints[cfg.ctrlInfoIndex][0],dt.ctrlPoints[cfg.ctrlInfoIndex][1],text=cfg.textInfo,fill=textColor,font=cfg.fontCtrl)