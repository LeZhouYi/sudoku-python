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