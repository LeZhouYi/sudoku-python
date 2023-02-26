import tkinter as tk

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

def drawChessboard(canvas:tk.Canvas,color:str,size:int,align:int,mainWidth:int,partWidth:int):
    '''
    绘制基本的布局
    canvas: 当前画布
    color: 直线颜色
    size:画布大小
    align: 边缘空白宽度
    mainWidth: 宫线宽度
    partWidth: 格线宽度
    '''
    lineLength = size-2*align #线长
    areaLength = round(lineLength/3) #宫间距
    latticeLength = round(lineLength/9) #格子间距

    #宫线绘制
    for i in range(4):
        drawLine(canvas,color,mainWidth,align,align+areaLength*i,length=lineLength,isVertical=False)
        drawLine(canvas,color,mainWidth,align+areaLength*i,align,length=lineLength,isVertical=True)
    #格线绘制
    for i in range(10):
        if i%3!=0:
            drawLine(canvas,color,partWidth,align,align+latticeLength*i,length=lineLength,isVertical=False)
            drawLine(canvas,color,partWidth,align+latticeLength*i,align,length=lineLength,isVertical=True)
    #可选数界面
    for i in range(2):
        drawLine(canvas,color,mainWidth,size+align,align+areaLength*i,length=areaLength,isVertical=False)
        drawLine(canvas,color,mainWidth,size+align+areaLength*i,align,length=areaLength,isVertical=True)
    for i in range(4):
        if i%3!=0:
            drawLine(canvas,color,partWidth,size+align,align+latticeLength*i,length=areaLength,isVertical=False)
            drawLine(canvas,color,partWidth,size+align+latticeLength*i,align,length=areaLength,isVertical=True)

numberChoiseBuff = None
def renderNumberChoice(canvas:tk.Canvas,pointList:list,number:list,offset:int):
    '''
    渲染可选数
    '''
    offsetClean = offset-2
    for i  in range(9):
        point = pointList[i]
        if i <len(number):
            canvas.create_rectangle(point[0]-offsetClean,point[1]-offsetClean,point[0]+offsetClean,point[1]+offsetClean,fill="pink",width=0)