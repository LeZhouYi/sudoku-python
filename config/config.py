#基本参数，与画面显示，控件位置等数据相关

mainCanvasSize = 550 #数独棋盘显示的画布大小
canvasAlign = 5 #空白间隙宽

windowWidth = mainCanvasSize+195 #整个窗口默认显示宽
windowHeight = mainCanvasSize + 60 #个窗口默认显示高
windowTitle = "Sudoku @Skily_leyu"

recordStartX = canvasAlign #操作记录横坐标
recordStartY = mainCanvasSize + canvasAlign #操作记录纵坐标
recordHeight = 50 #操作记录窗口高
recordWidth = windowWidth - 2*canvasAlign -4 #操作记录窗口宽
recordPoint = [recordStartX+int(recordWidth/2), recordStartY+int(recordHeight)/2] #文本

choiceStartX = mainCanvasSize+canvasAlign #可选数画布起始x坐标
choiceStartY = canvasAlign #可选数画布起始y坐标

colorCanvasBg = "white" #主要画布背景颜色
colorMainLine = "black" #宫线颜色
colorPartLine = "black" #格子颜色
colorSelectBg = "papayawhip" #被选中格子背景颜色
colorSelectLine = "brown" #被选中格子线颜色
colorFont = "black" #字体颜色
colorFontSelect = "brown" #字体被选中时颜色
colorFontUnable = "gray" #不可用字体颜色
colorFontBlock = "gray" #被锁定字体颜色
colorFontInfo = "gray" #格子提示的数字颜色
colorFontRecord = "black" #操作提示字体颜色

fontNumber = ("Purisa",20) #数字字体设置
fontCtrl = ("Purisa",16) #文本字体设置
fontInfo = ("Purisa",10) #格子提示数字字体
fontRecord = ("Purisa",14) #操作提示数字字体

lineMainWidth = 3 #宫线宽
linePartWidth = 1 #格线宽
lineLength = mainCanvasSize-2*canvasAlign #棋盘线长

areaLength = round(lineLength/3) #宫间距

latticeLength = round((mainCanvasSize-2*canvasAlign)/9) #格子宽
latticeOffset = round(latticeLength/2) #半个格子宽

timeClick = 0.1 #点击效果显示时间

ctrlStartX = choiceStartX #操作键起始X坐标
ctrlStartY = canvasAlign*2+areaLength+6 #操作键起始Y坐标
ctrlLength = round(areaLength/2) #操作键宽度
ctrlHeight = latticeLength-2 #操作键高度
ctrlFloorAmout = 6 #操作键总层数
ctrlOffsetX = round(ctrlLength/2) #中心距离X
ctrlOffsetY = round(ctrlHeight/2) #中心距离Y

textBlocked = "锁定"
textUnLock = "解锁"
textClear = "擦除"
textInfer = "推测"
textInfo = "提示"
textBefore = "上步"
textNext = "下步"

ctrlBlockedIndex = 0 #锁定、解锁键下标
ctrlClearIndex =1 #擦除
ctrlInferIndex = 2 #推测
ctrlInfoIndex = 3 #提示
ctrlBeforeIndex = 10 #上步
ctrlNextIndex = 11 #下步

infoOffset = 0
infoLength = int((latticeLength-2*infoOffset)/3)