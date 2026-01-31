import pytest
from pathlib import Path
import sys
import yaml

#sys.pathを弄る。
projectDir=Path(__file__).parent.parent.parent
sys.path.append(str(projectDir))

from src.anoyModule import DictTraversal

testDir=Path(__file__).parent/"test"
sandboxDir=Path(__file__).parent/"sandbox"

if(__name__=="__main__"):
    configPath=sandboxDir/"valid_float01"/"config.yaml"
    anoyPath=sandboxDir/"valid_float01"/"anoy.yaml"
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    tree01=DictTraversal(configDict)
    tree01.dirDFS(anoyPath)

