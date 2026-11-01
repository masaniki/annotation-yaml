import yaml
from pathlib import Path
import logging

from .confParser import ConfParser
from .errors import AnoyError

class AnoyParser():
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
        _anoyPath:
            @Summ: 現在探索中のANOY file名。
            @Type: Str
        _logger:
            @Summ: 使うlogger.
            @Type: Logger
        _exceptionMode:
            @Summ: 例外を出す時にtrue.
            @Type: Bool
    """

    def __init__(self,configDict:dict,exceptionMode:bool):
        """
        @Summ: constructor.
        """
        self._configDict=ConfParser.checkConf(configDict)
        # print(self._configDict)
        self._anoyPath=""
        self._logger=logging.getLogger(__name__)
        self._exceptionMode=exceptionMode

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
                self._logger.info(f"open: {anoyPath}")
                self._anoyPath=anoyPath
                self.anoyFreeSearch([],anoyDict)
        else:
            for childPath in anoyPath.iterdir():
                self.dirDFS(childPath)

    def logAnoyKeyError(self,yamlPath:list):
        """
        @Summ: keyError用のmessaegをloggingする関数。

        @Args:
            yamlPath:
                @Type: Str
        """
        msg=f"  keyError at:\n    {yamlPath}"
        if(self._exceptionMode):
            raise AnoyError(self._anoyPath,msg)
        else:
            self._logger.error(msg)


    def logAnoyTypeError(self,yamlPath:list,annoType:str):
        """
        @Summ: anoyTypeErrorの時のmessageをloggingする関数。

        @Args:
            yamlPath:
                @Type: Str
            annoType:
                @Summ: 例外の原因となったdata型名。
                @Type: Str
        """
        msg=f"  {annoType} contradiction at:\n    {yamlPath}"
        if(self._exceptionMode):
            raise AnoyError(self._anoyPath,msg)
        else:
            self._logger.error(msg)


    def anoyFreeSearch(self,anoyPath,anoyValue):
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
        @Returns:
            @Summ: 型が正常ならばTrue
            @Type: Bool
        """
        if(type(anoyValue)==list):
            isValid=self.checkAnoyList(anoyPath,anoyValue,{},force=True)
            return isValid
        elif(type(anoyValue)==dict):
            keyList=list(anoyValue.keys())
            if(keyList==[]):
                return True
            firstKey=keyList[0]
            if(type(firstKey)!=str):
                isValid=self.checkAnoyFreeMap(anoyPath,anoyValue)
            elif(firstKey[0]=="@"):
                isValid=self.checkAnoyAnnoMap(anoyPath,anoyValue,[],force=True)
            else:
                isValid=self.checkAnoyFreeMap(anoyPath,anoyValue)
            return isValid
        else:
            return True

    def checkAnoyType(self,anoyPath,data,confType,force):
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
            force:
                @Summ: 強制的にmessageを出す時にTrue.
                @Type: Bool
        @Returns:
            @Summ: 正しいdata型の時True。
            @Type: Bool
        """
        if(confType is None):
            isValid=self.anoyFreeSearch(anoyPath,data)
            return isValid
        typeStr=list(confType.keys())[0]
        typeOption=confType[typeStr]
        match typeStr:
            case "!Str":
                isValid=self.checkAnoyStr(anoyPath,data,typeOption)
            case "!Bool":
                isValid=self.checkAnoyBool(anoyPath,data)
            case "!Int":
                isValid=self.checkAnoyInt(anoyPath,data,typeOption)
            case "!Float":
                isValid=self.checkAnoyFloat(anoyPath,data,typeOption)
            case "!FreeMap":
                isValid=self.checkAnoyFreeMap(anoyPath,data)
            case "!AnnoMap":
                isValid=self.checkAnoyAnnoMap(anoyPath,data,typeOption,force)
            case "!List":
                isValid=self.checkAnoyList(anoyPath,data,typeOption,force)
            case "!Enum":
                isValid=self.checkAnoyEnum(anoyPath,data,typeOption)
            case _:
                self.logAnoyTypeError(anoyPath,"!Type")
        return isValid

    def checkAnoyStr(self,anoyPath,anoyValue,typeOption):
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
            force:
                @Summ: 強制的にmessageを出す時にTrue.
                @Type: Bool
        @Returns:
          @Summ: 型が正常である時にTrue.
          @Type: Bool
        """
        minLen=typeOption.get("min")
        maxLen=typeOption.get("max")
        isValid=True
        if(type(anoyValue)==str):
            if(minLen is not None):
                if(len(anoyValue)<minLen):
                    isValid=False
            if(maxLen is not None):
                if(maxLen<len(anoyValue)):
                    isValid=False
        else:
            isValid=False
        # error出すかの判断。
        if(isValid):
            return True
        else:
            self.logAnoyTypeError(anoyPath,"!Str")
            return False

    def checkAnoyBool(self,anoyPath,anoyValue):
        """
        @Summ: ANOY上で!Bool型を型確認する関数。

        @Args:
            anoyPath:
                @Summ: anoy内の現在地。
                @Type: List
            anoyValue:
                @Summ: 型確認する値。
        @Returns:
          @Summ: 正常な値ならばTrue.
          @Type: Bool
        """
        if(type(anoyValue)==bool):
            return True
        else:
            self.logAnoyTypeError(anoyPath,"!Bool")
            return False

    def checkAnoyInt(self,anoyPath,anoyValue,typeOption):
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
            typeOption:
                @Summ: int型のoption。
                @Type: Dict
        @Returns:
          @Type: Bool
        """
        minInt=typeOption.get("min")
        maxInt=typeOption.get("max")
        isValid=True
        if(type(anoyValue)==int):
            if(minInt is not None):
                if(anoyValue<minInt):
                    isValid=False
            if(maxInt is not None):
                if(maxInt<anoyValue):
                    isValid=False
        else:
            isValid=False
        # error出すかの判断。
        if(isValid):
            return True
        else:
            self.logAnoyTypeError(anoyPath,"!Int")
            return False


    def checkAnoyFloat(self,anoyPath,anoyValue,typeOption):
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
            typeOption:
                @Summ: float型のoption。
                @Type: Dict
        @Returns:
          @Type: Bool
        """
        minFloat=typeOption.get("min")
        maxFloat=typeOption.get("max")
        isValid=True
        if(type(anoyValue)==int or type(anoyValue)==float):
            if(minFloat is not None):
                if(anoyValue<minFloat):
                    isValid=False
            if(maxFloat is not None):
                if(maxFloat<anoyValue):
                    isValid=False
        else:
            isValid=False
        # error出すかの判断。
        if(isValid):
            return True
        else:
            self.logAnoyTypeError(anoyPath,"!Float")
            return False


    def checkAnoyFreeMap(self,anoyPath,anoyValue):
        """
        @Summ: ANOY上で!FreeMap型を型確認する関数。

        @Warning: まだ入れ子の機能を実装していない。浅い探索のみで終了する。

        @Args:
            anoyPath:
                @Summ: anoy内の現在地。
                @Type: List
            anoyValue:
                @Summ: 型確認する値。
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
                        self.logAnoyTypeError(anoyPath,"!FreeMap")
                        return False
                isValid=self.anoyFreeSearch(newAnoyPath,value)
                if(not isValid):
                    return False
            return True
        else:
            self.logAnoyTypeError(anoyPath,"!FreeMap")
            return False

    def checkAnoyAnnoMap(self,anoyPath,anoyValue,typeOption:list,force):
        """
        @Summ: ANOY上で!FreeMap型を型確認する関数。

        @Desc:
        - この関数が再帰の中心となる。
        - <typeOption>は最低限必要なannotation keyのlistが入る。
        - 最低限なので、<typeOption>以外のannotation keyも許容される。
        - 親のannotation keyには、1つ上のkeyまたは、2つ上のkeyが代入される。
        - 1つ上のkeyの接頭辞が`@`でない時に、2つ上のkeyが代入される。

        @Args:
            anoyPath:
                @Summ: anoy内の現在地。
                @Type: List
            anoyValue:
                @Summ: 型確認する値。
            typeOption:
                @Summ: 子要素になれるannotation keyのlist。
                @Desc:
                - 空lsitの時は任意のannotation keyを受け入れる。
                - これは全てのannotation keyが入ったlist型と同じ挙動をする。
                @Type: List
                @Default: []
            force:
                @Summ: 強制的にmessageを出す時にTrue.
                @Type: Bool
        @Returns:
            @Summ: 正常な値ならばTrue.
            @Type: Bool
        """
        if(type(anoyValue)==dict):
            for key,value in anoyValue.items():
                newAnoyPath=anoyPath+[key]
                # annotation keyの確認。
                confAnnoKey=self._configDict.get(key)
                if(confAnnoKey is None):
                    self.logAnoyKeyError(newAnoyPath)
                    return False
                # AnnoMap型のtypeOptionの確認。
                if(typeOption!=[]):
                    if(key not in typeOption):
                        self.logAnoyTypeError(anoyPath,"!AnnoMap")
                        return False
                # !Parentの確認。
                parentList=confAnnoKey.get("!Parent")
                if(parentList is None):
                    pass
                else:
                    # parent annotation keyの確定。
                    match len(anoyPath):
                        case 0:
                            parentAnnoKey=None
                        case 1:
                            parentAnnoKey=anoyPath[-1]
                        case _:
                            lastAnnoKey=anoyPath[-1]
                            if(type(lastAnnoKey)!=str):
                                parentAnnoKey=anoyPath[-2]
                            elif(lastAnnoKey[0]=="@"):
                                parentAnnoKey=lastAnnoKey
                            else:
                                parentAnnoKey=anoyPath[-2]
                    # parent annotation keyの検索。
                    if(parentAnnoKey not in parentList):
                        self.logAnoyTypeError(newAnoyPath,"!Parent")
                        return False
                # 子要素を探索。
                confChild=confAnnoKey.get("!Child")
                isValid=self.checkAnoyType(newAnoyPath,value,confChild,force)
                if(not isValid):
                    return False
            return True
        else:
            self.logAnoyTypeError(anoyPath,"!AnnoMap")
            return False

    def checkAnoyList(self,anoyPath,anoyValue,typeOption,force):
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
            typeOption:
                @Summ: list型のoption。
                @Desc:
                - type keyとlength keyがある。
                @Type: Dict
            force:
                @Summ: 強制的にmessageを出す時にTrue.
                @Type: Bool
        """
        eleType=typeOption.get("type")
        length=typeOption.get("length")
        if(type(anoyValue)==list):
            if(length is not None):
                if(length!=len(anoyValue)):
                    self.logAnoyTypeError(anoyPath,"!List")
                    return False
            for i in range(len(anoyValue)):
                anoyEle=anoyValue[i]
                newAnoyPath=anoyPath+[i]
                isValid=self.checkAnoyType(newAnoyPath,anoyEle,eleType,force)
                if(not isValid):
                    return False
            return True
        else:
            self.logAnoyTypeError(anoyPath,"!List")
            return False

    def checkAnoyEnum(self,anoyPath,anoyValue,typeOption:list):
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
            typeOption:
                @Summ: Enum型の選択肢を格納するlist型。
                @Desc: optionListには!Typeのlistが入る。
                @Type: List
        @Returns:
            @Summ: 正常な値ならばTrue.
            @Type: Bool
        """
        for i in range(len(typeOption)):
            option=typeOption[i]
            newAnoyPath=anoyPath+[i]
            # !Type型の選択肢。
            if(type(option)==dict):
                isValid=self.checkAnoyType(newAnoyPath,anoyValue,option,force=False)
                if(isValid):
                    return True
            # literalの選択肢。
            elif(anoyValue==option):
                return True
        self.logAnoyTypeError(anoyPath,"!Enum")
        return False



