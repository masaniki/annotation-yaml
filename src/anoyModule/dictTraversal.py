import yaml
from pathlib import Path

from .anoyErrors import AnnotationYamlError,ConfigurationYamlError,AnnotationYamlTypeError

class DictTraversal():
    """
    @Summ: 辞書型の中身を探索するclass

    @InsVars:
        _configDict:
            @Summ: config yamlを構文解析した後の値を格納する。
            @Desc:
            - !ChildValueの値は{"!ChildValue": {typeString(str):typOption(dict)}}という形式に直す。
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
        _curFile:
            @Summ: 現在探索中のANOY file名。
            @ComeFrom: current file.
            @Type: Str
        _curPath:
            @Summ: _curFile内での現在地。
            @ComeFrom: current path/
            @Type: List
    """

    def __init__(self,configDict:dict):
        """
        @Summ: constructor.
        """
        self._configDict=self.parseConfig(configDict)
        self._visitQueue=[]
        self._pathQueue=[]
        self._curFile=""
        self._curPath=[]
    
    def parseConfig(self,configDict:dict)->dict:
        """
        @Summ: configDictを構文解析する関数。

        @Desc
        - configDictに"isVisit" keyを追加し、annotation keyを使用したかを記録する。

        @Returns:
          @Summ: 型確認して、余計なものを取り除いたconfigDict。
          @Type: dict
        """
        newConfigDict={}  # 整形されたconfigDict
        for annoKey in configDict.items():
            if(annoKey[0]!="@" or annoKey[0]!="!"):
                raise ConfigurationYamlError(f"{annoKey} is invalid definition.")
            valueDict=configDict[annoKey]
            if(type(valueDict)!=dict):
                raise ConfigurationYamlError(f"{annoKey} is invalid definition.")
            # `!parentKey`の型確認
            confParent=valueDict.get("!ParentKey")
            if(confParent is not None):
                if(type(confParent)!=type):
                    raise ConfigurationYamlError(f"{annoKey} is invalid definition.")
                for item in confParent:
                    if(item[0]!="@"):
                        raise ConfigurationYamlError(f"{annoKey} is invalid definition.")
                newConfigDict["!ParentKey"]=confParent.copy()
            # `!ChildValue`の型確認
            confChild=valueDict.get("!ChildValue")
            if(confChild is not None):
                if(type(confChild)==str):
                    match confChild:
                        case "!Str":
                            newConfChild={"!Str":{"length":None,"min":None,"max":None}}
                        case "!Bool":
                            newConfChild={"!Bool":{}}
                        case "!Int":
                            newConfChild={"!Int":{"min":None,"max":None}}
                        case "!Float":
                            newConfChild={"!Float":{"min":None,"max":None}}
                        case "!List":
                            newConfChild={"!List":{"type":None,"length":None}}
                        case "!FreeMap":
                            newConfChild={"!FreeMap":{}}
                        case "!AnnoMap":
                            newConfChild={"!AnnoMap":[]}
                        case _:
                            raise ConfigurationYamlError(f"{annoKey} is invalid definition.")
                elif(type(confChild)==dict):
                    confChildKey=list(confChild.keys())
                    if(len(confChildKey)!=1):
                        raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                    typeStr=confChildKey[0]
                    typeOption=confChild[typeStr]
                    match typeStr:
                        case "!Str":
                            if(type(typeOption)!=dict):
                                raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                            strLength=None
                            strMin=None
                            strMax=None
                            for strKey,strVal in typeOption.items():
                                match strKey:
                                    case "length":
                                        if(strMin is None and strMax is None):
                                            strLength=strVal
                                        else:
                                            raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                                    case "min":
                                        if(strLength is None):
                                            strMin=strVal
                                        else:
                                            raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                                    case "max":
                                        if(strLength is None):
                                            strMax=strVal
                                        else:
                                            raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                                    case _:
                                        raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                            newConfChild={"!Str":{"length":strLength,"min":strMin,"max":strMax}}
                        case "!Int":
                            if(type(typeOption)!=dict):
                                raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                            intMin=None
                            intMax=None
                            for intKey,intVal in typeOption.items():
                                match intKey:
                                    case "min":
                                        intMin=intVal
                                    case "max":
                                        intMax=intVal
                                    case _:
                                        raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                            newConfChild={"!Int":{"min":intMin,"max":intMax}}
                        case "!Float":
                            if(type(typeOption)!=dict):
                                raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                            floatMin=None
                            floatMax=None
                            for floatKey,floatVal in typeOption.items():
                                match floatKey:
                                    case "min":
                                        floatMin=floatVal
                                    case "max":
                                        floatMax=floatVal
                                    case _:
                                        raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                            newConfChild={"!Float":{"min":floatMin,"max":floatMax}}
                        case "!Enum":
                            if(type(typeOption)!=list):
                                raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                            newConfChild={"!Enum":typeOption}
                        case "!List":
                            if(type(typeOption)!=dict):
                                raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                            listType=None
                            listLength=None
                            for listKey,listVal in typeOption.items():
                                match listKey:
                                    case "type":
                                        listType=listVal
                                    case "length":
                                        listLength=listVal
                                    case _:
                                        raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                            newConfChild={"!List":{"type":listType,"length":listLength}}
                        case "!AnnoDict":
                            if(type(typeOption)!=list):
                                raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                            for i in len(typeOption):
                                item=typeOption[i]
                                if(item[0]!="@"):
                                    raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                            newConfChild={"!AnnoDict":typeOption}
                        case _:
                            raise ConfigurationYamlError(f"`{annoKey}` has invalid definition.")
                else:
                    raise ConfigurationYamlError(f"{annoKey} is invalid definition.")
                newConfigDict["!ChildValue"]=newConfChild
            # isVisit keyの追加。
            valueDict["isVisit"]=False
        return newConfigDict


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
                self._curFile=anoyPath
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
            pathList=self._pathQueue.pop(0)
            # print(key,value)
            # print(pathList)
            self.typeCheck(key,value,pathList)

    def typeCheck(self,parentKey:str|None,childValue,path:list):
        """
        "@Summ": annoDict内を探索する関数。

        "@Desc":
        - 型確認は"!ParentKey"と"!ChildValue"の2つだ。
        - annotationKeyが親でない時は、"!ParentKey"も"!ChildValue"も効力を発揮しないので無視。
        - ただし、annoKeyがNoneの時は、"!ParentKey"が効力を発揮する場合がある。
        - !ChildValueが無い時は何もしない。
        - !ChildValueが無い時は、childValue=nullとして考える。
        - valueがanoyDict型の時のみ、!ParentKeyの型確認が行われる。

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
            path:
                @Summ: 今まで経由したkeyのlist。
                @Type: List
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
                raise AnnotationYamlError(f"{parentKey} is not found.")
            confChild=confDictVal.get("!ChildValue")
        else:
            confChild=None
        # anoyの型確認
        if(confChild is None): #Noneの処理方法は不明。
            pass
        typeStr=[confChild.keys()][0]
        confChildVal=confChild[typeStr]
        match typeStr:
            case "!Str":
                self.checkStr(childValue,path,**confChildVal)
            case "!Bool":
                self.checkBool(childValue,path)
            case "!Int":
                self.checkInt(childValue,path,**confChildVal)
            case "!Float":
                self.checkFloat(childValue,path,**confChildVal)
            case "!FreeMap":
                self.checkFreeMap(childValue,path)
            case "!AnnoMap":
                self.checkAnnoMap(childValue,path,confChildVal)
            case "!List":
                self.checkList(childValue,path,elementType=confChildVal["type"],length=confChildVal["length"])
            case "!Enum":
                self.checkEnum(childValue,path,confChildVal)
            case _:
                raise ConfigurationYamlError(f"{parentKey} is invalid definition.")

    def checkStr(self,anoyValue,path:list,length=None,min=None,max=None):
        """
        @Summ: !Str型を型確認する関数。

        @Desc:
        - <length>と<min>、<length>と<max>の両立は不可能であるが、この関数ではその確認を行わない。
        - 呼び出し時にその確認を行うべきである。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          path:
            @Summ: 現在探索している場所。
            @Type: List
          length:
            @Summ: 文字列の長さ。
            @Desc: min,maxとの両立は不可能。
          min:
            @Summ: 文字列の長さの最小値。
            @Desc: lengthとの両立は不可能。
          max:
            @Summ: 文字列の長さの最大値。
            @Desc: lengthとの両立は不可能。
        """
        if(type(anoyValue)==str):
            if(anoyValue is not None):
                if(len(anoyValue)==length):
                    return
            else:
                if(min is not None):
                    if(len(anoyValue)<min):
                        raise AnnotationYamlTypeError(self._curFile,"!Str",path)
                if(max is not None):
                    if(max<len(anoyValue)):
                        raise AnnotationYamlTypeError(self._curFile,"!Str",path)
                return
        else:
            raise AnnotationYamlTypeError(self._curFile,"!Str",path)

    def checkBool(self,anoyValue,path:list):
        """
        @Summ: !Bool型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          path:
            @Summ: 現在探索している場所。
            @Type: List
        """
        if(type(anoyValue)!=bool):
            raise AnnotationYamlTypeError(self._curFile,"!Bool",path)

    def checkInt(self,anoyValue,path:list,min=None,max=None):
        """
        @Summ: !Int型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          path:
            @Summ: 現在探索している場所。
            @Type: List
          min:
            @Summ: 最小値。
          max:
            @Summ: 最大値。
        """
        if(type(anoyValue)==int):
            if(min is not None):
                if(anoyValue<min):
                    raise AnnotationYamlTypeError(self._curFile,"!Int",path)
            if(max is not None):
                if(max<anoyValue):
                    raise AnnotationYamlTypeError(self._curFile,"!Int",path)
            return
        else:
            raise AnnotationYamlTypeError(self._curFile,"!Int",path)

    def checkFloat(self,anoyValue,path:list,min=None,max=None):
        """
        @Summ: !Float型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          path:
            @Summ: 現在探索している場所。
            @Type: List
          min:
            @Summ: 最小値。
          max:
            @Summ: 最大値。
        """
        if(type(anoyValue)==float):
            if(min is not None):
                if(anoyValue<min):
                    raise AnnotationYamlTypeError(self._curFile,"!Float",path)
            if(max is not None):
                if(max<anoyValue):
                    raise AnnotationYamlTypeError(self._curFile,"!Float",path)
            return
        else:
            raise AnnotationYamlTypeError(self._curFile,"!Float",path)

    def checkFreeMap(self,anoyValue,path:list):
        """
        @Summ: !FreeMap型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          path:
            @Summ: 現在探索している場所。
            @Type: List
        """
        if(type(anoyValue)==dict):
            for key,value in anoyValue.items():
                newPath=path+[key]
                self._visitQueue.append((key,value))
                self._pathQueue.append(newPath)
                if(key[0]=="@"):
                    raise AnnotationYamlTypeError(self._curFile,"!FreeMap",path)
        else:
            raise AnnotationYamlTypeError(self._curFile,"!FreeMap",path)

    def checkAnnoMap(self,anoyValue,path:list,annoKeyList:list=[]):
        """
        @Summ: !FreeMap型を型確認する関数。

        @Desc:
        - <annoKeyList>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<annoKeyList>以外のannotation keyも許容される。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          path:
            @Summ: 現在探索している場所。
            @Type: List
          annoKeyList:
            @Summ: annotation keyのlist。
            @Type: List
            @Default: []
        """
        if(type(anoyValue)==dict):
            for key,value in anoyValue.items():
                newPath=path+[key]
                self._visitQueue.append((key,value))
                self._pathQueue.append(newPath)
                if(key[0]!="@"):
                    raise AnnotationYamlTypeError(self._curFile,"!AnnoMap",path)
                if(annoKeyList!=[]):
                    if(key not in annoKeyList):
                        raise AnnotationYamlTypeError(self._curFile,"!AnnoMap",path)
        else:
            raise AnnotationYamlTypeError(self._curFile,"!AnnoMap",path)

    def checkList(self,anoyValue,path:list,elementType:str=None,length:int=None):
        """
        @Summ: !List型を型確認する関数。

        @Desc:
        - <typeOption>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<typeOption>以外のannotation keyも許容される。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          path:
            @Summ: 現在探索している場所。
            @Type: List
          elementType:
            @Summ: list型の子要素のdata型。
            @Desc:
            - [!Bool,!Str,!Int,!Float]を指定できる。
            - Noneの時はdata型を確認しない。
            @Type: Str
          length:
            @Summ: listの長さ
            @Type: Int
        """
        if(type(anoyValue)==list):
            if(length is not None):
                if(length!=len(list)):
                    raise AnnotationYamlTypeError(self._curFile,"!List",path) 
            for i in len(anoyValue):
                element=anoyValue[i]
                newPath=path+[i]
                if(elementType is not None):
                    match elementType:
                        case "!Str":
                            if(type(element)!=str):
                                raise AnnotationYamlTypeError(self._curFile,"!List",newPath)
                        case "!Bool":
                            if(type(element)!=bool):
                                raise AnnotationYamlTypeError(self._curFile,"!List",newPath)
                        case "!Int":
                            if(type(element)!=int):
                                raise AnnotationYamlTypeError(self._curFile,"!List",newPath)
                        case "!Float":
                            if(type(element)!=float):
                                raise AnnotationYamlTypeError(self._curFile,"!List",newPath)
                        case _:
                            raise ConfigurationYamlError(f"{elementType} is invalid definition.")
                self._visitQueue.append((i,element))
                self._pathQueue.append(newPath)
        else:
            raise AnnotationYamlTypeError(self._curFile,"!List",path)
    
    def checkEnum(self,anoyValue,path:list,optionList:list):
        """
        @Summ: !Enum型を型確認する関数。

        @Desc:
        - 他の言語のUnion型の役割も兼ねている。
        - nestしないdata型[!Bool,!Str,!Int,!Float,null]は選択肢にできる。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          path:
            @Summ: 現在探索している場所。
            @Type: List
          optionList:
            @Summ: Enum型の選択肢を格納するlist型。
            @Type: List
        """
        for i in range(len(optionList)):
            option=optionList[i]
            if(option is None):
                if(anoyValue is None):
                    return
                else:
                    raise AnnotationYamlTypeError(self._curFile,"!Enum",path)
            match option:
                case "!Str":
                    if(type(anoyValue)==str):
                        return
                    else:
                        raise AnnotationYamlTypeError(self._curFile,"!Enum",path)
                case "!Bool":
                    if(type(anoyValue)==bool):
                        return
                    else:
                        raise AnnotationYamlTypeError(self._curFile,"!Enum",path)
                case "!Int":
                    if(type(anoyValue)==int):
                        return
                    else:
                        raise AnnotationYamlTypeError(self._curFile,"!Enum",path)
                case "!Float":
                    if(type(anoyValue)==float):
                        return
                    else:
                        raise AnnotationYamlTypeError(self._curFile,"!Enum",path)
                case _:
                    if(anoyValue==option):
                        return
        raise AnnotationYamlTypeError(self._curFile,"!Enum",path)


if(__name__=="__main__"):
    configPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\config01.yaml"
    anoyPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\int_false.yaml"
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    with open(anoyPath,mode="r",encoding="utf-8") as f:
        anoyDict=yaml.safe_load(f)
    tree01=DictTraversal(configDict)
    tree01.dictBFS(anoyDict)

