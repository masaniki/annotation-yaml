import yaml
from pathlib import Path

from .errors import AnnotationKeyError,AnnotationTypeError,ConfigYamlError

class DictTraversal():
    """
    @Summ: 辞書型の中身を探索するclass.

    @InsVars:
        _configDict:
            @Summ: config yamlを構文解析した後の値を格納する。
            @Desc:
            - !Childの値は{"!Child": {typeString(str):typOption(dict)}}という形式に直す。
            - typeStringはdata型を表す文字列。
            - typeOptionはdata型の詳細な設定を表すdict型である。
            - つまり、str-format data typeもmap-format data typeに直すということ。
            - map-format data typeが無いBool型は{"!Bool":{}}とする。
            - annotation keyを使った否かを"isVisit" keyに記録する。
            @Type: Dict
        _visitQueue:
            @Summ: 探索queue
            @Desc: BFSなのでFIFO。
            @Type: List
        _pathQueue:
            @Summ: 探索する要素の相対pathを格納する。
            @Desc:
            - visitQueueと要素番号を共有する。
            - []でroot要素を表す。
            @Type: List
        _curAnoy:
            @Summ: 現在探索中のANOY file名。
            @ComeFrom: current ANOY.
            @Type: Str
        _anoyPath:
            @Summ: _curAnoy内での現在地。
            @Type: List
    """

    def __init__(self,configDict:dict):
        """
        @Summ: constructor.
        """
        self._configDict=self.checkConfig(configDict)
        # print(self._configDict)
        self._visitQueue=[]
        self._pathQueue=[]
        self._curAnoy=""
        self._anoyPath=[]
    
    def checkConfig(self,configDict:dict)->dict:
        """
        @Summ: config yamlの中身を構文解析する関数。

        @Desc
        - config yamlは、annotation keyかconfig keyの記述しか許さない。
        - configDictに"isVisit" keyを追加し、annotation keyを使用したかを記録する。

        @Args:
          configDict:
            @Summ: config yamlの中身。
            @Type: Dict
        @Returns:
          @Summ: 型確認して、余計なものを取り除いたconfigDict。
          @Type: dict
        """
        validConfigDict={}  # 整形されたconfigDict
        for annoKey in configDict.keys():
            validAnnoValue={}  #annotation value.
            if(annoKey[0]!="@"):
                raise ConfigYamlError([annoKey],"Annotaion key should start with `@`.")
            valueDict=configDict[annoKey]
            if(type(valueDict)!=dict):
                raise ConfigYamlError([annoKey])
            for key,value in valueDict.items():
                if(type(key)!=str):
                    raise ConfigYamlError([annoKey,key], "Invalid value as !Parent.")
                if(key[0]=="@"):
                    continue
                elif(key=="!Parent"):
                    validConfParent=self.checkConfParent([annoKey,"!Parent"],value)
                    validAnnoValue["!Parent"]=validConfParent
                elif(key=="!Child"):
                    validConfChild=self.checkConfType([annoKey,"!Child"],value)
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

    def dirDFS(self,anoyPath:Path):
        """
        @Summ: directory内を深さ優先探索する関数。

        @Warning: 

        @Desc:
        - fileならばYAMLかどうかを確認して、内部のdict型を探索する。
        - directoryならば、子要素を再帰的に探索する。

        @Args:
          anoyPath:
            @Summ: 探索するfileやdirectoryのpath名。
            @Type: Path
        """
        if(anoyPath.is_file()):
            suffix=anoyPath.suffix
            if(suffix==".yaml" or suffix==".yml" or suffix==".anoy"):
                with open(anoyPath, mode="r", encoding="utf-8") as f:
                    anoyDict=yaml.safe_load(f)
                self._curAnoy=anoyPath
                self.anoyFreeSearch([],anoyDict,errOut=True)
        else:
            for childPath in anoyPath.iterdir():
                self.dirDFS(childPath)


    def anoyFreeSearch(self,anoyPath,anoyValue,errOut:bool):
        """
        @Summ: data型が指定されていない時の関数。

        @Desc:
        - scalar型に対してはTrueを返してすぐ終了。
        - container型に対しては、子要素を探索する。
        - 組(anoyPath,そのpathでの値,configの値)で探索する。
        - 最初は([],長いdict)で、探索が進むごとに(anoyPath,短いdict)になる。
        - config yamlが指定されていなくても、free keyとannotation keyの混合は許さない。
        - list型やFreeMap型を検知してもconfig yamlは機能しない。AnnoMap型を検知するまでがこの関数の役割だ。

        @Args:
          anoyPath:
            @Summ: anoy上のpath。
            @Desc: root nodeの時は空listを代入。
            @Type: List
          anoyValue:
            @Summ: parentに対応する値を代入。
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        @Returns:
          @Summ: 型が正常ならばTrue
          @Type: Bool
        """
        if(type(anoyValue)==list):
            isValid=self.checkAnoyList(anoyPath,anoyValue,{},errOut)
            return isValid
        elif(type(anoyValue)==dict):
            keyList=list(anoyValue.keys())
            if(keyList==[]):
                return True
            firstKey=keyList[0]
            if(type(firstKey)!=str):
                isValid=self.checkAnoyFreeMap(anoyPath,anoyValue,errOut)
            elif(firstKey[0]=="@"):
                isValid=self.checkAnoyAnnoMap(anoyPath,anoyValue,[],errOut)
            else:
                isValid=self.checkAnoyFreeMap(anoyPath,anoyValue,errOut)
            return isValid
        else:
            return True

    def checkAnoyType(self,anoyPath,data,confType,errOut:bool):
        """
        @Summ: ANOY上でdata型構文を確認する関数。

        @Note: confType=Noneの時を記述する必要がある。

        @Args:
          anoyPath:
            @Summ: ANOY上の位置。
            @Type: List
          data:
            @Summ: ANOY上の値。型確認する対象。
          confType:
            @Summ: config yaml上のdata型構文。
            @Desc: Noneの時はfreeSearchする。
            @Type: Dict
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        @Returns:
          @Summ: 正しいdata型の時True。
          @Type: Bool
        """
        if(confType is None):
            isValid=self.anoyFreeSearch(anoyPath,data,errOut)
            return isValid
        typeStr=list(confType.keys())[0]
        typeOption=confType[typeStr]
        match typeStr:
            case "!Str":
                isValid=self.checkAnoyStr(anoyPath,data,typeOption,errOut)
            case "!Bool":
                isValid=self.checkAnoyBool(anoyPath,data,errOut)
            case "!Int":
                isValid=self.checkAnoyInt(anoyPath,data,typeOption,errOut)
            case "!Float":
                isValid=self.checkAnoyFloat(anoyPath,data,typeOption,errOut)
            case "!FreeMap":
                isValid=self.checkAnoyFreeMap(anoyPath,data,errOut)
            case "!AnnoMap":
                isValid=self.checkAnoyAnnoMap(anoyPath,data,typeOption,errOut)
            case "!List":
                isValid=self.checkAnoyList(anoyPath,data,typeOption,errOut)
            case "!Enum":
                isValid=self.checkAnoyEnum(anoyPath,data,typeOption,errOut)
            case _:
                if(errOut):
                    raise AnnotationTypeError(self._curAnoy,anoyPath,"!Type")
                else:
                    isValid=False
        return isValid

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

    def checkAnoyStr(self,anoyPath,anoyValue,confValue,errOut:bool):
        """
        @Summ: ANOY上で!Str型を型確認する関数。

        @Desc:
        - strOptionのkeyは"min"と"max"だ。

        @Args:
          anoyPath:
            @Summ: anoy内の現在地。
            @Type: List
          anoyValue:
            @Summ: 型確認する値。
          strOption:
            @Summ: 文字列型のoption。
            @Type: Dict
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        @Returns:
          @Summ: 型が正常である時にTrue.
          @Type: Bool
        """
        minLen=confValue.get("min")
        maxLen=confValue.get("max")
        raiseError=False
        if(type(anoyValue)==str):
            if(minLen is not None):
                if(len(anoyValue)<minLen):
                    raiseError=True
            if(maxLen is not None):
                if(maxLen<len(anoyValue)):
                    raiseError=True
        else:
            raiseError=True
        # error出すかの判断。
        if(raiseError):
            if(errOut):
                raise AnnotationTypeError(self._curAnoy,anoyPath,"!Str")
            else:
                return False
        else:
            return True

    def checkAnoyBool(self,anoyPath,anoyValue,errOut:bool):
        """
        @Summ: ANOY上で!Bool型を型確認する関数。

        @Args:
          anoyPath:
            @Summ: anoy内の現在地。
            @Type: List
          anoyValue:
            @Summ: 型確認する値。
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        @Returns:
          @Summ: 正常な値ならばTrue.
          @Type: Bool
        """
        if(type(anoyValue)==bool):
            return True
        elif(errOut):
            raise AnnotationTypeError(self._curAnoy,anoyPath,"!Bool")
        else:
            return False

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
            raise ConfigYamlError(configPath, "Required `!Map` type.")
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

    def checkAnoyInt(self,anoyPath,anoyValue,confValue,errOut:bool):
        """
        @Summ: ANOY上で!Int型を型確認する関数。

        @Desc:
        - intOptionのkeyは、"min"と"max"。

        @Args:
          anoyPath:
            @Summ: anoy内の現在地。
            @Type: List
          anoyValue:
            @Summ: 型確認する値。
          confValue:
            @Summ: int型のoption。
            @Type: Dict
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        @Returns:
          @Type: Bool
        """
        minInt=confValue.get("min")
        maxInt=confValue.get("max")
        raiseError=False
        if(type(anoyValue)==int):
            if(minInt is not None):
                if(anoyValue<minInt):
                    raiseError=True
            if(maxInt is not None):
                if(maxInt<anoyValue):
                    raiseError=True
        else:
            raiseError=True
        # error出すかの判断。
        if(raiseError):
            if(errOut):
                raise AnnotationTypeError(self._curAnoy,anoyPath,"!Int")
            else:
                return False
        else:
            return True

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

    def checkAnoyFloat(self,anoyPath,anoyValue,confValue,errOut:bool):
        """
        @Summ: ANOY上で!Float型を型確認する関数。

        @Desc:
        - int型も受け入れる。
        - intOptionのkeyは、"min"と"max"。

        @Args:
          anoyPath:
            @Summ: anoy内の現在地。
            @Type: List
          anoyValue:
            @Summ: 型確認する値。
          confValue:
            @Summ: float型のoption。
            @Type: Dict
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        @Returns:
          @Type: Bool
        """
        minFloat=confValue.get("min")
        maxFloat=confValue.get("max")
        raiseError=False
        if(type(anoyValue)==int or type(anoyValue)==float):
            if(minFloat is not None):
                if(anoyValue<minFloat):
                    raiseError=True
            if(maxFloat is not None):
                if(maxFloat<anoyValue):
                    raiseError=True
        else:
            raiseError=True
        # error出すかの判断。
        if(raiseError):
            if(errOut):
                raise AnnotationTypeError(self._curAnoy,anoyPath,"!Float")
            else:
                return False
        else:
            return True

    def checkAnoyFreeMap(self,anoyPath,anoyValue,errOut:bool):
        """
        @Summ: ANOY上で!FreeMap型を型確認する関数。

        @Warning: まだ入れ子の機能を実装していない。浅い探索のみで終了する。

        @Args:
          anoyPath:
            @Summ: anoy内の現在地。
            @Type: List
          anoyValue:
            @Summ: 型確認する値。
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        @Returns:
          @Summ: 正常な値ならばTrue.
          @Type: Bool
        """
        if(type(anoyValue)==dict):
            for key,value in anoyValue.items():
                newAnoyPath=anoyPath+[key]
                # "@"の確認。
                if(type(key)==str):
                    if(key[0]=="@"):
                        if(errOut):
                            raise AnnotationTypeError(self._curAnoy,newAnoyPath,"!FreeMap")
                        else:
                            return False
                isValid=self.anoyFreeSearch(newAnoyPath,value,errOut)
                if(not isValid):
                    return False
            return True
        else:
            if(errOut):
                raise AnnotationTypeError(self._curAnoy,anoyPath,"!FreeMap")
            else:
                return False

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
                newConfPath=confPath+[item]
                item=confValue[i]
                if(item[0]!="@"):
                    raise ConfigYamlError(newConfPath)
        return {"!AnnoMap":confValue}

    def checkAnoyAnnoMap(self,anoyPath,anoyValue,confValue:list,errOut:bool):
        """
        @Summ: ANOY上で!FreeMap型を型確認する関数。

        @Desc:
        - この関数が再帰の中心となる。
        - <annoKeyList>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<annoKeyList>以外のannotation keyも許容される。

        @Args:
          anoyPath:
            @Summ: anoy内の現在地。
            @Type: List
          anoyValue:
            @Summ: 型確認する値。
          confValue:
            @Summ: 子要素になれるannotation keyのlist。
            @Desc:
            - 空lsitの時は任意のannotation keyを受け入れる。
            - これは全てのannotation keyが入ったlist型と同じ挙動をする。
            @Type: List
            @Default: []
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        @Returns:
          @Summ: 正常な値ならばTrue.
          @Type: Bool
        """
        if(type(anoyValue)==dict):
            for key,value in anoyValue.items():
                newAnoyPath=anoyPath+[key]
                # !Parentの確認。
                configValue=self._configDict.get(key)
                if(configValue is None):
                    if(errOut):
                        raise AnnotationKeyError(self._curAnoy,newAnoyPath,key)
                    else:
                        return False
                confParent=configValue.get("!Parent")
                confChild=configValue.get("!Child")
                if(confParent is not None):
                    if(anoyPath==[]):
                        parentKey=None
                    else:
                        parentKey=anoyPath[-1]
                    if(parentKey not in confParent):
                        if(errOut):
                            raise AnnotationTypeError(self._curAnoy,newAnoyPath,"!Parent")
                        else:
                            return False
                # AnnoMap型のtypeOptionの確認。
                if(confValue!=[]):
                    if(key not in confValue):
                        if(errOut):
                            raise AnnotationTypeError(self._curAnoy,newAnoyPath,"!AnnoMap")
                        else:
                            return False
                # 子要素を探索。
                isValid=self.checkAnoyType(newAnoyPath,value,confChild,errOut)
                if(not isValid):
                    return False
            return True
        else:
            return False

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
                        listType=listVal
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


    def checkAnoyList(self,anoyPath,anoyValue,confValue,errOut:bool):
        """
        @Summ: ANOY上で!List型を型確認する関数。

        @Desc:
        - <typeOption>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<typeOption>以外のannotation keyも許容される。
        - <type>には!Type型が入る。

        @Args:
          anoyPath:
            @Summ: anoy内の現在地。
            @Type: List
          anoyValue:
            @Summ: 型確認する値。
          confValue:
            @Summ: list型のoption。
            @Desc:
            - type keyとlength keyがある。
            @Type: Dict
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        """
        eleType=confValue.get("type")
        length=confValue.get("length")
        if(type(anoyValue)==list):
            if(length is not None):
                if(length!=len(anoyValue)):
                    if(errOut):
                        raise AnnotationTypeError(self._curAnoy,anoyPath,"!List")
                    else:
                        return False
            for i in range(len(anoyValue)):
                anoyEle=anoyValue[i]
                newAnoyPath=anoyPath+[i]
                isValid=self.checkAnoyType(newAnoyPath,anoyEle,eleType,errOut)
                if(not isValid):
                    return False
            return True
        else:
            if(errOut):
                raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!List")
            else:
                return False


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

    def checkAnoyEnum(self,anoyPath,anoyValue,confValue:list,errOut):
        """
        @Summ: ANOY上で!Enum型を型確認する関数。

        @Desc:
        - 他の言語のUnion型の役割も兼ねている。
        - 選択できるdata型は、[null,!Bool,!Str,!Int,!Float,!List,!FreeMap]である。
        - 入れ子の下層までは確認しない(浅いdata型確認)。

        @Args:
          anoyPath:
            @Summ: anoy内の現在地。
            @Type: List
          anoyValue:
            @Summ: 型確認する値。
          confValue:
            @Summ: Enum型の選択肢を格納するlist型。
            @Desc: optionListには!Typeのlistが入る。
            @Type: List
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        @Returns:
          @Summ: 正常な値ならばTrue.
          @Type: Bool
        """
        for i in range(len(confValue)):
            option=confValue[i]
            newAnoyPath=anoyPath+[i]
            # !Type型の選択肢。
            if(type(option)==dict):
                isValid=self.checkAnoyType(newAnoyPath,anoyValue,option,errOut=False)
                if(isValid):
                    return True
            # literalの選択肢。
            elif(anoyValue==option):
                return True
        if(errOut):
            raise AnnotationTypeError(self._curAnoy,anoyPath,"!Enum")
        else:
            return False


if(__name__=="__main__"):
    configPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\config01.yaml"
    anoyPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\int_false.yaml"
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    with open(anoyPath,mode="r",encoding="utf-8") as f:
        anoyDict=yaml.safe_load(f)
    tree01=DictTraversal(configDict)
    tree01.anoyFreeSearch([],anoyDict)

