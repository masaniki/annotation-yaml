import pytest
from pathlib import Path
import sys
import yaml

#sys.pathを弄る。
projectDir=Path(__file__).parent.parent.parent
sys.path.append(str(projectDir))

from src.anoy import AnoyParser
from src.anoy import AnnotationKeyError, AnnotationTypeError, ConfigYamlError

testDir=Path(__file__).parent

@pytest.mark.parametrize(
        "x,y",[
        ("case01/config01.yaml", "case01/valid_anoy.yaml"),
        ("valid_parent01/config.yaml", "valid_parent01/anoy.yaml"),
        ("valid_parent02/config.yaml", "valid_parent02/anoy.yaml"),
        ("valid_str01/config.yaml", "valid_str01/anoy.yaml"),
        ("valid_int01/config.yaml", "valid_int01/anoy.yaml"),
        ("valid_float01/config.yaml", "valid_float01/anoy.yaml"),
        ("valid_list01/config.yaml", "valid_list01/anoy.yaml"),
        ("valid_childNull01/config.yaml", "valid_childNull01/anoy.yaml"),
        ("valid_freeMap01/config.yaml", "valid_freeMap01/anoy.yaml"),
        ("valid_annoMap01/config.yaml", "valid_annoMap01/anoy.yaml"),
        ("valid_enum01/config.yaml", "valid_enum01/anoy.yaml"),
        ("valid_enum02/config.yaml", "valid_enum02/anoy.yaml"),
        ("valid_enum03/config.yaml", "valid_enum03/anoy.yaml"),
        ("valid_enum04/config.yaml", "valid_enum04/anoy.yaml"),
        ("sampleCase/library_config.yaml", "sampleCase/valid_library.yaml"),
        ]
)
def test_valid_anoyFile(x,y):
    """
    @Summ: anoy引数にanoy fileを代入する場合。

    @Desc: 完走したらtest合格。

    @Args:
      x:
        @Summ: config yamlのpath。
        @Desc: test directoryからtest caseへの相対path。
        @Type: Str
      y:
        @Summ: 
        @Desc: test directoryからtest caseへの相対path。
        @Type: Str
    """
    configPath=testDir/x
    anoyPath=testDir/y
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    tree01=AnoyParser(configDict)
    tree01.dirDFS(anoyPath)
    assert True

def test_valid_anoy01():
    """
    @Summ: configが正常∧anoyが正常な場合をtestする。
    """
    suitePath=testDir/"valid_anoy"/"testsuite"
    for childPath in suitePath.iterdir():
        anoyPath=childPath/"anoy.yaml"
        configPath=childPath/"config.yaml"
        with open(configPath,mode="r",encoding="utf-8") as f:
            configDict=yaml.safe_load(f)
        tree01=AnoyParser(configDict)
        tree01.dirDFS(anoyPath)
        assert True

def test_invalid_anoy01(outName:str="out.yaml",expName:str="exp.yaml",isTest=True):
    """
    @Summ: configが正常∧anoyが異常な場合をtestする。

    @Args:
      outName:
        @Summ: 結果を出力するfile名。
        @Type: Str
        @Default: out
      expName:
        @Summ: 期待値のfile名。
        @Type: Str
        @Default: exp
      isTest:
        @Summ: testの時にTrue.
        @Default: true
        @Type: Bool
    """
    suitePath=testDir/"invalid_anoy"/"testsuite"/"in"
    outDict={}
    for childPath in suitePath.iterdir():
        caseName=childPath.name
        anoyPath=childPath/"anoy.yaml"
        configPath=childPath/"config.yaml"
        with open(configPath,mode="r",encoding="utf-8") as f:
            configDict=yaml.safe_load(f)
        try:
            tree01=AnoyParser(configDict)
            tree01.dirDFS(anoyPath)
        except BaseException as e:
            errorDict={}
            if(type(e)==AnnotationKeyError):
                errorType="AnnotationKeyError"
                errorDict["errorType"]=errorType
                errorDict["filePath"]=str(e.fileName)
                errorDict["yamlPath"]=e.yamlPath
                errorDict["msg"]=e.msg
            elif(type(e)==AnnotationTypeError):
                errorType="AnnotationTypeError"
                errorDict["errorType"]=errorType
                errorDict["filePath"]=str(e.fileName)
                errorDict["yamlPath"]=e.yamlPath
                errorDict["msg"]=e.msg
            elif(type(e)==ConfigYamlError):
                errorType="ConfigYamlError"
                errorDict["errorType"]=errorType
                errorDict["configPath"]=e.configPath
                errorDict["msg"]=e.msg
            else:
                raise TypeError("unknown type is found.")
            outDict[caseName]=errorDict
    outputPath=testDir/"invalid_anoy"/"testsuite"/outName
    with open(outputPath,mode="w",encoding="utf-8") as f:
        yaml.safe_dump(outDict,f)
    if(isTest):
      expectedPath=testDir/"invalid_anoy"/"testsuite"/expName
      with open(expectedPath,mode="r",encoding="utf-8") as f:
          expDict=yaml.safe_load(f)
      assert outDict==expDict


