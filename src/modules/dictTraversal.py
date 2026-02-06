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
                    validConfParent=self.checkParent([annoKey,"!Parent"],value)
                    validAnnoValue["!Parent"]=validConfParent
                elif(key=="!Child"):
                    validConfChild=self.checkDataType([annoKey,"!Child"],value)
                    validAnnoValue["!Child"]=validConfChild
                else:
                    raise ConfigYamlError([annoKey,key], "Invalid value as !Parent.")
            # isVisit keyの追加。
            validAnnoValue["isVisit"]=False
            validConfigDict[annoKey]=validAnnoValue
        return validConfigDict
    
    @classmethod
    def checkParent(cls,confPath,value):
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
    def checkDataType(cls,confPath,value):
        """
        @Summ: data型構文を確認する関数。

        @Desc: `!Child`だけでなく、data型の入れ子が発生する際にも呼び出される。

        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          value:
            @Summ: data型構文。
            @Type: Any
        @Returns:
          @Summ: `!Child`のvalueとして有効な値。
          @Type: Dict
        """
        if(type(value)==str):
            newConfPath=confPath+[value]
            match value:
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
        elif(type(value)==dict):
            confChildKey=list(value.keys())
            if(len(confChildKey)!=1):
                raise ConfigYamlError(confPath,"Invalid data type.")
            typeStr=confChildKey[0]
            newConfPath=confPath+[typeStr]
            typeOption=value[typeStr]
            match typeStr:
                case "!Str":
                    validType=cls.checkConfStr(newConfPath,typeOption)
                case "!Int":
                    validType=cls.checkConfInt(newConfPath,typeOption)
                case "!Float":
                    validType=cls.checkConfFloat(newConfPath,typeOption)
                case "!Enum":
                    validType=cls.checkConfEnum(newConfPath,typeOption)
                case "!List":
                    validType=cls.checkConfList(newConfPath,typeOption)
                case "!AnnoMap":
                    validType=cls.checkConfAnnoMap(newConfPath,typeOption)
                case _:
                    raise ConfigYamlError(newConfPath,"Invalid data type.")
        else:
            raise ConfigYamlError(confPath,"Invalid data type.")
        return validType


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
            @Type: Any
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        @Returns:
          @Summ: 正しいdata型の時True。
          @Type: Bool
        """
        if(confType is None):
            self.anoyFreeSearch(anoyPath,data)
            return
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
                isValid=self.checkAnoyFreeMap(anoyPath,data)
                if(not isValid):
                    raise AnnotationTypeError(self._curAnoy,anoyPath,typeStr)
            case "!AnnoMap":
                isValid=self.checkAnoyAnnoMap(anoyPath,data,typeOption)
                if(not isValid):
                    raise AnnotationTypeError(self._curAnoy,anoyPath,typeStr)
            case "!List":
                isValid=self.checkAnoyList(anoyPath,data,typeOption)
                if(not isValid):
                    raise AnnotationTypeError(self._curAnoy,anoyPath,typeStr)
            case "!Enum":
                isValid=self.checkAnoyEnum(anoyPath,data,typeOption)
                if(not isValid):
                    raise AnnotationTypeError(self._curAnoy,anoyPath,typeStr)
            case _:
                if(errOut):
                    raise AnnotationTypeError(self._curAnoy,anoyPath,"!Type")
                else:
                    isValid=False
        return isValid

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
                self.anoyFreeSearch([],anoyDict)
        else:
            for childPath in anoyPath.iterdir():
                self.dirDFS(childPath)


    def dictBFS(self,anoyDict:dict):
        """
        @Summ: anoyDictの中を幅優先探索を開始する関数。

        @Desc:
        - list型は単純に探索する。
        - dict型は型確認しながら探索する。
        - visitQueueには(key(str),value(any))のtupleを入れる。
        - list型の時は、(key(int),value(any))になる。
        @Args:
            anoyDict:
                @Summ: annotation yamlのdict型。
        """
        self._visitQueue=[(None,anoyDict)]
        self._pathQueue=[[]]
        while(True):
            if(self._visitQueue==[]):
                break
            key,value=self._visitQueue.pop(0)
            self._anoyPath=self._pathQueue.pop(0)
            print(key,value)
            print(self._anoyPath)
            self.checkAnoy(key,value)

    def checkAnoy(self,parentKey:str|None,childValue):
        """
        "@Summ": anoyの中身を探索する関数。

        "@Warning": 削除予定。

        "@Desc":
        - 型確認は"!Parent"と"!Child"の2つだ。
        - parentKeyの`!Child`がchildValueを制限する。
        - childValueの`!parent`がparentKeyを制限する。
        - parentKeyがannotationKeyでない時は、"!Parent"も"!Child"も効力を発揮しないので無視。
        - !Childが無い時は、childValue=Noneとして考える。
        - `!Parent`による型確認は、childValueが`!AnnoMap`型の時のみ行われる。

        "@Args":
            parentKey:
                "@Summ": 探索するdict型のkey。
                "@Desc":
                - nullは親要素が存在しないことを表す(つまりvalueがroot要素である)。
                "@Type":
                    Union:
                    - Str
                    - null
            childValue:
                "@Summ": 探索するdict型のvalue。
                "@Type": Any
        "@Error":
        - AnnotationYamlError
        - AnnotationYamlTypeError
        - ConfigurationYamlError
        """
        if(parentKey is None):
            confChild=None    #confChild=Noneの時は型確認をしない。
        elif(type(parentKey)!=str):
            confChild=None
        elif(parentKey[0]=="@"):
            confDictVal=self._configDict.get(parentKey)
            if(confDictVal is None):
                raise AnnotationKeyError(self._curAnoy, self._anoyPath,parentKey)
            confChild=confDictVal.get("!Child")
        else:
            confChild=None
        # anoyの型確認
        if(confChild is None):
            # nestになるlistとdictだけ対処する。
            if(type(childValue)==list):
                for i in range(len(childValue)):
                    element=childValue[i]
                    newPath=self._anoyPath+[i]
                    self._visitQueue.append((i,element))
                    self._pathQueue.append(newPath)
            elif(type(childValue)==dict):
                # !Child=nullであってもfree keyとannotation keyの混合は許さない。
                # keyがstr型でない時は!FreeMapとして扱う。
                isAnnoMap=None
                for key,value in childValue.items():
                    if(type(key)!=str):
                        if(isAnnoMap is None):
                            isAnnoMap=False
                        elif(isAnnoMap==True):
                            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!AnnoMap")
                    elif(key[0]=="@"):
                        if(isAnnoMap is None):
                            isAnnoMap=True
                        elif(isAnnoMap==False):
                            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!FreeMap")
                    else:
                        if(isAnnoMap is None):
                            isAnnoMap=False
                        elif(isAnnoMap==True):
                            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!AnnoMap")
                    newPath=self._anoyPath+[key]
                    self._visitQueue.append((key,value))
                    self._pathQueue.append(newPath)
            return
        typeStr=list(confChild.keys())[0]
        typeOption=confChild[typeStr]
        match typeStr:
            case "!Str":
                self.checkAnoyStr(childValue,typeOption,errOut=True)
            case "!Bool":
                self.checkAnoyBool(childValue,errOut=True)
            case "!Int":
                self.checkAnoyInt(childValue,typeOption,errOut=True)
            case "!Float":
                self.checkAnoyFloat(childValue,typeOption,errOut=True)
            case "!FreeMap":
                self.checkAnoyFreeMap(childValue)
            case "!AnnoMap":
                self.checkAnoyAnnoMap(parentKey,childValue,typeOption)
            case "!List":
                self.checkAnoyList(parentKey,childValue,elementType=typeOption["type"],length=typeOption["length"])
            case "!Enum":
                self.checkAnoyEnum(childValue,typeOption)
            case _:
                raise ConfigYamlError([parentKey,"!Child"])

    def anoyFreeSearch(self,anoyPath,data):
        """
        @Summ: config yamlが指定されていない時に、anoyDictの中を自由に優先探索する関数。

        @Desc:
        - 深さ優先探索。
        - 再帰関数で探索する。
        - 最初は([],長いdict)で、探索が進むごとに(anoyPath,短いdict)になるイメージ。
        - config yamlが指定されていなくても、free keyとannotation keyの混合は許さない。
        - list型やFreeMap型を検知してもconfig yamlは機能しない。AnnoMap型を検知するまでがこの関数の役割だ。
        - anoyFreeSearchは例外を出す関数。

        @Args:
          anoyPath:
            @Summ: anoy上のpath。
            @Desc: root nodeの時は空listを代入。
            @Type: List
          data:
            @Summ: parentに対応する値を代入。
        @Returns:
          @Summ: 型が正常ならばTrue
          @Type: Bool
        """
        if(type(data)==list):
            for i in range(len(data)):
                item=data[i]
                newAnoyPath=anoyPath+[item]
                isValid=self.anoyFreeSearch(newAnoyPath,i)
                if(not isValid):
                    raise AnnotationTypeError(self._curAnoy,anoyPath,"!AnnoMap")
        elif(type(data)==dict):
            keyList=list(data.keys())
            if(0<len(keyList)):
                firstKey=keyList[0]
                if(type(firstKey)!=str):
                    isValid=self.checkAnoyFreeMap(anoyPath,data)
                    if(not isValid):
                        raise AnnotationTypeError(self._curAnoy,anoyPath,"!FreeMap")
                elif(firstKey[0]=="@"):
                    isValid=self.checkAnoyAnnoMap(anoyPath,data,[])
                    if(not isValid):
                        raise AnnotationTypeError(self._curAnoy,anoyPath,"!AnnoMap")
                else:
                    isValid=self.checkAnoyFreeMap(anoyPath,data)
                    if(not isValid):
                        raise AnnotationTypeError(self._curAnoy,anoyPath,"!FreeMap")
        return True


    @classmethod
    def checkConfStr(cls,confPath,typeOption):
        """
        @Summ: config yaml上で!Str型のtype optionを確認する関数。
        
        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          typeOption:
            @Summ: !Strに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: Dict
        @Returns:
          @Summ: 有効なtype option。
          @Type: Dict
        """
        lenMin=None
        lenMax=None
        if(typeOption is None):
            pass
        elif(type(typeOption)!=dict):
            raise ConfigYamlError(confPath)
        else:
            for key,value in typeOption.items():
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

    def checkAnoyStr(self,anoyPath,anoyValue,strOption,errOut:bool):
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
        minLen=strOption.get("min")
        maxLen=strOption.get("max")
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
    def checkConfInt(cls,confPath,typeOption):
        """
        @Summ: config yaml上で!Int型のtype optionを確認する関数。
        
        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          typeOption:
            @Summ: !Intに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: Dict
        @Returns:
          @Summ: 有効なtype option。
          @Type: Dict
        """
        intMin=None
        intMax=None
        if(typeOption is None):
            pass
        elif(type(typeOption)!=dict):
            raise ConfigYamlError(configPath, "Required `!Map` type.")
        else:
            for key,value in typeOption.items():
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

    def checkAnoyInt(self,anoyPath,anoyValue,intOption,errOut:bool):
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
          intOption:
            @Type: Int
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        @Returns:
          @Type: Bool
        """
        minInt=intOption.get("min")
        maxInt=intOption.get("max")
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
    def checkConfFloat(cls,annoKey,typeOption):
        """
        @Summ: config yaml上で!Float型のtype optionを確認する関数。
        
        @Args:
          annoKey:
            @Summ: `!Child!Float`を格納するannotation key。
            @Type: Str
          typeOption:
            @Summ: !Floatに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: Dict
        @Returns:
          @Summ: 有効なtype option。
          @Type: Dict
        """
        floatMin=None
        floatMax=None
        if(typeOption is None):
            pass
        elif(type(typeOption)!=dict):
            raise ConfigYamlError([annoKey,"!Child","!Float"], "Required `!Map` type.")
        else:
            for floatKey,floatVal in typeOption.items():
                match floatKey:
                    case "min":
                        if(type(floatVal)!=int and type(floatVal)!=float):
                            raise ConfigYamlError([annoKey,"!Child","!Float"])    
                        floatMin=floatVal
                    case "max":
                        if(type(floatVal)!=int and type(floatVal)!=float):
                            raise ConfigYamlError([annoKey,"!Child","!Float"])    
                        floatMax=floatVal
                    case _:
                        raise ConfigYamlError([annoKey,"!Child","!Float"])
        return {"!Float":{"min":floatMin,"max":floatMax}}

    def checkAnoyFloat(self,anoyPath,anoyValue,floatOption,errOut:bool):
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
          intOption:
            @Type: Int
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        @Returns:
          @Type: Bool
        """
        minFloat=floatOption.get("min")
        maxFloat=floatOption.get("max")
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

    def checkAnoyFreeMap(self,anoyValue):
        """
        @Summ: ANOY上で!FreeMap型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
        """
        if(type(anoyValue)==dict):
            for key,value in anoyValue.items():
                newPath=self._anoyPath+[key]
                self._visitQueue.append((key,value))
                self._pathQueue.append(newPath)
                if(type(key)==str):
                    if(key[0]=="@"):
                        raise AnnotationTypeError(self._curAnoy,newPath,"!FreeMap")
        else:
            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!FreeMap")

    @classmethod
    def checkConfAnnoMap(cls,annoKey,typeOption):
        """
        @Summ: config yaml上で!AnnoMap型のtype optionを確認する関数。
        
        @Args:
          annoKey:
            @Summ: `!Child!AnnoMap`を格納するannotation key。
            @Type: Str
          typeOption:
            @Summ: !AnnoMapに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: List
        @Returns:
          @Summ: 有効なtype option。
          @Type: Dict
        """
        if(typeOption is None):
            typeOption=[]
        elif(type(typeOption)!=list):
            raise ConfigYamlError([annoKey,"!Child","!AnnoMap"])
        else:
            for i in range(len(typeOption)):
                item=typeOption[i]
                if(item[0]!="@"):
                    raise ConfigYamlError([annoKey,"!Child","!AnnoMap",item])
        return {"!AnnoMap":typeOption}

    def checkAnoyAnnoMap(self,parentKey,anoyValue,annoKeyList:list=[]):
        """
        @Summ: ANOY上で!FreeMap型を型確認する関数。

        @Desc:
        - <annoKeyList>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<annoKeyList>以外のannotation keyも許容される。

        @Args:
          parentKey:
            @Summ: 親要素のannotation key。
            @Type: Str
          anoyValue:
            @Summ: 型確認する値。
          annoKeyList:
            @Summ: 子要素になれるannotation keyのlist。
            @Desc:
            - 空lsitの時は任意のannotation keyを受け入れる。
            - これは全てのannotation keyが入ったlist型と同じ挙動をする。
            @Type: List
            @Default: []
        """
        if(type(anoyValue)==dict):
            for key,value in anoyValue.items():
                newPath=self._anoyPath+[key]
                self._visitQueue.append((key,value))
                self._pathQueue.append(newPath)
                # !Parentの確認。
                configValue=self._configDict.get(key)
                if(configValue is None):
                    raise AnnotationKeyError(self._curAnoy,newPath,key)
                confParent=configValue.get("!Parent")
                if(confParent is not None):
                    if(parentKey not in confParent):
                        raise AnnotationTypeError(self._curAnoy,newPath,"!Parent")
                if(annoKeyList!=[]):
                    if(key not in annoKeyList):
                        raise AnnotationTypeError(self._curAnoy,newPath,"!AnnoMap")
        else:
            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!AnnoMap")

    @classmethod
    def checkConfList(cls,annoKey,typeOption):
        """
        @Summ: config yaml上で!List型のtype optionを確認する関数。
        
        @Args:
          annoKey:
            @Summ: `!Child!List`を格納するannotation key。
            @Type: Str
          typeOption:
            @Summ: !Listに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: Dict
        @Returns:
          @Summ: 有効なtype option。
          @Type: Dict
        """
        listType=None
        listLength=None
        if(typeOption is None):
            pass
        elif(type(typeOption)!=dict):
            raise ConfigYamlError([annoKey,"!Child","!List"])
        else:
            for listKey,listVal in typeOption.items():
                match listKey:
                    case "type":
                        listType=listVal
                    case "length":
                        if(listVal is None):
                            continue
                        elif(type(listVal)!=int):
                            raise ConfigYamlError([annoKey,"!Child","!List",listKey])
                        elif(listVal<=0):
                            raise ConfigYamlError([annoKey,"!Child","!List",listKey])
                        listLength=listVal
                    case _:
                        raise ConfigYamlError([annoKey,"!Child","!List",listKey])
        return {"!List":{"type":listType,"length":listLength}}


    def checkAnoyList(self,anoyPath,anoyValue,listOption,errOut:bool):
        """
        @Summ: ANOY上で!List型を型確認する関数。

        @Desc:
        - <typeOption>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<typeOption>以外のannotation keyも許容される。

        @Args:
          anoyPath:
            @Summ: anoy内の現在地。
            @Type: List
          anoyValue:
            @Summ: 型確認する値。
          listOption:
            @Summ: list型のoption。
            @Type: Dict
          errOut:
            @Summ: 例外を出すならばTrue、Bool型で出力するならばFalse。
            @Type: Bool
        """
        elementType=listOption.get("type")
        length=listOption.get("length")
        raiseError=False
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
                #以下未確定。
                if(elementType is not None):
                    match elementType:
                        case "!Str":
                            if(type(anoyEle)!=str):
                                raise AnnotationTypeError(self._curAnoy,newAnoyPath,"!List")
                        case "!Bool":
                            if(type(anoyEle)!=bool):
                                raise AnnotationTypeError(self._curAnoy,newAnoyPath,"!List")
                        case "!Int":
                            if(type(anoyEle)!=int):
                                raise AnnotationTypeError(self._curAnoy,newAnoyPath,"!List")
                        case "!Float":
                            if(type(anoyEle)!=float):
                                raise AnnotationTypeError(self._curAnoy,newAnoyPath,"!List")
                        case _:
                            raise ConfigYamlError([parentKey,"!Child"])
        else:
            raiseError=True
        # error出すかの判断。
        if(raiseError):
            if(errOut):
                raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!List")
            else:
                return False
        else:
            return True

    @classmethod
    def checkConfEnum(cls,annoKey,typeOption):
        """
        @Summ: config yaml上で!Enum型のtype optionを確認する関数。
        
        @Args:
          annoKey:
            @Summ: `!Child!Enum`を格納するannotation key。
            @Type: Str
          typeOption:
            @Summ: !Enumに対応するtype option。
            @Type: List
        @Returns:
          @Summ: 有効なtype option。
          @Type: Dict
        """
        enumOption=[]
        if(type(typeOption)!=list):
            raise ConfigYamlError([annoKey,"!Child","!Enum"])
        else:
            for item in typeOption:
                if(type(item)==list):
                    raise ConfigYamlError([annoKey,"!Child","!Enum",item])
                elif(type(item)==dict):
                    keyList=list(item.keys())
                    if(len(keyList)!=1):
                        raise ConfigYamlError([annoKey,"!Child","!Enum",item])
                    enumOption.append(keyList[0])
                else:
                    enumOption.append(item)
        return {"!Enum":enumOption}

    def checkAnoyEnum(self,anoyValue,optionList:list):
        """
        @Summ: ANOY上で!Enum型を型確認する関数。

        @Desc:
        - 他の言語のUnion型の役割も兼ねている。
        - 選択できるdata型は、[null,!Bool,!Str,!Int,!Float,!List,!FreeMap]である。
        - 入れ子の下層までは確認しない(浅いdata型確認)。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          optionList:
            @Summ: Enum型の選択肢を格納するlist型。
            @Type: List
        """
        for i in range(len(optionList)):
            option=optionList[i]
            if(option is None and anoyValue is None):
                    return
            match option:
                case "!Str":
                    if(type(anoyValue)==str):
                        return
                case "!Bool":
                    if(type(anoyValue)==bool):
                        return
                case "!Int":
                    if(type(anoyValue)==int):
                        return
                case "!Float":
                    if(type(anoyValue)==float):
                        return
                case "!List":
                    if(type(anoyValue)==list):
                        return
                case "!FreeMap":
                    if(type(anoyValue)==dict):
                        return
                case _:
                    if(anoyValue==option):
                        return
        raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!Enum")


if(__name__=="__main__"):
    configPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\config01.yaml"
    anoyPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\int_false.yaml"
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    with open(anoyPath,mode="r",encoding="utf-8") as f:
        anoyDict=yaml.safe_load(f)
    tree01=DictTraversal(configDict)
    tree01.anoyFreeSearch([],anoyDict)

