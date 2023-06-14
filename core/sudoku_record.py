#coding=utf-8
from core.sudoku_base import *

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
ACTION_XY_WING = 16 #XY-WING推测

class RecordContent(object):
    '''用于记录操作记录具体内容的数据结构'''

    def __init__(self,actionType:int,index:int,valueList:list[int]|int,extract:any) -> None:
        self.actionType = actionType #动作类型
        self.index = index#影响的格子下标
        self.valueList = valueList#影响格子的具体的值
        self.extract = extract
        self.debug()

    def debug(self):
        '''
        输入当前的调试信息
        '''
        self.info = ""
        if self.isAction(ACTION_INPUT_NUMBER): #在某格子输入数字
            self.info = "【输入】%s格子输入数字[%d]，清空格子所有可选数字"%(self.getIndexText(self.index),self.valueList)
        elif self.isAction(ACTION_CLEAR_NUMBER): #清除某格子输入数字
            self.info = "【擦除】%s格子擦除数字[%d]，恢复格子所有可选数字，恢复格子所在%s的可选数字[%d]"%(self.getIndexText(self.index),self.valueList,
                            self.getIndexFull(self.index),self.valueList)
        elif self.isAction(ACTION_ROW_LINE_BASE): #行基础推测
            self.info = "【行基础】因%s行存在数字%s，清空%s格子的可选数字%s"%(self.extract["lineIndex"]+1,self.extract["existNumbers"],
                            self.getIndexText(self.index),self.valueList)
        elif self.isAction(ACTION_COLUMN_LINE_BASE): #行基础推测
            self.info = "【列基础】因%s行存在数字%s，清空%s格子的可选数字%s"%(self.extract["lineIndex"]+1,self.extract["existNumbers"],
                            self.getIndexText(self.index),self.valueList)
        elif self.isAction(ACTION_ROW_COMBINE): #行组合推测
            valueList = [self.extract["combineQueue"][i]+1 for i in range(len(self.extract["combineQueue"]))]
            pointList = ""
            for value in self.extract["combinePoint"]:
                pointList+=self.getIndexText(value)
            self.info = "【行组合】因%s行存在数字%s在格子「%s」中%d*%d组合，清空%s格子的可选数字%s"%(self.extract["lineIndex"]+1,valueList,pointList,
                len(valueList),len(valueList),self.getIndexText(self.index),self.valueList)
        elif self.isAction(ACTION_COLUMN_COMBINE): #列组合推测
            valueList = [self.extract["combineQueue"][i]+1 for i in range(len(self.extract["combineQueue"]))]
            pointList = ""
            for value in self.extract["combinePoint"]:
                pointList+=self.getIndexText(value)
            self.info = "【列组合】因%s列存在数字%s在格子「%s」中%d*%d组合，清空%s格子的可选数字%s"%(self.extract["lineIndex"]+1,valueList,pointList,
                len(valueList),len(valueList),self.getIndexText(self.index),self.valueList)
        elif self.isAction(ACTION_ROW_ONLY):
            self.info = "【行唯一】因%s行中数字[%d]只在%s格子中可填，清空该格子的可选数字%s"%(self.extract["lineIndex"]+1,self.extract["choiceNumber"],
                            self.getIndexText(self.index),self.valueList)
        elif self.isAction(ACTION_CLOUMN_ONLY):
            self.info = "【列唯一】因%s列中数字[%d]只在%s格子中可填，清空该格子的可选数字%s"%(self.extract["lineIndex"]+1,self.extract["choiceNumber"],
                            self.getIndexText(self.index),self.valueList)
        elif self.isAction(ACTION_AREA_BASE):
            self.info = "【宫基础】因第%d宫存在数字%s，清空%s格子的可选数字%s"%(self.extract["areaIndex"]+1,self.extract["existNumbers"],
                            self.getIndexText(self.index),self.valueList)
        elif self.isAction(ACTION_AREA_LINE_ONE):
            areaIndex = toArea(self.extract["extraIndexs"][0])
            pointList = ""
            for value in self.extract["extraIndexs"]:
                pointList+=self.getIndexText(value)
            if self.extract["isRow"]:
                self.info = "【宫一行】因第%d宫中数字[%d]只在「%s」格子中可填并形成一行，清空第%s行中%s格子的可选数字[%s]"%(areaIndex+1,self.valueList+1,
                                pointList,self.extract["lineIndex"]+1,self.getIndexText(self.index),self.valueList+1)
            else:
                self.info = "【宫一列】因第%d宫中数字[%d]只在「%s」格子中可填并形成一列，清空第%s列中%s格子的可选数字[%s]"%(areaIndex+1,self.valueList+1,
                                pointList,self.extract["lineIndex"]+1,self.getIndexText(self.index),self.valueList+1)
        elif self.isAction(ACTION_AREA_LINE_TWO):
            areaIndexs = self.extract["extraAreas"]
            lineIndexs = self.extract["lineChecks"]
            if self.extract["isRow"]:
                self.info = "【宫两行】因第%d,%d宫中数字[%d]只在第%d,%d行中可填，清空第%d宫中%s格子的可选数字[%d]"%(areaIndexs[0]+1,areaIndexs[1]+1,self.valueList+1,
                                lineIndexs[0]+1,lineIndexs[1]+1,toArea(self.index),self.getIndexText(self.index),self.valueList+1)
            else:
                self.info = "【宫两列】因第%d,%d宫中数字[%d]只在第%d,%d列中可填，清空第%d宫中%s格子的可选数字[%d]"%(areaIndexs[0]+1,areaIndexs[1]+1,self.valueList+1,
                                lineIndexs[0]+1,lineIndexs[1]+1,toArea(self.index),self.getIndexText(self.index),self.valueList+1)
        elif self.isAction(ACTION_AREA_ONLY_IN):
            self.info = "【宫唯一】因第%d宫中数字[%d]只在%s格子可填，清空该格子的可选数字%s"%(toArea(self.index)+1,self.extract["choiceIndex"],
                                self.getIndexText(self.index),self.valueList)
        elif self.isAction(ACTION_AREA_ONLY_LINE):
            areaIndex = toArea(self.extract["extraIndexs"])
            pointText = self.getIndexText(self.extract["extraIndexs"])
            if self.extract["isRow"]:
                self.info = "【宫唯一】因第%d宫中数字[%d]只在%s格子可填，清空%s格子的可选数字[%s]"%(areaIndex+1,self.valueList+1,pointText,self.getIndexText(self.index),self.valueList+1)
            else:
                self.info = "【宫唯一】因第%d宫中数字[%d]只在%s格子可填，清空%s格子的可选数字[%s]"%(areaIndex+1,self.valueList+1,pointText,self.getIndexText(self.index),self.valueList+1)
        elif self.isAction(ACTION_AREA_COMBINE):
            valueList = [self.extract["combineQueue"][i]+1 for i in range(len(self.extract["combineQueue"]))]
            pointList = ""
            for value in self.extract["combinePoint"]:
                pointList+=self.getIndexText(value)
            self.info = "【宫组合】因第%d宫中存在数字%s在「%s」格子中%d*%d组合，清空%s格子的可选数字%s"%(self.extract["areaIndex"]+1,valueList,pointList,
                                len(pointList),len(pointList),self.index,self.valueList)
        elif self.isAction(ACTION_X_WING):
            pointList = ""
            for value in self.extract["extraIndexs"]:
                pointList+=self.getIndexText(value)
            if self.extract["isRow"]:
                self.info = "【XWing】因数字[%d]在「%s」格子中形成XWING结构，清空第%d行%s格子的可选数字[%d]"%(self.valueList+1,pointList,self.extract["lineIndex"]+1,
                                self.getIndexText(self.index),self.valueList+1)
            else:
                self.info = "【XWing】因数字[%d]在「%s」格子中形成XWING结构，清空第%d列%s格子的可选数字[%d]"%(self.valueList+1,pointList,self.extract["lineIndex"]+1,
                                self.getIndexText(self.index),self.valueList+1)
        elif self.isAction(ACTION_XY_WING):
            pointList = ""
            for value in self.extract["extraIndexs"]:
                pointList+=self.getIndexText(value)
            self.info = "【XYWing】因在[%s]格子中形成XYWING结构，清空%s格子的可选数字[%d]"%(pointList,self.getIndexText(self.index),self.valueList)
        print(self.info)

    def getIndexFull(self,index:int)->str:
        '''返回格子下标对应格子的完整信息'''
        return "%d行%d列%s宫"%(toRow(index)+1,toColumn(index)+1,toArea(index)+1)

    def getIndexText(self,index:int)->str:
        '''返回格子下标对应的行/列信息'''
        return "[%d,%d]"%(toRow(index)+1,toColumn(index)+1)

    def isAction(self,actionType:int):
        '''判断是否一样的操作'''
        return self.actionType == actionType

    def getInfo(self)->str:
        '''返回操作日志文本'''
        return self.info

class Record(object):
    '''用于储存sudoku操作记录的数据结构'''

    def __init__(self) -> None:
        self.actionList = []

    def addRecord(self,content:RecordContent):
        '''添加记录'''
        self.actionList.append(content)

    def isEmpty(self)->bool:
        '''判断当前记录是否为空'''
        return len(self.actionList)==0

    def getRecordInfo(self,index:int)->str:
        '''获得当前下标所对应的记录信息'''
        if index>=0 and index<len(self.actionList):
            return self.actionList[index].getInfo()
        elif index<0 and index>-len(self.actionList):
            return self.actionList[index].getInfo()
        else:
            return ""