def test_invalid_config01():
    """
    @Summ: configが異常∧anoyが正常な場合をtestする。
    """
    assert True

@pytest.mark.parametrize(
        "x,y,z",[
        ("case02/config01.yaml", "case02/invalid_int.yaml", AnnotationTypeError),
        ("typo01/config.yaml", "typo01/anoy.yaml", AnnotationKeyError),
        ("invalid_parent01/config.yaml", "invalid_parent01/anoy.yaml", AnnotationTypeError),
        ("invalid_parent02/config.yaml", "invalid_parent02/anoy.yaml", AnnotationTypeError),
        ("invalid_str01/config.yaml", "invalid_str01/anoy.yaml", AnnotationTypeError),
        ("invalid_str02/config.yaml", "invalid_str02/anoy.yaml", AnnotationTypeError),
        ("invalid_int01/config.yaml", "invalid_int01/anoy.yaml", AnnotationTypeError),
        ("invalid_float01/config.yaml", "invalid_float01/anoy.yaml", AnnotationTypeError),
        ("invalid_float02/config.yaml", "invalid_float02/anoy.yaml", AnnotationTypeError),
        ("invalid_list01/config.yaml", "invalid_list01/anoy.yaml", AnnotationTypeError),
        ("invalid_list02/config.yaml", "invalid_list02/anoy.yaml", AnnotationTypeError),
        ("invalid_freeMap01/config.yaml", "invalid_freeMap01/anoy.yaml", AnnotationTypeError),
        ("invalid_annoMap01/config.yaml", "invalid_annoMap01/anoy.yaml", AnnotationKeyError),
        ("invalid_annoMap02/config.yaml", "invalid_annoMap02/anoy.yaml", AnnotationTypeError),
        ("invalid_childNull01/config.yaml", "invalid_childNull01/anoy.yaml", AnnotationTypeError),
        ("invalid_enum01/config.yaml", "invalid_enum01/anoy.yaml", AnnotationTypeError),
        ("invalid_enum02/config.yaml", "invalid_enum02/anoy.yaml", AnnotationTypeError),
        ("invalid_enum03/config.yaml", "invalid_enum03/anoy.yaml", ConfigYamlError),
        ("sampleCase/library_config.yaml", "sampleCase/invalid_library.yaml", AnnotationKeyError)
        ]
)
def test_invalid_anoyFile(x,y,z):
    """
    @Summ: anoy引数にanoy fileを代入する場合。

    @Args:
      x:
        @Summ: config yamlのpath。
        @Desc: test directoryからtest caseへの相対path。
        @Type: Str
      y:
        @Summ: anoyのpath。
        @Desc: test directoryからtest caseへの相対path。
        @Type: Str
      z:
        @Summ: Error名。
        @Type: Exception
    """
    configPath=testDir/x
    anoyPath=testDir/y
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    with pytest.raises(z) as e:
        tree01=AnoyParser(configDict)
        tree01.dirDFS(anoyPath)
    assert e.type==z

@pytest.mark.parametrize(
        "x,y",[
        # ("case04/config.yaml", "case04/anoy"),
        ]
)
def test_valid_anoyDir(x,y):
    """
    @Summ: anoy引数にanoy directoryを代入する場合。

    @Desc: 完走したらtest合格。

    @Args:
      x:
        @Summ: config yamlのpath。
        @Desc: test directoryからtest caseへの相対path。
        @Type: Str
      y:
        @Summ: 
        @Desc: test directoryからtest caseへの相対path。
        @Type: Str
    """
    configPath=testDir/x
    anoyPath=testDir/y
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    tree01=AnoyParser(configDict)
    tree01.dirDFS(anoyPath)
    assert True

@pytest.mark.parametrize(
        "x,y,z",[
        # ("case05/config.yaml", "case05/anoy", AnnotationTypeError),
        ]
)
def test_invalid_anoyDir(x,y,z):
    """
    @Summ: anoy引数にanoy directoryを代入する場合。

    @Args:
      x:
        @Summ: config yamlのpath。
        @Desc: test directoryからtest caseへの相対path。
        @Type: Str
      y:
        @Summ: anoyのpath。
        @Desc: test directoryからtest caseへの相対path。
        @Type: Str
      z:
        @Summ: Error名。
        @Type: Exception
    """
    configPath=testDir/x
    anoyPath=testDir/y
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    with pytest.raises(z) as e:
        tree01=AnoyParser(configDict)
        tree01.dirDFS(anoyPath)
    assert e.type==z

if(__name__=="__main__"):
    test_invalid_anoy01(isTest=False)
    # testCaseDir=testDir/"invalid_anoy"/"testsuite"/"in"/"invalid_annoMap01"
    # anoyPath=testCaseDir/"anoy.yaml"
    # configPath=testCaseDir/"config.yaml"
    # with open(configPath,mode="r",encoding="utf-8") as f:
    #     configDict=yaml.safe_load(f)
    # try:
    #   tree01=AnoyParser(configDict)
    #   tree01.dirDFS(anoyPath)
    # except BaseException as e:
    #     print(type(e))
    #     print(e.fileName)
    #     print(e.yamlPath)
    #     print(e.msg)
