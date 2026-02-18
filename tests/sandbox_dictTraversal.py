import pytest
from pathlib import Path
import sys
import yaml

#sys.pathを弄る。
projectDir=Path(__file__).parent.parent
sys.path.append(str(projectDir))

from src.anoy import AnoyParser

parnetDir=Path(__file__).parent

if(__name__=="__main__"):
    sandboxDir=parnetDir/"valid_anoy"/"sandbox"
    configPath=sandboxDir/"invalid_grandparent01"/"config.yaml"
    anoyPath=sandboxDir/"invalid_grandparent01"/"anoy.yaml"
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    tree01=AnoyParser(configDict)
    tree01.dirDFS(anoyPath)
