import tkinter as tk

from render import window_render

mainWindow = tk.Tk()

#基本参数
windowWidth = 550
windowHeight = 550

#基本配置
mainWindow.title("Soduku @Skily_leyu")
window_render.centerWindow(mainWindow,windowWidth,windowHeight)

#组件
mainCanvas = tk.Canvas(mainWindow,width=windowWidth,height=windowHeight)
mainCanvas.config(background="white")
mainCanvas.pack()

window_render.drawLine(mainCanvas,"black",3,10,10,500,True)

mainWindow.mainloop() #显示窗口