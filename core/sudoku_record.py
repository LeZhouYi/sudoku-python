#coding=utf-8

ACTION_INPUT_NUMBER = 0
ACTION_CLEAR_NUMBER = 1
ACTION_ROW_LINE_BASE = 2 #行简单推测
ACTION_COLUMN_LINE_BASE = 3 #列简单推测
ACTION_ROW_COMBINE = 4 #行组合推测
ACTION_COLUMN_COMBINE = 5 #列组合推测
ACTION_ROW_ONLY = 6 #行唯一推测
ACTION_CLOUMN_ONLY = 7 #列唯一推测
ACTION_AREA_BASE = 8 #宫基础推测
ACTION_AREA_LINE_ONE = 9 #宫行列推测
ACTION_AREA_LINE_TWO = 10 #宫行列推测
ACTION_AREA_ONLY_IN = 11 #宫唯一推测
ACTION_AREA_ONLY_LINE = 12 #宫唯一推测
ACTION_AREA_COMBINE = 13 #宫组合推测
ACTION_X_WING = 15 #X-WING推测

'''
用于记录操作记录具体内容的数据结构
'''
class RecordContent(object):

    def __init__(self,actionType:int,indexList:list[int]|int,valueList:list[int]|int,extract:any) -> None:
        self.actionType = actionType #动作类型
        self.indexList = indexList#影响的格子下标
        self.valueList = valueList#影响格子的具体的值
        self.extract = extract
        self.debug()

    def debug(self):
        '''
        输入当前的调试信息
        '''
        self.info = ""
        if self.isAction(ACTION_INPUT_NUMBER): #在某格子输入数字
            self.info = "【输入】%s格子输入数字[%d]，清空格子所有可选数字"%(self.getIndexText(self.indexList),self.valueList)
        elif self.isAction(ACTION_CLEAR_NUMBER): #清除某格子输入数字
            self.info = "【擦除】%s格子擦除数字[%d]，恢复格子所有可选数字，恢复格子所在%s的可选数字[%d]"%(self.getIndexText(self.indexList),self.valueList,
                            self.getIndexFull(self.indexList),self.valueList)
        elif self.isAction(ACTION_ROW_LINE_BASE): #行基础推测
            self.info = "【行基础】因%s行存在数字%s，清空%s格子的可选数字%s"%(self.extract["lineIndex"]+1,self.extract["existNumbers"],
                            self.getIndexText(self.indexList),self.valueList)
        elif self.isAction(ACTION_COLUMN_LINE_BASE): #行基础推测
            self.info = "【列基础】因%s行存在数字%s，清空%s格子的可选数字%s"%(self.extract["lineIndex"]+1,self.extract["existNumbers"],
                            self.getIndexText(self.indexList),self.valueList)
        elif self.isAction(ACTION_ROW_COMBINE): #行组合推测
            valueList = [self.extract["combineQueue"][i]+1 for i in range(len(self.extract["combineQueue"]))]
            pointList = ""
            for value in self.extract["combinePoint"]:
                pointList+=self.getIndexText(value)
            self.info = "【行组合】因%s行存在数字%s在格子「%s」中%d*%d组合，清空%s格子的可选数字%s"%(self.extract["lineIndex"]+1,valueList,pointList,
                len(valueList),len(valueList),self.getIndexText(self.indexList),self.valueList)
        elif self.isAction(ACTION_COLUMN_COMBINE): #列组合推测
            valueList = [self.extract["combineQueue"][i]+1 for i in range(len(self.extract["combineQueue"]))]
            pointList = ""
            for value in self.extract["combinePoint"]:
                pointList+=self.getIndexText(value)
            self.info = "【列组合】因%s列存在数字%s在格子「%s」中%d*%d组合，清空%s格子的可选数字%s"%(self.extract["lineIndex"]+1,valueList,pointList,
                len(valueList),len(valueList),self.getIndexText(self.indexList),self.valueList)
        elif self.isAction(ACTION_ROW_ONLY):
            self.info = "【行唯一】因%s行中数字[%d]只在%s格子中可填，清空该格子的可选数字%s"%(self.extract["lineIndex"]+1,self.extract["choiceNumber"],
                            self.getIndexText(self.indexList),self.valueList)
        elif self.isAction(ACTION_CLOUMN_ONLY):
            self.info = "【列唯一】因%s列中数字[%d]只在%s格子中可填，清空该格子的可选数字%s"%(self.extract["lineIndex"]+1,self.extract["choiceNumber"],
                            self.getIndexText(self.indexList),self.valueList)
        elif self.isAction(ACTION_AREA_BASE):
            self.info = "【宫基础】因第%d宫存在数字%s，清空%s格子的可选数字%s"%(self.extract["areaIndex"]+1,self.extract["existNumbers"],
                            self.getIndexText(self.indexList),self.valueList)
        elif self.isAction(ACTION_AREA_LINE_ONE):
            areaIndex = self.getAreaIndex(self.extract["extraIndexs"][0])
            pointList = ""
            for value in self.extract["extraIndexs"]:
                pointList+=self.getIndexText(value)
            if self.extract["isRow"]:
                self.info = "【宫一行】因第%d宫中数字[%d]只在「%s」格子中可填并形成一行，清空第%s行中%s格子的可选数字[%s]"%(areaIndex+1,self.valueList+1,
                                pointList,self.extract["lineIndex"]+1,self.getIndexText(self.indexList),self.valueList+1)
            else:
                self.info = "【宫一列】因第%d宫中数字[%d]只在「%s」格子中可填并形成一列，清空第%s列中%s格子的可选数字[%s]"%(areaIndex+1,self.valueList+1,
                                pointList,self.extract["lineIndex"]+1,self.getIndexText(self.indexList),self.valueList+1)
        elif self.isAction(ACTION_AREA_LINE_TWO):
            areaIndexs = self.extract["extraAreas"]
            lineIndexs = self.extract["lineChecks"]
            if self.extract["isRow"]:
                self.info = "【宫两行】因第%d,%d宫中数字[%d]只在第%d,%d行中可填，清空第%d宫中%s格子的可选数字[%d]"%(areaIndexs[0]+1,areaIndexs[1]+1,self.valueList+1,
                                lineIndexs[0]+1,lineIndexs[1]+1,self.getAreaIndex(self.indexList),self.getIndexText(self.indexList),self.valueList+1)
            else:
                self.info = "【宫两列】因第%d,%d宫中数字[%d]只在第%d,%d列中可填，清空第%d宫中%s格子的可选数字[%d]"%(areaIndexs[0]+1,areaIndexs[1]+1,self.valueList+1,
                                lineIndexs[0]+1,lineIndexs[1]+1,self.getAreaIndex(self.indexList),self.getIndexText(self.indexList),self.valueList+1)
        elif self.isAction(ACTION_AREA_ONLY_IN):
            self.info = "【宫唯一】因第%d宫中数字[%d]只在%s格子可填，清空该格子的可选数字%s"%(self.getAreaIndex(self.indexList)+1,self.extract["choiceIndex"],
                                self.getIndexText(self.indexList),self.valueList)
        elif self.isAction(ACTION_AREA_ONLY_LINE):
            areaIndex = self.getAreaIndex(self.extract["extraIndexs"])
            pointText = self.getIndexText(self.extract["extraIndexs"])
            if self.extract["isRow"]:
                self.info = "【宫唯一】因第%d宫中数字[%d]只在%s格子可填，清空%s格子的可选数字[%s]"%(areaIndex+1,self.valueList+1,pointText,self.getIndexText(self.indexList),self.valueList+1)
            else:
                self.info = "【宫唯一】因第%d宫中数字[%d]只在%s格子可填，清空%s格子的可选数字[%s]"%(areaIndex+1,self.valueList+1,pointText,self.getIndexText(self.indexList),self.valueList+1)
        elif self.isAction(ACTION_AREA_COMBINE):
            valueList = [self.extract["combineQueue"][i]+1 for i in range(len(self.extract["combineQueue"]))]
            pointList = ""
            for value in self.extract["combinePoint"]:
                pointList+=self.getIndexText(value)
            self.info = "【宫组合】因第%d宫中存在数字%s在「%s」格子中%d*%d组合，清空%s格子的可选数字%s"%(self.extract["areaIndex"]+1,valueList,pointList,
                                len(pointList),len(pointList),self.indexList,self.valueList)
        elif self.isAction(ACTION_X_WING):
            pointList = ""
            for value in self.extract["extraIndexs"]:
                pointList+=self.getIndexText(value)
            if self.extract["isRow"]:
                self.info = "【XWing】因数字[%d]在「%s」格子中形成XWING结构，清空第%d行%s格子的可选数字[%d]"%(self.valueList+1,pointList,self.extract["lineIndex"]+1,
                                self.getIndexText(self.indexList),self.valueList+1)
            else:
                self.info = "【XWing】因数字[%d]在「%s」格子中形成XWING结构，清空第%d列%s格子的可选数字[%d]"%(self.valueList+1,pointList,self.extract["lineIndex"]+1,
                                self.getIndexText(self.indexList),self.valueList+1)
        print(self.info)

    def getAreaIndex(self,index)->int:
        row,column= int(index/9),index%9
        areaIndex = int(row/3)*3 + column%3
        return areaIndex

    def getIndexFull(self,index:int)->str:
        row,column= int(index/9),index%9
        areaIndex = int(row/3)*3 + column%3
        return "%d行%d列%s宫"%(row+1,column+1,areaIndex+1)

    def getIndexText(self,index:int)->str:
        return "[%d,%d]"%(int(index/9)+1,index%9+1)

    def isAction(self,actionType:int):
        return self.actionType == actionType

    def getInfo(self)->str:
        return self.info

'''
用于储存sudoku操作记录的数据结构
'''
class Record(object):

    def __init__(self) -> None:
        self.actionList = []

    def addRecord(self,content:RecordContent):
        self.actionList.append(content)

    def isEmpty(self)->bool:
        return len(self.actionList)==0

    def getRecordInfo(self,index:int)->str:
        if index>=0 and index<len(self.actionList):
            return self.actionList[index].getInfo()
        elif index<0 and index>-len(self.actionList):
            return self.actionList[index].getInfo()
        else:
            return ""