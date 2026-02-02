import yaml
from pprint import pprint
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
        pprint(self._configDict)
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
                    validConfParent=self.checkConfParent(newConfigPath,value)
                    validAnnoValue["!Parent"]=validConfParent
                elif(key=="!Child"):
                    validConfChild=self.checkConfType(newConfigPath,value)
                    validAnnoValue["!Child"]=validConfChild
                else:
                    raise ConfigYamlError([annoKey], "Unknown config key is found.")
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
    def checkConfType(cls,confPath,value):
        """
        @Summ: config yaml上でdata型構文を確認する関数。

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
                    validDict=cls.checkConfStr(newConfPath,None)
                case "!Bool":
                    validDict={"!Bool":{}}
                case "!Int":
                    validDict=cls.checkConfInt(newConfPath,None)
                case "!Float":
                    validDict=cls.checkConfFloat(newConfPath,None)
                case "!List":
                    validDict=cls.checkConfList(newConfPath,None)
                case "!FreeMap":
                    validDict={"!FreeMap":{}}
                case "!AnnoMap":
                    validDict=cls.checkConfAnnoMap(newConfPath,None)
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
                    validDict=cls.checkConfStr(newConfPath,typeOption)
                case "!Int":
                    validDict=cls.checkConfInt(newConfPath,typeOption)
                case "!Float":
                    validDict=cls.checkConfFloat(newConfPath,typeOption)
                case "!Enum":
                    validDict=cls.checkConfEnum(newConfPath,typeOption)
                case "!List":
                    validDict=cls.checkConfList(newConfPath,typeOption)
                case "!AnnoMap":
                    validDict=cls.checkConfAnnoMap(newConfPath,typeOption)
                case _:
                    raise ConfigYamlError(newConfPath,"Invalid data type.")
        else:
            raise ConfigYamlError(confPath,"Invalid data type.")
        return validDict

    def checkAnoyType(self,anoyPath,data,confType):
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
        @Returns:
          @Summ: `!Child`のvalueとして有効な値。
          @Type: Dict
        """
        if(confType is None):
            self.anoyFreeSearch(anoyPath,data)
            return
        typeStr=list(confType.keys())[0]
        typeOption=confType[typeStr]
        match typeStr:
            case "!Str":
                isValid=self.checkAnoyStr(data,typeOption)
                if(not isValid):
                    raise AnnotationTypeError(self._curAnoy,anoyPath,typeStr)
            case "!Bool":
                isValid=self.checkAnoyBool(data)
                if(not isValid):
                    raise AnnotationTypeError(self._curAnoy,anoyPath,typeStr)
            case "!Int":
                isValid=self.checkAnoyInt(data,typeOption)
                if(not isValid):
                    raise AnnotationTypeError(self._curAnoy,anoyPath,typeStr)
            case "!Float":
                isValid=self.checkAnoyFloat(data,typeOption)
                if(not isValid):
                    raise AnnotationTypeError(self._curAnoy,anoyPath,typeStr)
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
                raise ConfigYamlError(anoyPath)

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
                self.anoyFreeSearch([],anoyDict)
        else:
            for childPath in anoyPath.iterdir():
                self.dirDFS(childPath)


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

    def checkAnoyStr(self,data,typeOption)->bool:
        """
        @Summ: ANOY上で!Str型を型確認する関数。

        @Desc: typeOptionの型確認はcheckConfStr()で行っている前提。

        @Args:
          data:
            @Summ: ANOY上の値。型確認する対象。
          typeOption:
            @Summ: str型のtypeOptionが入る。
            @Type: Dict
        @Returns:
          @Summ: 正常なdata型ならばTrue.
          @Type: Bool
        """
        lenMin=typeOption["min"]
        lenMax=typeOption["max"]
        if(type(data)==str):
            if(lenMin is not None):
                if(len(data)<lenMin):
                    return False
            if(lenMax is not None):
                if(lenMax<len(data)):
                    return False
            return True
        else:
            return False

    def checkAnoyBool(self,data):
        """
        @Summ: ANOY上で!Bool型を型確認する関数。

        @Args:
          data:
            @Summ: 型確認する値。
        @Returns:
          @Summ: data型が正常の時True.
          @Type: Bool
        """
        if(type(data)==bool):
            return True
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

    def checkAnoyInt(self,data,typeOption):
        """
        @Summ: ANOY上で!Int型を型確認する関数。

        @Args:     
          data:
            @Summ: ANOY上の値。型確認する対象。
          typeOption:
            @Summ: !Int型のtypeOptionが入る。
            @Type: Dict
        @Returns:
          @Summ: 正常なdata型ならばTrue.
          @Type: Bool
        """
        intMin=typeOption["min"]
        intMax=typeOption["max"]
        if(type(data)==int):
            if(intMin is not None):
                if(data<intMin):
                    return False
            if(intMax is not None):
                if(intMax<data):
                    return False
            return True
        else:
            return False

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
                        if(type(value)==int or type(value)==float):
                            if(floatMax is not None):
                                if(floatMax<value):
                                    raise ConfigYamlError(newConfPath)
                        else:
                            raise ConfigYamlError(newConfPath)
                    case "max":
                        floatMax=value
                        if(type(value)==int or type(value)==float):
                            if(floatMax is not None):
                                if(value<floatMin):
                                    raise ConfigYamlError(newConfPath)
                        else:
                            raise ConfigYamlError(newConfPath)
                    case _:
                        raise ConfigYamlError(newConfPath)
        return {"!Float":{"min":floatMin,"max":floatMax}}

    def checkAnoyFloat(self,data,typeOption):
        """
        @Summ: ANOY上で!Float型を型確認する関数。

        @Args:
          data:
            @Summ: ANOY上の値。型確認する対象。
          typeOption:
            @Summ: !Float型のtypeOptionが入る。
            @Type: Dict
        @Returns:
          @Summ: 正常なdata型ならばTrue.
          @Type: Bool
        """
        floatMin=typeOption["min"]
        floatMax=typeOption["max"]
        if(type(data)==int or type(data)==float):
            if(floatMin is not None):
                if(data<floatMin):
                    return False
            if(floatMax is not None):
                if(floatMax<data):
                    return False
            return True
        else:
            return False

    def checkAnoyFreeMap(self,anoyPath,data):
        """
        @Summ: ANOY上で!FreeMap型を型確認する関数。

        @Args:
          anoyPath:
            @Summ: anoy上のpath。
            @Type: List
          data:
            @Summ: ANOY上の値。型確認する対象。
        @Returns:
          @Summ: 正常なdata型ならばTrue.
          @Type: Bool
        """
        if(type(data)==dict):
            for key,value in data.items():
                newAnoyPath=anoyPath+[key]
                if(key[0]=="@"):
                    return False
                self.anoyFreeSearch(newAnoyPath,value)
            return True
        else:
            return False

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

    def checkAnoyAnnoMap(self,anoyPath,data,typeOption:list):
        """
        @Summ: ANOY上で!FreeMap型を型確認する関数。

        @Note: 未完成。子要素を探索するか否か。。。

        @Args:
          parentKey:
            @Summ: 親要素のannotation key。
            @Type: Str
          anoyPath:
            @Summ: anoy上のpath。
            @Type: List
          data:
            @Summ: ANOY上の値。型確認する対象。
          typeOption:
            @Summ: 子要素になれるannotation keyのlist。
            @Desc:
            - 最低限必要なannotation keyのlistが入る。
            - 空lsitの時は任意のannotation keyを受け入れる。
            @Type: List
        @Returns:
          @Summ: 正常なdata型ならばTrue.
          @Type: Bool
        """
        if(anoyPath==[]):
            annoKey=None
        else:
            annoKey=anoyPath[-1]
        if(type(data)==dict):
            for key,value in data.items():
                newAnoyPath=anoyPath+[key]
                # !Parentの確認。
                configValue=self._configDict.get(key)
                if(configValue is None):
                    return False
                confParent=configValue.get("!Parent")
                if(confParent is not None):
                    if(annoKey not in confParent):
                        return False
                if(typeOption!=[]):
                    if(key not in typeOption):
                        return False
                # 子要素を探索。
                confType=configValue.get("!Child")
                self.checkAnoyType(newAnoyPath,value,confType)
            return True
        else:
            return False

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
                        validValue=cls.checkConfType(newConfPath,value)
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


    def checkAnoyList(self,anoyPath,data,typeOption):
        """
        @Summ: ANOY上で!List型を型確認する関数。

        @Desc:
        - <typeOption>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<typeOption>以外のannotation keyも許容される。

        @Args:
          anoyPath:
            @Summ: anoy上のpath。
            @Type: List
          data:
            @Summ: ANOY上の値。型確認する対象。
          typeOption:
            @Summ: !List型のtypeOptionが入る。
            @Type: Dict
        @Returns:
          @Summ: 正常なdata型ならばTrue.
          @Type: Bool
        """
        confType=typeOption["type"]
        length=typeOption["length"]
        if(type(data)==list):
            # lengthを確認
            if(length is not None):
                if(length!=len(data)):
                    return False
            for i in range(len(data)):
                element=data[i]
                newAnoyPath=anoyPath+[i]
                # typeを確認
                if(confType is not None):
                    self.checkAnoyType(newAnoyPath,element,confType)
            return True
        else:
            return False

    @classmethod
    def checkConfEnum(cls,confPath,typeOption):
        """
        @Summ: config yaml上で!Enum型のtype optionを確認する関数。

        @Desc:
        - scalar型がdict型であることも許容している。{scalar:@Summ:xxx}みたいな構文。
        - checkConfの時点で、data型構文をdict型に、scalarはscalarにしておく。
        - list型は選択肢にはできない。
        
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
                if(type(item)==str):
                    item
                elif(type(item)==list):
                    raise ConfigYamlError(newConfPath)
                elif(type(item)==dict):
                    keyList=list(item.keys())
                    if(len(keyList)!=1):
                        raise ConfigYamlError(newConfPath)
                    uniqueKey=keyList[0]
                    if(type(uniqueKey)!=str):
                        # dict型で表現されたstr型以外のscalar型。
                        enumOption.append(uniqueKey)
                    elif(uniqueKey[0]!="!"):
                        # dict型で表現されたstr型。
                        enumOption.append(uniqueKey)
                    else:
                        # type構文。
                        validDict=cls.checkConfType(newConfPath,item)
                        enumOption.append(validDict)
                else:
                    # scalar型で表現されたscalar型。
                    enumOption.append(item)
        return {"!Enum":enumOption}

    def checkAnoyEnum(self,anoyPath,data,optionList:list):
        """
        @Summ: ANOY上で!Enum型を型確認する関数。

        @Note: 未完成。!Typeとただのliteralを分岐する必要がある。

        @Desc:
        - 他の言語のUnion型の役割も兼ねている。
        - 選択肢がdict型ならば、data型構文。
        - 選択肢がscalarならば、scalarの中から選択する。

        @Args:
          anoyPath:
            @Summ: anoy上のpath。
            @Type: List
          data:
            @Summ: ANOY上の値。型確認する対象。
          optionList:
            @Summ: Enum型の選択肢を格納するlist型。
            @Type: List
        @Returns:
          @Summ: 正常なdata型ならばTrue.
          @Type: Bool
        """
        for i in range(len(optionList)):
            option=optionList[i]
            if(option is None and data is None):
                return True
            elif(type(option)==dict):
                # dict型はdata型を表す。
                typeStr=list(option.keys())[0]
                typeOption=option[typeStr]
                match typeStr:
                    case "!Str":
                        isValid=self.checkAnoyStr(data,typeOption)
                        if(isValid):
                            return True
                    case "!Bool":
                        isValid==self.checkAnoyBool(data,typeOption)
                        if(isValid):
                            return True
                    case "!Int":
                        isValid=self.checkAnoyInt(data,typeOption)
                        if(isValid):
                            return True
                    case "!Float":
                        isValid=self.checkAnoyFloat(data,typeOption)
                        if(isValid):
                            return True
                    case "!List":
                        isValid=self.checkAnoyList(anoyPath,data,typeOption)
                        if(isValid):
                            return True
                    case "!FreeMap":
                        isValid=self.checkAnoyFreeMap(anoyPath,data,typeOption)
                        if(isValid):
                            return True
                    case _:
                            return False
            elif(data==option):  # scalar用の処理。
                    return True
        # 全てに合致しない時
        return False


if(__name__=="__main__"):
    configPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\config01.yaml"
    anoyPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\int_false.yaml"
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    with open(anoyPath,mode="r",encoding="utf-8") as f:
        anoyDict=yaml.safe_load(f)
    tree01=DictTraversal(configDict)
    tree01.dictBFS(anoyDict)

