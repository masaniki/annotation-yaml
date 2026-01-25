import yaml

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
    """
    def __init__(self,configDict:dict):
        """
        @Summ: constructor.
        """
        self._configDict=configDict
        self._visitQueue=[]
        self._pathQueue=[]
        self._configVisit={key:False for key in configDict.keys()}

    def startBFS(self,anoyDict:dict):
        """
        @Summ: 幅優先探索を開始する関数。

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

    def typeCheck(self,dictKey:str|None,dictValue,path:list):
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
            annoKey:
                "@Summ": annotation key
                "@Desc":
                - nullは親要素が存在しないことを表す(つまりvalueがroot要素である)。
                "@Type":
                Union:
                - Str
                - null
            annoValue:
                "@Summ": annotation keyに対応するvalue。
                "@Type": Any
            path:
                @Summ: 今まで経由したkeyのlist。
                @Type: List
        """
        if(dictKey is None):
            confChild=None    #confChild=Noneの時は型確認をしない。
        elif(dictKey[0]=="@"):
            confChild=self._configDict[dictKey].get("!ChildValue")
        else:
            confChild=None
        if(type(dictValue)==bool):
            if((confChild is None) or confChild=="Bool"):
                return True
            else:
                return False
        elif(type(dictValue)==str):
            if((confChild is None or confChild=="Str")):
                return True
            else:
                return False
        elif(type(dictValue)==int):
            if((confChild is None) or confChild=="Int"):
                return True
            else:
                return False
        elif(type(dictValue)==float):
            if((confChild is None) or confChild=="Float"):
                return True
            else:
                return False
        elif(type(dictValue)==list):
            if((confChild is None) or confChild=="List"):
                for i in range(len(dictValue)):
                    newPath=path+[i]
                    self._visitQueue.append((i,dictValue[i]))
                    self._pathQueue.append(newPath)
                return True
            else:
                return False
        elif(type(dictValue)==dict):
            if(confChild is None):
                for childKey,childVal in dictValue.items():
                    newPath=path+[childKey]
                    self._visitQueue.append((childKey,childVal))
                    self._pathQueue.append(newPath)
                return True
            elif(confChild=="FreeDict"):
                for childKey,childVal in dictValue.items():
                    newPath=path+[childKey]
                    self._visitQueue.append((childKey,childVal))
                    self._pathQueue.append(newPath)
                    if(childKey[0]=="@"):
                        return False
                return True
            elif(confChild=="AnnoDict"):
                for childKey,childVal in dictValue.items():
                    newPath=path+[childKey]
                    self._visitQueue.append((childKey,childVal))
                    self._pathQueue.append(newPath)
                    confParent=self._configDict[childKey].get("!ParentKey")
                    if(childKey[0]!="@"):
                        return False
                    if(confParent is None):
                        return True
                    elif(dictKey not in confParent):
                        return False
                return True
            else:  #Enum型の型確認。
                # config yaml側の型確認。
                if(type(confChild)!=dict):
                    return False
                confKeyList=list(confChild.keys())
                if(len(confKeyList)!=1 or confKeyList[0]!="Enum"):
                    return False
                confValueList=confChild["Enum"]
                if(type(confValueList)!=list):
                    return False
                # annotaion yaml側の型確認。
                for i in range(len(confValueList)):
                    if(dictValue==confValueList[i]):
                        return True
                    return False
                return True
        else:
            pathStr="/"+"/".join(path)
            raise TypeError(f"invalid value is found at `{path}`.")

if(__name__=="__main__"):
    configPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\sandbox\ood_v0_2_0.yaml"
    anoyPath=r"C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unit\sandbox\builtins_false.yaml"
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    with open(anoyPath,mode="r",encoding="utf-8") as f:
        anoyDict=yaml.safe_load(f)
    tree01=DictTraversal(configDict)
    tree01.startBFS(anoyDict)

