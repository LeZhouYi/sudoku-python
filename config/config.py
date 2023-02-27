#基本参数，与画面显示，控件位置等数据相关

mainCanvasSize = 550 #数独棋盘显示的画布大小
canvasAlign = 5 #空白间隙宽

windowWidth = mainCanvasSize+195 #整个窗口默认显示宽
windowHeight = mainCanvasSize #个窗口默认显示高
windowTitle = "Soduku @Skily_leyu"

choiceStartX = mainCanvasSize+canvasAlign #可选数画布起始x坐标
choiceStartY = canvasAlign #可选数画布起始y坐标

colorCanvasBg = "white" #主要画布背景颜色
colorMainLine = "black" #宫线颜色
colorPartLine = "black" #格子颜色
colorSelectBg = "papayawhip" #被选中格子背景颜色
colorSelectLine = "brown" #被选中格子线颜色
colorFont = "black" #字体颜色
colorFontUnable = "gray" #不可用字体颜色

fontNumber = ("Purisa",20) #数字字体设置

lineMainWidth = 3 #宫线宽
linePartWidth = 1 #格线宽
lineLength = mainCanvasSize-2*canvasAlign #棋盘线长

areaLength = round(lineLength/3) #宫间距

latticeLength = round((mainCanvasSize-2*canvasAlign)/9) #格子宽
latticeOffset = round(latticeLength/2) #半个格子宽