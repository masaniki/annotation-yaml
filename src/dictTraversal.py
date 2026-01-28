import yaml
from pathlib import Path

from anoyError import AnnotationYamlError,ConfigurationYamlError,AnnotationYamlTypeError

class DictTraversal():
    """
    @Summ: 辞書型の中身を探索するclass

    @InsVars:
        _configDict:
            @Summ: configuration yamlの中身。
            @Type: Dict
        _configVisit:
            @Summ: configuration yaml内のannotationKeyを使った否かを記録する変数。
            @Desc: {annotationKey(str):訪れた⇒True(bool)}
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
            @Summ: 現在探索中のANOY file.
            @ComeFrom: current ANOY.
            @Type: Str
    """
    def __init__(self,configDict:dict):
        """
        @Summ: constructor.
        """
        self._configDict=configDict
        self._visitQueue=[]
        self._pathQueue=[]
        self._configVisit={key:False for key in configDict.keys()}
        self._curAnoy=""


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
            print(anoyPath)
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
            print(key,value)
            print(pathList)
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
            confChildVal=None    #confChild=Noneの時は型確認をしない。
        elif(type(parentKey)!=str):
            confChildVal=None
        elif(parentKey[0]=="@"):
            confChild=self._configDict.get(parentKey)
            if(confChild is None):
                raise ConfigurationYamlError(f"`{parentKey}` is not defined.")
            confChildVal=confChild.get("!ChildValue")
        else:
            confChildVal=None
        if(type(confChildVal)==dict):
            #Enum型の型確認。
            # config yaml側の型確認。
            confKeyList=list(confChildVal.keys())
            if(len(confKeyList)!=1 or confKeyList[0]!="Enum"):
                raise ConfigurationYamlError(f"`{parentKey}` has invalid definition.")
            confValueList=confChildVal["Enum"]
            if(type(confValueList)!=list):
                raise ConfigurationYamlError(f"`{parentKey}` has invalid definition.")
            # annotaion yaml側の型確認。
            for i in range(len(confValueList)):
                if(childValue==confValueList[i]):
                    return
            raise AnnotationYamlTypeError(str(self._curAnoy),"Enum",path)
        elif(type(childValue)==bool):
            if((confChildVal is None) or confChildVal=="Bool"):
                return
            else:
                raise AnnotationYamlTypeError(str(self._curAnoy),"Bool",path)
        elif(type(childValue)==str):
            if((confChildVal is None or confChildVal=="Str")):
                return
            else:
                raise AnnotationYamlTypeError(str(self._curAnoy),type="Str",path=path)
        elif(type(childValue)==int):
            if((confChildVal is None) or confChildVal=="Int"):
                return
            else:
                raise AnnotationYamlTypeError(str(self._curAnoy),"Int",path)
        elif(type(childValue)==float):
            if((confChildVal is None) or confChildVal=="Float"):
                return
            else:
                raise AnnotationYamlTypeError(str(self._curAnoy),"Float",path)
        elif(type(childValue)==list):
            if((confChildVal is None) or confChildVal=="List"):
                for i in range(len(childValue)):
                    newPath=path+[i]
                    self._visitQueue.append((i,childValue[i]))
                    self._pathQueue.append(newPath)
                return
            else:
                raise AnnotationYamlTypeError(str(self._curAnoy),"List",path)
        elif(type(childValue)==dict):
            if(confChildVal is None):
                for key,childValue in childValue.items():
                    newPath=path+[key]
                    self._visitQueue.append((key,childValue))
                    self._pathQueue.append(newPath)
                return
            elif(confChildVal=="FreeDict"):
                for key,childValue in childValue.items():
                    newPath=path+[key]
                    self._visitQueue.append((key,childValue))
                    self._pathQueue.append(newPath)
                    if(key[0]=="@"):
                        raise AnnotationYamlTypeError(str(self._curAnoy),"FreeDict",path)
                return
            elif(confChildVal=="AnnoDict"):
                for key,childValue in childValue.items():
                    newPath=path+[key]
                    self._visitQueue.append((key,childValue))
                    self._pathQueue.append(newPath)
                    confParent=self._configDict[key].get("!ParentKey")
                    if(key[0]!="@"):
                        raise AnnotationYamlTypeError(str(self._curAnoy),"AnnoDict",path)
                    if(confParent is None):
                        pass
                    elif(parentKey not in confParent):
                        raise AnnotationYamlTypeError(str(self._curAnoy),"AnnoDict",path)
                return
        else:
            raise AnnotationYamlError(f" invalid value is found at:\n    {str(self._curAnoy)}: `{path}`.")

if(__name__=="__main__"):
    configPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\config01.yaml"
    anoyPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\case01\int_false.yaml"
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    with open(anoyPath,mode="r",encoding="utf-8") as f:
        anoyDict=yaml.safe_load(f)
    tree01=DictTraversal(configDict)
    tree01.dictBFS(anoyDict)

