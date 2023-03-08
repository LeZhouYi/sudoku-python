import threading
from config import config as cfg

#整个数独执行过程用到的公共变量
selectLock = threading.Lock()
selectIndexs = [] #当前选中的格子

isRunInfer = False #当前是否在执行推断
isRunInferLock = threading.Lock()

isInfo = False #是否显示可选数
isInfoLock = threading.Lock()

widthList = [cfg.lineMainWidth,cfg.linePartWidth] #用于选择绘线宽度
colorList = [cfg.colorMainLine,cfg.colorPartLine] #用于选择绘线颜色

latticePoints = [] #设置格子的点击范围
for mColumn in range(9):
    for mRow in range(9):
        index = mRow*9+mColumn
        centerX = cfg.canvasAlign+cfg.latticeOffset+cfg.latticeLength*mRow
        centerY = cfg.canvasAlign+cfg.latticeOffset+cfg.latticeLength*mColumn
        latticePoints.append([centerX,centerY])

numberChoicePoints = [] #设置可选数的点击范围
for c in range(3):
    for r in range(3):
        numberChoicePoints.append([cfg.choiceStartX+cfg.latticeOffset+cfg.latticeLength*r,
                        cfg.choiceStartY+cfg.latticeOffset+cfg.latticeLength*c])

ctrlPoints = [] #设置操作键的点击范围
for r in range(cfg.ctrlFloorAmout):
    for c in range(2):
        ctrlPoints.append([cfg.ctrlStartX+cfg.ctrlOffsetX+cfg.ctrlLength*c,
                        cfg.ctrlStartY+cfg.ctrlOffsetY+cfg.ctrlHeight*r])

def isMatchNumberChoise(pointX,pointY)->int|None:
    '''
    根据画布当前的坐标返回对应的可选数下标
    pointX:横坐标
    pointY:纵坐标
    '''
    for i in range(len(numberChoicePoints)):
        point = numberChoicePoints[i]
        diffX = pointX-point[0]
        diffY = pointY-point[1]
        if diffX>=-cfg.latticeOffset and diffX<=cfg.latticeOffset and diffY>=-cfg.latticeOffset and diffY<=cfg.latticeOffset:
            return i
    return None

def isMatchControl(pointX,pointY)->int|None:
    '''
    根据画布当前的坐标返回对应的操作键下标
        pointX:横坐标
        pointY:纵坐标
    '''
    for i in range(len(ctrlPoints)):
        point = ctrlPoints[i]
        diffX = pointX-point[0]
        diffY = pointY-point[1]
        if diffX>=-cfg.ctrlOffsetX and diffX<=cfg.ctrlOffsetX and diffY>=-cfg.ctrlOffsetY and diffY<=cfg.ctrlOffsetY:
            return i
    return None

def hasSelect()->bool:
    '''
    判断是否有格子选中
    '''
    return len(selectIndexs)>0