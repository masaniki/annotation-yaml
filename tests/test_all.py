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

def test_invalid_anoy():
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

def test_invalid_config():
    """
    @Summ: configが異常∧anoyが正常な場合をtestする。
    """
    assert True


if(__name__=="__main__"):
    test_invalid_anoy()
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
