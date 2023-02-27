from config import config as cfg

#整个数独执行过程用到的公共变量
selectIndexs = [] #当前选中的格子

numberChoicePoint = [] #设置可选数的点击范围
for c in range(3):
    for r in range(3):
        numberChoicePoint.append([cfg.choiceStartX+cfg.latticeOffset+cfg.latticeLength*r,
                        cfg.choiceStartY+cfg.latticeOffset+cfg.latticeLength*c])