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
                newConfigPath=[annoKey,key]
                if(key[0]=="@"):
                    continue
                elif(key=="!Parent"):
                    validConfParent=self.checkParent(newConfigPath,value)
                    validAnnoValue["!Parent"]=validConfParent
                elif(key=="!Child"):
                    validConfChild=self.checkDataType(newConfigPath,value)
                    validAnnoValue["!Child"]=validConfChild
                else:
                    raise ConfigYamlError([annoKey], "Unknown config key is found.")
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
            newConfPath=configPath+typeStr
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


    def dirDFS(self,anoyPath:Path):
        """
        @Summ: directory内を深さ優先探索する関数。

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
                self.dictBFS(anoyDict)
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
                isAnnoMap=None
                for key,value in childValue.items():
                    if(isAnnoMap is None):
                        if(key[0]=="@"):
                            isAnnoMap=True
                        else:
                            isAnnoMap=False
                    else:
                        if(isAnnoMap==True and key[0]!="@"):
                            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!AnnoMap")
                        elif(isAnnoMap==False and key[0]=="@"):
                            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!FreeMap")
                    newPath=self._anoyPath+[key]
                    self._visitQueue.append((key,value))
                    self._pathQueue.append(newPath)
            return
        typeStr=list(confChild.keys())[0]
        typeOption=confChild[typeStr]
        match typeStr:
            case "!Str":
                self.checkAnoyStr(childValue,typeOption)
            case "!Bool":
                self.checkAnoyBool(childValue)
            case "!Int":
                self.checkAnoyInt(childValue,typeOption)
            case "!Float":
                self.checkAnoyFloat(childValue,typeOption)
            case "!FreeMap":
                self.checkAnoyFreeMap(childValue)
            case "!AnnoMap":
                self.checkAnoyAnnoMap(parentKey,childValue,typeOption)
            case "!List":
                self.checkAnoyList(parentKey,childValue,typeOption)
            case "!Enum":
                self.checkAnoyEnum(childValue,typeOption)
            case _:
                raise ConfigYamlError([parentKey,"!Child"])

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
          @Summ: 有効なdata型構文。
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

    def checkAnoyStr(self,anoyValue,typeOption):
        """
        @Summ: ANOY上で!Str型を型確認する関数。

        @Desc: typeOptionの型確認はcheckConfStr()で行っている前提。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          typeOption:
            @Summ: str型のtypeOptionが入る。
            @Type: Dict
        """
        lenMin=typeOption["min"]
        lenMax=typeOption["max"]
        if(type(anoyValue)==str):
            if(lenMin is not None):
                if(len(anoyValue)<lenMin):
                    raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!Str")
            if(lenMax is not None):
                if(lenMax<len(anoyValue)):
                    raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!Str")
        else:
            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!Str")

    def checkAnoyBool(self,anoyValue):
        """
        @Summ: ANOY上で!Bool型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
        """
        if(type(anoyValue)!=bool):
            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!Bool")

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
          @Summ: 有効なdata型構文。
          @Type: Dict
        """
        intMin=None
        intMax=None
        if(typeOption is None):
            pass
        elif(type(typeOption)!=dict):
            raise ConfigYamlError(configPath)
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

    def checkAnoyInt(self,anoyValue,typeOption):
        """
        @Summ: ANOY上で!Int型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          typeOption:
            @Summ: !Int型のtypeOptionが入る。
            @Type: Dict
        """
        intMin=typeOption["min"]
        intMax=typeOption["max"]
        if(type(anoyValue)==int):
            if(intMin is not None):
                if(anoyValue<intMin):
                    raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!Int")
            if(intMax is not None):
                if(intMax<anoyValue):
                    raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!Int")
            return
        else:
            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!Int")

    @classmethod
    def checkConfFloat(cls,confPath,typeOption):
        """
        @Summ: config yaml上で!Float型のtype optionを確認する関数。
        
        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          typeOption:
            @Summ: !Floatに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: Dict
        @Returns:
          @Summ: 有効なdata型構文。
          @Type: Dict
        """
        floatMin=None
        floatMax=None
        if(typeOption is None):
            pass
        elif(type(typeOption)!=dict):
            raise ConfigYamlError(confPath)
        else:
            for key,value in typeOption.items():
                newConfPath=confPath+[key]
                match key:
                    case "min":
                        floatMin=value
                        if(type(value)==int):
                            if(floatMax is not None):
                                if(floatMax<value):
                                    raise ConfigYamlError(newConfPath)
                        else:
                            raise ConfigYamlError(newConfPath)
                    case "max":
                        floatMax=value
                        if(type(value)==int):
                            if(floatMax is not None):
                                if(value<floatMin):
                                    raise ConfigYamlError(newConfPath)
                        else:
                            raise ConfigYamlError(newConfPath)
                    case _:
                        raise ConfigYamlError(newConfPath)
        return {"!Float":{"min":floatMin,"max":floatMax}}

    def checkAnoyFloat(self,anoyValue,typeOption):
        """
        @Summ: ANOY上で!Float型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          typeOption:
            @Summ: !Float型のtypeOptionが入る。
            @Type: Dict
        """
        floatMin=typeOption["min"]
        floatMax=typeOption["max"]
        if(type(anoyValue)==int or type(anoyValue)==float):
            if(floatMin is not None):
                if(anoyValue<floatMin):
                    raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!Float")
            if(floatMax is not None):
                if(floatMax<anoyValue):
                    raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!Float")
            return
        else:
            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!Float")

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
                if(key[0]=="@"):
                    raise AnnotationTypeError(self._curAnoy,newPath,"!FreeMap")
        else:
            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!FreeMap")

    @classmethod
    def checkConfAnnoMap(cls,confPath,typeOption):
        """
        @Summ: config yaml上で!AnnoMap型のtype optionを確認する関数。
        
        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          typeOption:
            @Summ: !AnnoMapに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: List
        @Returns:
          @Summ: 有効なdata型構文。
          @Type: Dict
        """
        if(typeOption is None):
            typeOption=[]
        elif(type(typeOption)!=list):
            raise ConfigYamlError(confPath)
        else:
            for i in range(len(typeOption)):
                item=typeOption[i]
                newConfPath=confPath+[item]
                if(item[0]!="@"):
                    raise ConfigYamlError(newConfPath)
        return {"!AnnoMap":typeOption}

    def checkAnoyAnnoMap(self,parentKey,anoyValue,typeOption:list=[]):
        """
        @Summ: ANOY上で!FreeMap型を型確認する関数。

        @Desc:
        - <typeOption>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<typeOption>以外のannotation keyも許容される。

        @Args:
          parentKey:
            @Summ: 親要素のannotation key。
            @Type: Str
          anoyValue:
            @Summ: 型確認する値。
          typeOption:
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
                if(typeOption!=[]):
                    if(key not in typeOption):
                        raise AnnotationTypeError(self._curAnoy,newPath,"!AnnoMap")
        else:
            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!AnnoMap")

    @classmethod
    def checkConfList(cls,confPath,typeOption):
        """
        @Summ: config yaml上で!List型のtype optionを確認する関数。

        @Desc: type keyがある時は入れ子になる。
        
        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          typeOption:
            @Summ: !Listに対応するtype option。
            @Desc: Noneの時はstring_formatとして処理する。
            @Type: Dict
        @Returns:
          @Summ: 有効なdata型構文。
          @Type: Dict
        """
        listType=None
        listLength=None
        if(typeOption is None):
            pass
        elif(type(typeOption)!=dict):
            raise ConfigYamlError(confPath)
        else:
            for key,value in typeOption.items():
                newConfPath=confPath+[key]
                match key:
                    case "type":
                        validValue=cls.checkDataType(newConfPath,value)
                        listType=validValue
                    case "length":
                        listLength=value
                        if(type(value)!=int):
                            raise ConfigYamlError(newConfPath)
                        elif(value<=0):
                            raise ConfigYamlError(newConfPath)
                    case _:
                        raise ConfigYamlError(newConfPath)
        return {"!List":{"type":listType,"length":listLength}}


    def checkAnoyList(self,parentKey,anoyValue,typeOption):
        """
        @Summ: ANOY上で!List型を型確認する関数。

        @Desc:
        - <typeOption>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<typeOption>以外のannotation keyも許容される。

        @Args:
          parentKey:
            @Summ: 親のkey。
            @Type: Str
          anoyValue:
            @Summ: 型確認する値。
          typeOption:
            @Summ: !List型のtypeOptionが入る。
            @Type: Dict
        """
        elementType=typeOption["type"]
        length=typeOption["length"]
        if(type(anoyValue)==list):
            if(length is not None):
                if(length!=len(anoyValue)):
                    raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!List")
            for i in range(len(anoyValue)):
                element=anoyValue[i]
                newPath=self._anoyPath+[i]
                if(elementType is not None):
                    match elementType:
                        case "!Str":
                            if(type(element)!=str):
                                raise AnnotationTypeError(self._curAnoy,newPath,"!List")
                        case "!Bool":
                            if(type(element)!=bool):
                                raise AnnotationTypeError(self._curAnoy,newPath,"!List")
                        case "!Int":
                            if(type(element)!=int):
                                raise AnnotationTypeError(self._curAnoy,newPath,"!List")
                        case "!Float":
                            if(type(element)!=float):
                                raise AnnotationTypeError(self._curAnoy,newPath,"!List")
                        case _:
                            raise ConfigYamlError([parentKey,"!Child"])
                self._visitQueue.append((i,element))
                self._pathQueue.append(newPath)
        else:
            raise AnnotationTypeError(self._curAnoy,self._anoyPath,"!List")

    @classmethod
    def checkConfEnum(cls,confPath,typeOption):
        """
        @Summ: config yaml上で!Enum型のtype optionを確認する関数。
        
        @Args:
          confPath:
            @Summ: config yaml上の位置。
            @Type: List
          typeOption:
            @Summ: !Enumに対応するtype option。
            @Type: List
        @Returns:
          @Summ: 有効なdata型構文。
          @Type: Dict
        """
        enumOption=[]
        if(type(typeOption)!=list):
            raise ConfigYamlError(confPath)
        else:
            for item in typeOption:
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
    tree01.dictBFS(anoyDict)

