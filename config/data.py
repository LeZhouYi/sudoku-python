from config import config as cfg

#整个数独执行过程用到的公共变量
selectIndexs = [] #当前选中的格子

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