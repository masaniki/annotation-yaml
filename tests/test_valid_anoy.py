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


if(__name__=="__main__"):
    test_valid_anoy()
