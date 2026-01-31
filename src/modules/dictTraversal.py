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
        self._configDict=self.checkConfig(configDict)
        print(self._configDict)
        self._visitQueue=[]
        self._pathQueue=[]
        self._curFile=""
        self._curPath=[]
    
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
        newConfigDict={}  # 整形されたconfigDict
        for annoKey in configDict.keys():
            newAnnoValue={}  #annotation keyに対応する値。
            if(annoKey[0]!="@"):
                raise ConfigYamlError(f"{annoKey} is invalid definition.")
            valueDict=configDict[annoKey]
            if(type(valueDict)!=dict):
                raise ConfigYamlError(f"{annoKey} is invalid definition.")
            for key,value in valueDict.items():
                if(key[0]=="@"):
                    continue
                elif(key=="!Parent"):
                    validConfParent=self.checkParent(annoKey,value)
                    newAnnoValue["!Parent"]=validConfParent
                elif(key=="!Child"):
                    validConfChild=self.checkChild(annoKey,value)
                    newAnnoValue["!Child"]=validConfChild
                else:
                    raise ConfigYamlError(f"{annoKey} is invalid definition.")
            # isVisit keyの追加。
            newAnnoValue["isVisit"]=False
            newConfigDict[annoKey]=newAnnoValue
        return newConfigDict
    
    @classmethod
    def checkParent(cls,annoKey,confParent):
        """
        @Summ: `!Parent`に対応する値を型確認する関数。

        @Args:
          annoKey:
            @Summ: `!Parent`の親となるannotation key.
            @Type: Str
          confParent:
            @Summ: `!Parent`の子。
            @Type: Any
        @Returns:
          @Summ: `!Parent`のvalueとして有効な値。
          @Type: List
        """
        if(type(confParent)!=list):
            raise ConfigYamlError(f"{annoKey} is invalid definition.")
        for item in confParent:
            if(item is None):
                continue
            if(item[0]!="@"):
                raise ConfigYamlError(f"{annoKey} is invalid definition.")
        return confParent.copy()
    
    @classmethod
    def checkChild(cls,annoKey,confChild):
        """
        @Summ: `!Child`に対応する値を型確認する関数。

        @Args:
          annoKey:
            @Summ: `!Child`の親となるannotation key.
            @Type: Str
          confChild:
            @Summ: `!Child`の子。
            @Type: Any
        @Returns:
          @Summ: `!Child`のvalueとして有効な値。
          @Type: Dict
        """
        if(type(confChild)==str):
            match confChild:
                case "!Str":
                    return {"!Str":{"length":None,"min":None,"max":None}}
                case "!Bool":
                    return {"!Bool":{}}
                case "!Int":
                    return {"!Int":{"min":None,"max":None}}
                case "!Float":
                    return {"!Float":{"min":None,"max":None}}
                case "!List":
                    return {"!List":{"type":None,"length":None}}
                case "!FreeMap":
                    return {"!FreeMap":{}}
                case "!AnnoMap":
                    return {"!AnnoMap":[]}
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
                    return {"!Str":{"length":strLength,"min":strMin,"max":strMax}}
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
                    return {"!Int":{"min":intMin,"max":intMax}}
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
                    return {"!Float":{"min":floatMin,"max":floatMax}}
                case "!Enum":
                    if(type(typeOption)!=list):
                        raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                    enumOption=[]
                    for item in typeOption:
                        if(type(item)==list):
                            raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                        elif(type(item)==dict):
                            keyList=list(item.keys())
                            if(len(keyList)!=1):
                                raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                            enumOption.append(keyList[0])
                        else:
                            enumOption.append(item)
                    return {"!Enum":enumOption}
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
                    return {"!List":{"type":listType,"length":listLength}}
                case "!AnnoDict":
                    if(type(typeOption)!=list):
                        raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                    for i in len(typeOption):
                        item=typeOption[i]
                        if(item[0]!="@"):
                            raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
                    return {"!AnnoDict":typeOption}
                case _:
                    raise ConfigYamlError(f"`{annoKey}` has invalid definition.")
        else:
            raise ConfigYamlError(f"{annoKey} is invalid definition.")


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
                raise AnnotationKeyError(self._curFile, self._curPath,parentKey)
            confChild=confDictVal.get("!Child")
        else:
            confChild=None
        # anoyの型確認
        if(confChild is None): #Noneの処理方法は不明。
            # nestになるlistとdictだけ対処する。
            if(type(childValue)==list):
                for i in range(len(childValue)):
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
        typeOption=confChild[typeStr]
        match typeStr:
            case "!Str":
                self.checkStr(childValue,**typeOption)
            case "!Bool":
                self.checkBool(childValue)
            case "!Int":
                self.checkInt(childValue,**typeOption)
            case "!Float":
                self.checkFloat(childValue,**typeOption)
            case "!FreeMap":
                self.checkFreeMap(childValue)
            case "!AnnoMap":
                self.checkAnnoMap(parentKey,childValue,typeOption)
            case "!List":
                self.checkList(parentKey,childValue,elementType=typeOption["type"],length=typeOption["length"])
            case "!Enum":
                self.checkEnum(childValue,typeOption)
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
                    raise AnnotationTypeError(self._curFile,self._curPath,"!Str",)
            else:
                if(min is not None):
                    if(len(anoyValue)<min):
                        raise AnnotationTypeError(self._curFile,self._curPath,"!Str")
                if(max is not None):
                    if(max<len(anoyValue)):
                        raise AnnotationTypeError(self._curFile,self._curPath,"!Str")
                return
        else:
            raise AnnotationTypeError(self._curFile,self._curPath,"!Str")

    def checkBool(self,anoyValue):
        """
        @Summ: !Bool型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
        """
        if(type(anoyValue)!=bool):
            raise AnnotationTypeError(self._curFile,self._curPath,"!Bool")

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
                    raise AnnotationTypeError(self._curFile,self._curPath,"!Int")
            if(max is not None):
                if(max<anoyValue):
                    raise AnnotationTypeError(self._curFile,self._curPath,"!Int")
            return
        else:
            raise AnnotationTypeError(self._curFile,self._curPath,"!Int")

    def checkFloat(self,anoyValue,min=None,max=None):
        """
        @Summ: !Float型を型確認する関数。

        @Args:
          anoyValue:
            @Summ: 型確認する値。
          min:
            @Summ: 最小値。
            @Desc: anoyValue=minの時もtrue.
          max:
            @Summ: 最大値。
            @Desc: anoyValue=maxの時もtrue.
        """
        print(anoyValue,min,max)
        if(type(anoyValue)==float):
            if(min is not None):
                if(anoyValue<min):
                    raise AnnotationTypeError(self._curFile,self._curPath,"!Float")
            if(max is not None):
                if(max<anoyValue):
                    raise AnnotationTypeError(self._curFile,self._curPath,"!Float")
            return
        else:
            raise AnnotationTypeError(self._curFile,self._curPath,"!Float")

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
                    raise AnnotationTypeError(self._curFile,newPath,"!FreeMap")
        else:
            raise AnnotationTypeError(self._curFile,self._curPath,"!FreeMap")

    def checkAnnoMap(self,parentKey,anoyValue,annoKeyList:list=[]):
        """
        @Summ: !FreeMap型を型確認する関数。

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
            @Summ: annotation keyのlist。
            @Type: List
            @Default: []
        """
        if(type(anoyValue)==dict):
            for key,value in anoyValue.items():
                newPath=self._curPath+[key]
                self._visitQueue.append((key,value))
                self._pathQueue.append(newPath)
                # !Parentの確認。
                configValue=self._configDict.get(key)
                if(configValue is None):
                    raise AnnotationKeyError(self._curFile,self._curPath,parentKey)
                confParent=configValue.get("!Parent")
                if(confParent is not None):
                    if(parentKey not in confParent):
                        raise AnnotationTypeError(self._curFile,newPath,"!Parent")
                if(annoKeyList!=[]):
                    if(key not in annoKeyList):
                        raise AnnotationTypeError(self._curFile,self._curPath,"!AnnoMap")
        else:
            raise AnnotationTypeError(self._curFile,self._curPath,"!AnnoMap")

    def checkList(self,parentKey,anoyValue,elementType:str=None,length:int=None):
        """
        @Summ: !List型を型確認する関数。

        @Desc:
        - <typeOption>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<typeOption>以外のannotation keyも許容される。

        @Args:
          parentKey:
            @Summ: 親のkey。
            @Type: Str
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
                    raise AnnotationTypeError(self._curFile,self._curPath,"!List")
            for i in range(len(anoyValue)):
                element=anoyValue[i]
                newPath=self._curPath+[i]
                if(elementType is not None):
                    match elementType:
                        case "!Str":
                            if(type(element)!=str):
                                raise AnnotationTypeError(self._curFile,newPath,"!List")
                        case "!Bool":
                            if(type(element)!=bool):
                                raise AnnotationTypeError(self._curFile,newPath,"!List")
                        case "!Int":
                            if(type(element)!=int):
                                raise AnnotationTypeError(self._curFile,newPath,"!List")
                        case "!Float":
                            if(type(element)!=float):
                                raise AnnotationTypeError(self._curFile,newPath,"!List")
                        case _:
                            raise ConfigYamlError(f"{parentKey} is invalid definition.")
                self._visitQueue.append((i,element))
                self._pathQueue.append(newPath)
        else:
            raise AnnotationTypeError(self._curFile,self._curPath,"!List")
    
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
                    if(anoyValue==option):
                        return
        raise AnnotationTypeError(self._curFile,self._curPath,"!Enum")


if(__name__=="__main__"):
    configPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\config01.yaml"
    anoyPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\int_false.yaml"
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    with open(anoyPath,mode="r",encoding="utf-8") as f:
        anoyDict=yaml.safe_load(f)
    tree01=DictTraversal(configDict)
    tree01.dictBFS(anoyDict)

