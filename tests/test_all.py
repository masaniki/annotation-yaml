import pytest
from pathlib import Path
import sys
import yaml
import difflib

import logging
import logging.config

#sys.pathを弄る。
PROJECT_DIR=Path(__file__).parent.parent
sys.path.append(str(PROJECT_DIR))

from src.anoy import AnoyParser
from src.anoy import ConfigYamlError

TESTS_DIR=Path(__file__).parent

def test_valid_anoy():
    """
    @Summ: config yamlが正常∧anoyが正常な場合をtestする。

    @Desc:
    - testに必要なfileは全てtestsuite directoryに格納する。

    """
    # logginの環境設定。
    suitePath=TESTS_DIR/"valid_anoy"/"testsuite"
    loggingConfigPath=suitePath/"logging_config.yaml"
    with open(loggingConfigPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    logging.config.dictConfig(configDict)
    # 関数の実行。
    inputPath=suitePath/"in"
    for childPath in inputPath.iterdir():
        anoyPath=childPath/"anoy.yaml"
        configPath=childPath/"config.yaml"
        with open(configPath,mode="r",encoding="utf-8") as f:
            configDict=yaml.safe_load(f)
        tree01=AnoyParser(configDict)
        tree01.dirDFS(anoyPath)
    # log.txtの比較。
    outputLogPath=suitePath/"output_log.txt"
    expectedLogPath=suitePath/"expected_log.txt"
    with open(outputLogPath,mode="r",encoding="utf-8") as f1:
        outputTextLiens=f1.readlines()
    with open(expectedLogPath,mode="r",encoding="utf-8") as f1:
        expectedTextLines=f1.readlines()
    diffIter=difflib.unified_diff(outputTextLiens,expectedTextLines)
    diffList=list(diffIter)
    assert diffList==[]

def test_invalid_anoy02():
    """
    @Summ: configが正常∧anoyが異常な場合をtestする。

    @Desc:
    - testに必要なfileは全てtestsuite directoryに格納する。

    """
    # logginの環境設定。
    suitePath=TESTS_DIR/"invalid_anoy"/"testsuite"
    loggingConfigPath=suitePath/"logging_config.yaml"
    with open(loggingConfigPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    logging.config.dictConfig(configDict)
    inputPath=suitePath/"in"
    for childPath in inputPath.iterdir():
        anoyPath=childPath/"anoy.yaml"
        configPath=childPath/"config.yaml"
        with open(configPath,mode="r",encoding="utf-8") as f:
            configDict=yaml.safe_load(f)
        tree01=AnoyParser(configDict)
        tree01.dirDFS(anoyPath)
    # log.txtの比較。
    outputLogPath=suitePath/"output_log.txt"
    expectedLogPath=suitePath/"expected_log.txt"
    with open(outputLogPath,mode="r",encoding="utf-8") as f1:
        outputTextLiens=f1.readlines()
    with open(expectedLogPath,mode="r",encoding="utf-8") as f1:
        expectedTextLines=f1.readlines()
    diffIter=difflib.unified_diff(outputTextLiens,expectedTextLines)
    diffList=list(diffIter)
    assert diffList==[]

def test_invalid_anoy(outName:str="output.yaml",expName:str="expected.yaml",isTest=True):
    """
    @Summ: configが正常∧anoyが異常な場合をtestする。

    @Args:
      outName:
        @Summ: 結果を出力するfile名。
        @Type: Str
        @Default: output.yaml
      expName:
        @Summ: 期待値のfile名。
        @Type: Str
        @Default: expected.yaml
      isTest:
        @Summ: testの時にTrue.
        @Default: true
        @Type: Bool
    """
    inputPath=TESTS_DIR/"invalid_anoy"/"testsuite"/"in"
    outDict={}
    for childPath in inputPath.iterdir():
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
                errorDict["yamlPath"]=e.yamlPath
                errorDict["msg"]=e.msg
            elif(type(e)==AnnotationTypeError):
                errorType="AnnotationTypeError"
                errorDict["errorType"]=errorType
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
    outputPath=TESTS_DIR/"invalid_anoy"/"testsuite"/outName
    with open(outputPath,mode="w",encoding="utf-8") as f:
        yaml.safe_dump(outDict,f)
    if(isTest):
      expectedPath=TESTS_DIR/"invalid_anoy"/"testsuite"/expName
      with open(expectedPath,mode="r",encoding="utf-8") as f:
          expDict=yaml.safe_load(f)
      assert outDict==expDict


def test_invalid_config():
    """
    @Summ: configが異常∧anoyが正常な場合をtestする。
    """
    assert True


if(__name__=="__main__"):
    test_invalid_anoy02()
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
