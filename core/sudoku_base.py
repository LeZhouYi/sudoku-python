#coding=utf-8

class LatticeStatus(object):
    '''格子状态'''

    EMPTY = 0 #表示格子为空，正常状态
    WRITTEN = 1 #已填入数字，正常状态
    BLOCKED = 2 #已填入数字且锁定，表示不可更改,正常状态
    EMPTY_CHOICE = 3 #未填入数字但可选数为空，非正常状态
    EXIST_WRITTEN = 4 #已填入数字但与其它数字冲突，对应状态=1转换而来的错误
    EXIST_BLOCKED = 5 #已填入数字但与其它数字冲突，对应状态=2转换而来的错误

    @classmethod
    def empty(cls)->int:
        '''表示格子为空，正常状态'''
        return cls.EMPTY

    @classmethod
    def isEmpty(cls,status:int)->bool:
        '''判断当前状态是否为EMPTY状态'''
        return status==cls.EMPTY

    @classmethod
    def written(cls)->int:
        '''表示已填入数字，正常状态'''
        return cls.WRITTEN

    @classmethod
    def isWritten(cls,status:int)->bool:
        '''判断当前状态是否为WRITTED状态'''
        return status==cls.WRITTEN

    @classmethod
    def blocked(cls)->int:
        '''表示已填入数字且锁定，表示不可更改,正常状态'''
        return cls.BLOCKED

    @classmethod
    def isBlocked(cls,status:int)->bool:
        '''判断当前状态是否为BLOCKED状态'''
        return status==cls.BLOCKED

    @classmethod
    def emptyChoice(cls)->int:
        '''表示未填入数字但可选数为空，非正常状态'''
        return cls.EMPTY_CHOICE

    @classmethod
    def isEmptyChoice(cls,status:int)->bool:
        '''判断当前状态是否为EMPTY_CHOICE状态'''
        return status==cls.EMPTY_CHOICE

    @classmethod
    def existWritten(cls)->int:
        '''表示已填入数字但与其它数字冲突，对应状态=1转换而来的错误'''
        return cls.EXIST_WRITTEN

    @classmethod
    def isExistWritten(cls,status:int)->bool:
        '''判断当前状态是否为EXIST_WRITTEN状态'''
        return status==cls.EXIST_WRITTEN

    @classmethod
    def existBlocked(cls)->int:
        '''表示已填入数字但与其它数字冲突，对应状态=2转换而来的错误'''
        return cls.EXIST_BLOCKED

    @classmethod
    def isExistBlocked(cls,status:int)->bool:
        '''判断当前状态是否为EXIST_BLOCKED状态'''
        return status==cls.EXIST_BLOCKED


class LatticeValue(object):
    '''格子填入/展示的值'''

    NUMBER_EMPTY = 0 #空值

    @classmethod
    def isEmpty(cls,value:int)->bool:
        '''判断当前状态是否为EMPTY'''
        return value == cls.NUMBER_EMPTY

    @classmethod
    def empty(cls)->int:
        '''表示当前没有填入任何数字'''
        return cls.NUMBER_EMPTY

def toRow(latticeIndex:int)->int:
    '''给定格子下标，返回格子所在行数'''
    return int(latticeIndex/9)

def toColumn(latticeIndex:int)->int:
    '''给定格子下标，返回格子所在列数'''
    return int(latticeIndex%9)

def toArea(latticeIndex:int)->int:
    '''给定格子下标，返回格子所在宫下标'''
    return int(toRow(latticeIndex)/3)*3+int(toColumn(latticeIndex)/3)