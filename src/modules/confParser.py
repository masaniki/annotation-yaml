import yaml
from pathlib import Path

from .errors import AnnotationKeyError,AnnotationTypeError,ConfigYamlError

class ConfParser():
    """
    @Summ: config yaml用のparser。

    @Desc: 全てclass関数で実装する。

    """

    @classmethod
    def parseFromFile(cls,confPath:str):
        """
        @Summ: config yamlのpathから構文解析する関数。

        @Returns:
          @Summ: 型確認して、余計なものを取り除いたconfigDict。
          @Type: dict
        """
        with open(confPath,mode="r",encoding="utf-8") as f:
            confDict=yaml.safe_load(f)
        validDict=cls.checkConf(confDict)
        return validDict


    @classmethod
    def checkConf(cls,confDict:dict)->dict:
        """
        @Summ: config yamlの中身を構文解析する関数。

        @Desc
        - config yamlは、annotation keyかconfig keyの記述しか許さない。
        - confDictに"isVisit" keyを追加し、annotation keyを使用したかを記録する。

        @Args:
          confDict:
            @Summ: config yamlの中身。
            @Type: Dict
        @Returns:
          @Summ: 型確認して、余計なものを取り除いたconfigDict。
          @Type: dict
        """
        validConfigDict={}  # 整形されたconfigDict
        for annoKey in confDict.keys():
            validAnnoValue={}  #annotation value.
            if(annoKey[0]!="@"):
                raise ConfigYamlError([annoKey],"Annotaion key should start with `@`.")
            valueDict=confDict[annoKey]
            if(type(valueDict)!=dict):
                raise ConfigYamlError([annoKey])
            for key,value in valueDict.items():
                if(type(key)!=str):
                    raise ConfigYamlError([annoKey,key], "Invalid value as !Parent.")
                if(key[0]=="@"):
                    continue
                elif(key=="!Parent"):
                    validConfParent=cls.checkConfParent([annoKey,"!Parent"],value)
                    validAnnoValue["!Parent"]=validConfParent
                elif(key=="!Child"):
                    validConfChild=cls.checkConfType([annoKey,"!Child"],value)
                    validAnnoValue["!Child"]=validConfChild
                else:
                    raise ConfigYamlError([annoKey,key], "Invalid value as !Parent.")
            # isVisit keyの追加。
            validAnnoValue["isVisit"]=False
            validConfigDict[annoKey]=validAnnoValue
        return validConfigDict
    
    @classmethod
    def checkConfParent(cls,confPath,value):
        """
        @Summ: `!Parent`に対応する値を型確認する関数。

        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          value:
            @Summ: `!Parent`に対応する値。
            @Type: Any
        @Returns:
          @Summ: `!Parent`のvalueとして有効な値。
          @Type: List
        """
        if(type(value)!=list):
            raise ConfigYamlError(confPath)
        for item in value:
            if(item is None):
                continue
            if(item[0]!="@"):
                raise ConfigYamlError(confPath)
        return value.copy()

    @classmethod
    def checkConfType(cls,confPath,confValue):
        """
        @Summ: data型構文を確認する関数。

        @Desc: `!Child`だけでなく、data型の入れ子が発生する際にも呼び出される。

        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          confValue:
            @Summ: data型構文。
            @Type: Any
        @Returns:
          @Summ: `!Child`のvalueとして有効な値。
          @Type: Dict
        """
        if(type(confValue)==str):
            newConfPath=confPath+[confValue]
            match confValue:
                case "!Str":
                    validType=cls.checkConfStr(newConfPath,None)
                case "!Bool":
                    validType={"!Bool":{}}
                case "!Int":
                    validType=cls.checkConfInt(newConfPath,None)
                case "!Float":
                    validType=cls.checkConfFloat(newConfPath,None)
                case "!List":
                    validType=cls.checkConfList(newConfPath,None)
                case "!FreeMap":
                    validType={"!FreeMap":{}}
                case "!AnnoMap":
                    validType=cls.checkConfAnnoMap(newConfPath,None)
                case _:
                    raise ConfigYamlError(newConfPath,"Invalid data type.")
        elif(type(confValue)==dict):
            confChildKey=list(confValue.keys())
            if(len(confChildKey)!=1):
                raise ConfigYamlError(confPath,"Invalid data type.")
            typeStr=confChildKey[0]
            newConfPath=confPath+[typeStr]
            newConfValue=confValue[typeStr]
            match typeStr:
                case "!Str":
                    validType=cls.checkConfStr(newConfPath,newConfValue)
                case "!Int":
                    validType=cls.checkConfInt(newConfPath,newConfValue)
                case "!Float":
                    validType=cls.checkConfFloat(newConfPath,newConfValue)
                case "!Enum":
                    validType=cls.checkConfEnum(newConfPath,newConfValue)
                case "!List":
                    validType=cls.checkConfList(newConfPath,newConfValue)
                case "!AnnoMap":
                    validType=cls.checkConfAnnoMap(newConfPath,newConfValue)
                case _:
                    raise ConfigYamlError(newConfPath,"Invalid data type.")
        else:
            raise ConfigYamlError(confPath,"Invalid data type.")
        return validType

    @classmethod
    def checkConfStr(cls,confPath,confValue):
        """
        @Summ: config yaml上で!Str型のtype optionを確認する関数。
        
        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          confValue:
            @Summ: !Strに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: Dict
        @Returns:
          @Summ: 有効なtype option。
          @Type: Dict
        """
        lenMin=None
        lenMax=None
        if(confValue is None):
            pass
        elif(type(confValue)!=dict):
            raise ConfigYamlError(confPath)
        else:
            for key,value in confValue.items():
                newConfPath=confPath+[key]
                match key:
                    case "min":
                        lenMin=value
                        if(type(value)==int):
                            if(lenMax is not None):
                                if(lenMax<value):
                                    raise ConfigYamlError(newConfPath)
                        else:
                            raise ConfigYamlError(newConfPath)
                    case "max":
                        lenMax=value
                        if(type(value)==int):
                            if(lenMax is not None):
                                if(value<lenMin):
                                    raise ConfigYamlError(newConfPath)
                        else:
                            raise ConfigYamlError(newConfPath)
                    case _:
                        raise ConfigYamlError(newConfPath)
        return {"!Str":{"min":lenMin,"max":lenMax}}


    @classmethod
    def checkConfInt(cls,confPath,confValue):
        """
        @Summ: config yaml上で!Int型のtype optionを確認する関数。
        
        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          confValue:
            @Summ: !Intに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: Dict
        @Returns:
          @Summ: 有効なtype option。
          @Type: Dict
        """
        intMin=None
        intMax=None
        if(confValue is None):
            pass
        elif(type(confValue)!=dict):
            raise ConfigYamlError(confPath, "Required `!Map` type.")
        else:
            for key,value in confValue.items():
                newConfPath=confPath+[key]
                match key:
                    case "min":
                        intMin=value
                        if(type(value)==int):
                            if(intMax is not None):
                                if(intMax<value):
                                    raise ConfigYamlError(newConfPath)
                        else:
                            raise ConfigYamlError(newConfPath)
                    case "max":
                        intMax=value
                        if(type(value)==int):
                            if(intMax is not None):
                                if(value<intMin):
                                    raise ConfigYamlError(newConfPath)
                        else:
                            raise ConfigYamlError(newConfPath)
                    case _:
                        raise ConfigYamlError(newConfPath)
        return {"!Int":{"min":intMin,"max":intMax}}

    @classmethod
    def checkConfFloat(cls,confPath,confValue):
        """
        @Summ: config yaml上で!Float型のtype optionを確認する関数。
        
        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          confValue:
            @Summ: !Floatに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: Dict
        @Returns:
          @Summ: 有効なtype option。
          @Type: Dict
        """
        floatMin=None
        floatMax=None
        if(confValue is None):
            pass
        elif(type(confValue)!=dict):
            raise ConfigYamlError(confPath, "Required `!Map` type.")
        else:
            for floatKey,floatVal in confValue.items():
                match floatKey:
                    case "min":
                        if(type(floatVal)!=int and type(floatVal)!=float):
                            raise ConfigYamlError(confPath)    
                        floatMin=floatVal
                    case "max":
                        if(type(floatVal)!=int and type(floatVal)!=float):
                            raise ConfigYamlError(confPath)
                        floatMax=floatVal
                    case _:
                        raise ConfigYamlError(confPath)
        return {"!Float":{"min":floatMin,"max":floatMax}}

    @classmethod
    def checkConfAnnoMap(cls,confPath,confValue):
        """
        @Summ: config yaml上で!AnnoMap型のtype optionを確認する関数。
        
        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          confValue:
            @Summ: !AnnoMapに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: List
        @Returns:
          @Summ: 有効なtype option。
          @Type: Dict
        """
        if(confValue is None):
            confValue=[]
        elif(type(confValue)!=list):
            raise ConfigYamlError(confPath)
        else:
            for i in range(len(confValue)):
                item=confValue[i]
                newConfPath=confPath+[item]
                if(item[0]!="@"):
                    raise ConfigYamlError(newConfPath)
        return {"!AnnoMap":confValue}

    @classmethod
    def checkConfList(cls,confPath,confValue):
        """
        @Summ: config yaml上で!List型のtype optionを確認する関数。
        
        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          confValue:
            @Summ: !Listに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: Dict
        @Returns:
          @Summ: 有効なtype option。
          @Type: Dict
        """
        listType=None
        listLength=None
        if(confValue is None):
            pass
        elif(type(confValue)!=dict):
            raise ConfigYamlError(confPath)
        else:
            for listKey,listVal in confValue.items():
                newConfPath=confPath+[listKey]
                match listKey:
                    case "type":
                        validDict=cls.checkConfType(newConfPath,listVal)
                        listType=validDict
                    case "length":
                        if(listVal is None):
                            continue
                        elif(type(listVal)!=int):
                            raise ConfigYamlError(newConfPath)
                        elif(listVal<=0):
                            raise ConfigYamlError(newConfPath)
                        listLength=listVal
                    case _:
                        raise ConfigYamlError(newConfPath)
        return {"!List":{"type":listType,"length":listLength}}

    @classmethod
    def checkConfEnum(cls,confPath,confValue):
        """
        @Summ: config yaml上で!Enum型のtype optionを確認する関数。
        
        @Args:
          annoKey:
            @Summ: `!Child!Enum`を格納するannotation key。
            @Type: Str
          confValue:
            @Summ: !Enumに対応するtype option。
            @Type: List
        @Returns:
          @Summ: 有効なtype option。
          @Type: Dict
        """
        enumOption=[]
        if(type(confValue)!=list):
            raise ConfigYamlError(confPath)
        else:
            for item in confValue:
                newConfPath=confPath+[item]
                if(type(item)==list):
                    raise ConfigYamlError(newConfPath)
                elif(type(item)==dict):
                    keyList=list(item.keys())
                    if(len(keyList)!=1):
                        raise ConfigYamlError(newConfPath)
                    enumOption.append(keyList[0])
                else:
                    enumOption.append(item)
        return {"!Enum":enumOption}

if(__name__=="__main__"):
    pass

