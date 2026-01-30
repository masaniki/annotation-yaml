import yaml
from pathlib import Path

from .anoyErrors import AnoyError,ConfigYamlError,AnoyTypeError

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
        print(self._configDict)
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
        for annoKey in configDict.keys():
            newAnnoValue={}  #annotation keyに対応する値。
            if(annoKey[0]!="@" and annoKey[0]!="!"):
                raise ConfigYamlError(f"{annoKey} is invalid definition.")
            valueDict=configDict[annoKey]
            if(type(valueDict)!=dict):
                raise ConfigYamlError(f"{annoKey} is invalid definition.")
            # `!Parent`の型確認
            confParent=valueDict.get("!Parent")
            if(confParent is not None):
                if(type(confParent)!=list):
                    raise ConfigYamlError(f"{annoKey} is invalid definition.")
                for item in confParent:
                    if(item[0]!="@"):
                        raise ConfigYamlError(f"{annoKey} is invalid definition.")
                newAnnoValue["!Parent"]=confParent.copy()
            # `!Child`の型確認
            confChild=valueDict.get("!Child")
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
                            raise ConfigYamlError(f"{annoKey} is invalid definition.")
                elif(type(confChild)==dict):
                    confChildKey=list(confChild.keys())
                    if(len(confChildKey)!=1):
                        raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                    typeStr=confChildKey[0]
                    typeOption=confChild[typeStr]
                    match typeStr:
                        case "!Str":
                            if(type(typeOption)!=dict):
                                raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                            strLength=None
                            strMin=None
                            strMax=None
                            for strKey,strVal in typeOption.items():
                                match strKey:
                                    case "length":
                                        if(strMin is None and strMax is None):
                                            strLength=strVal
                                        else:
                                            raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                                    case "min":
                                        if(strLength is None):
                                            strMin=strVal
                                        else:
                                            raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                                    case "max":
                                        if(strLength is None):
                                            strMax=strVal
                                        else:
                                            raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                                    case _:
                                        raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                            newConfChild={"!Str":{"length":strLength,"min":strMin,"max":strMax}}
                        case "!Int":
                            if(type(typeOption)!=dict):
                                raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                            intMin=None
                            intMax=None
                            for intKey,intVal in typeOption.items():
                                match intKey:
                                    case "min":
                                        intMin=intVal
                                    case "max":
                                        intMax=intVal
                                    case _:
                                        raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                            newConfChild={"!Int":{"min":intMin,"max":intMax}}
                        case "!Float":
                            if(type(typeOption)!=dict):
                                raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                            floatMin=None
                            floatMax=None
                            for floatKey,floatVal in typeOption.items():
                                match floatKey:
                                    case "min":
                                        floatMin=floatVal
                                    case "max":
                                        floatMax=floatVal
                                    case _:
                                        raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                            newConfChild={"!Float":{"min":floatMin,"max":floatMax}}
                        case "!Enum":
                            if(type(typeOption)!=list):
                                raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                            newConfChild={"!Enum":typeOption}
                        case "!List":
                            if(type(typeOption)!=dict):
                                raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                            listType=None
                            listLength=None
                            for listKey,listVal in typeOption.items():
                                match listKey:
                                    case "type":
                                        listType=listVal
                                    case "length":
                                        listLength=listVal
                                    case _:
                                        raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                            newConfChild={"!List":{"type":listType,"length":listLength}}
                        case "!AnnoDict":
                            if(type(typeOption)!=list):
                                raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                            for i in len(typeOption):
                                item=typeOption[i]
                                if(item[0]!="@"):
                                    raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                            newConfChild={"!AnnoDict":typeOption}
                        case _:
                            raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                else:
                    raise ConfigYamlError(f"{annoKey} is invalid definition.")
                newAnnoValue["!Child"]=newConfChild
                # isVisit keyの追加。
                newAnnoValue["isVisit"]=False
            # 最後にannotation keyを登録。
            newConfigDict[annoKey]=newAnnoValue
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
            self._curPath=self._pathQueue.pop(0)
            print(key,value)
            print(self._curPath)
            self.typeCheck(key,value)

    def typeCheck(self,parentKey:str|None,childValue):
        """
        "@Summ": annoDict内を探索する関数。

        "@Desc":
        - 型確認は"!Parent"と"!Child"の2つだ。
        - annotationKeyが親でない時は、"!Parent"も"!Child"も効力を発揮しないので無視。
        - ただし、annoKeyがNoneの時は、"!Parent"が効力を発揮する場合がある。
        - !Childが無い時は何もしない。
        - !Childが無い時は、childValue=nullとして考える。
        - valueがanoyDict型の時のみ、!Parentの型確認が行われる。

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
                raise AnoyError(f"{parentKey} is not found.")
            confChild=confDictVal.get("!Child")
        else:
            confChild=None
        # anoyの型確認
        if(confChild is None): #Noneの処理方法は不明。
            # nestになるlistとdictだけ対処する。
            if(type(childValue)==list):
                for i in len(childValue):
                    element=childValue[i]
                    newPath=self._curPath+[i]
                    self._visitQueue.append((i,element))
                    self._pathQueue.append(newPath)
            elif(type(childValue)==dict):
                for key,value in childValue.items():
                    newPath=self._curPath+[key]
                    self._visitQueue.append((key,value))
                    self._pathQueue.append(newPath)
            return
        typeStr=list(confChild.keys())[0]
        confChildVal=confChild[typeStr]
        match typeStr:
            case "!Str":
                self.checkStr(childValue,**confChildVal)
            case "!Bool":
                self.checkBool(childValue)
            case "!Int":
                self.checkInt(childValue,**confChildVal)
            case "!Float":
                self.checkFloat(childValue,**confChildVal)
            case "!FreeMap":
                self.checkFreeMap(childValue)
            case "!AnnoMap":
                self.checkAnnoMap(childValue,confChildVal)
            case "!List":
                self.checkList(childValue,elementType=confChildVal["type"],length=confChildVal["length"])
            case "!Enum":
                self.checkEnum(childValue,confChildVal)
            case _:
                raise ConfigYamlError(f"{parentKey} is invalid definition.")

    def checkStr(self,anoyValue,length=None,min=None,max=None):
        """
        @Summ: !Str型を型確認する関数。

        @Desc:
        - <length>と<min>、<length>と<max>の両立は不可能であるが、この関数ではその確認を行わない。
        - 呼び出し時にその確認を行うべきである。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          length:
            @Summ: 文字列の長さ。
            @Desc: min,maxとの両立は不可能。
          min:
            @Summ: 文字列の長さの最小値。
            @Desc:
            - lengthとの両立は不可能。
            - min-1からerror.
          max:
            @Summ: 文字列の長さの最大値。
            @Desc:
            - lengthとの両立は不可能。
            - max+1からerror.
        """
        if(type(anoyValue)==str):
            if(length is not None):
                if(len(anoyValue)==length):
                    return
                else:
                    raise AnoyTypeError("!Str",self._curFile,self._curPath)
            else:
                if(min is not None):
                    if(len(anoyValue)<min):
                        raise AnoyTypeError("!Str",self._curFile,self._curPath)
                if(max is not None):
                    if(max<len(anoyValue)):
                        raise AnoyTypeError("!Str",self._curFile,self._curPath)
                return
        else:
            raise AnoyTypeError("!Str",self._curFile,self._curPath)

    def checkBool(self,anoyValue):
        """
        @Summ: !Bool型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
        """
        if(type(anoyValue)!=bool):
            raise AnoyTypeError("!Bool",self._curFile,self._curPath)

    def checkInt(self,anoyValue,min=None,max=None):
        """
        @Summ: !Int型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          min:
            @Summ: 最小値。
          max:
            @Summ: 最大値。
        """
        if(type(anoyValue)==int):
            if(min is not None):
                if(anoyValue<min):
                    raise AnoyTypeError("!Int",self._curFile,self._curPath)
            if(max is not None):
                if(max<anoyValue):
                    raise AnoyTypeError("!Int",self._curFile,self._curPath)
            return
        else:
            raise AnoyTypeError("!Int",self._curFile,self._curPath)

    def checkFloat(self,anoyValue,min=None,max=None):
        """
        @Summ: !Float型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          min:
            @Summ: 最小値。
          max:
            @Summ: 最大値。
        """
        if(type(anoyValue)==float):
            if(min is not None):
                if(anoyValue<min):
                    raise AnoyTypeError("!Float",self._curFile,self._curPath)
            if(max is not None):
                if(max<anoyValue):
                    raise AnoyTypeError("!Float",self._curFile,self._curPath)
            return
        else:
            raise AnoyTypeError("!Float",self._curFile,self._curPath)

    def checkFreeMap(self,anoyValue):
        """
        @Summ: !FreeMap型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
        """
        if(type(anoyValue)==dict):
            for key,value in anoyValue.items():
                newPath=self._curPath+[key]
                self._visitQueue.append((key,value))
                self._pathQueue.append(newPath)
                if(key[0]=="@"):
                    raise AnoyTypeError("!FreeMap",self._curFile,newPath)
        else:
            raise AnoyTypeError("!FreeMap",self._curFile,self._curPath)

    def checkAnnoMap(self,anoyValue,annoKeyList:list=[]):
        """
        @Summ: !FreeMap型を型確認する関数。

        @Desc:
        - <annoKeyList>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<annoKeyList>以外のannotation keyも許容される。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          annoKeyList:
            @Summ: annotation keyのlist。
            @Type: List
            @Default: []
        """
        if(type(anoyValue)==dict):
            for key,value in anoyValue.items():
                newPath=self._curPath+[key]
                self._visitQueue.append((key,value))
                self._pathQueue.append(newPath)
                if(key[0]!="@"):
                    raise AnoyTypeError("!AnnoMap",self._curFile,self._curPath)
                if(annoKeyList!=[]):
                    if(key not in annoKeyList):
                        raise AnoyTypeError("!AnnoMap",self._curFile,self._curPath)
        else:
            raise AnoyTypeError("!AnnoMap",self._curFile,self._curPath)

    def checkList(self,anoyValue,elementType:str=None,length:int=None):
        """
        @Summ: !List型を型確認する関数。

        @Desc:
        - <typeOption>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<typeOption>以外のannotation keyも許容される。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
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
                if(length!=len(anoyValue)):
                    raise AnoyTypeError("!List",self._curFile,self._curPath) 
            for i in range(len(anoyValue)):
                element=anoyValue[i]
                newPath=self._curPath+[i]
                if(elementType is not None):
                    match elementType:
                        case "!Str":
                            if(type(element)!=str):
                                raise AnoyTypeError("!List",self._curFile,newPath)
                        case "!Bool":
                            if(type(element)!=bool):
                                raise AnoyTypeError("!List",self._curFile,newPath)
                        case "!Int":
                            if(type(element)!=int):
                                raise AnoyTypeError("!List",self._curFile,newPath)
                        case "!Float":
                            if(type(element)!=float):
                                raise AnoyTypeError("!List",self._curFile,newPath)
                        case _:
                            raise ConfigYamlError(f"{elementType} is invalid definition.")
                self._visitQueue.append((i,element))
                self._pathQueue.append(newPath)
        else:
            raise AnoyTypeError("!List",self._curFile,self._curPath)
    
    def checkEnum(self,anoyValue,optionList:list):
        """
        @Summ: !Enum型を型確認する関数。

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
                    print("else")
                    if(anoyValue==option):
                        return
        raise AnoyTypeError("!Enum",self._curFile,self._curPath)


if(__name__=="__main__"):
    configPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\config01.yaml"
    anoyPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\int_false.yaml"
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    with open(anoyPath,mode="r",encoding="utf-8") as f:
        anoyDict=yaml.safe_load(f)
    tree01=DictTraversal(configDict)
    tree01.dictBFS(anoyDict)

