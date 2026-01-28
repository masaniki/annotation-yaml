import pytest
from pathlib import Path
import sys
import yaml

#sys.pathを弄る。
projectDir=Path(__file__).parent.parent.parent
sys.path.append(str(projectDir))

from src.anoyModule import DictTraversal
from src.anoyModule import AnnotationYamlTypeError

testDir=Path(__file__).parent/"test"
sandboxDir=Path(__file__).parent/"sandbox"


@pytest.mark.parametrize(
        "x,y",[
        ("case01/config01.yaml", "case01/valid_anoy.yaml"),
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
    tree01=DictTraversal(configDict)
    tree01.dirDFS(anoyPath)
    assert True

@pytest.mark.parametrize(
        "x,y,z",[
        ("case02/config01.yaml", "case02/invalid_int.yaml", AnnotationYamlTypeError),
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
        tree01=DictTraversal(configDict)
        tree01.dirDFS(anoyPath)
    assert e.type==z

@pytest.mark.parametrize(
        "x,y",[
        ("case04/config01.yaml", "case04/anoy"),
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
    tree01=DictTraversal(configDict)
    tree01.dirDFS(anoyPath)
    assert True

@pytest.mark.parametrize(
        "x,y,z",[
        ("case05/config01.yaml", "case05/anoy", AnnotationYamlTypeError),
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
        tree01=DictTraversal(configDict)
        tree01.dirDFS(anoyPath)
    assert e.type==z

if(__name__=="__main__"):
    args=("case02/config01.yaml", "case02/invalid_int.yaml")
    test_valid_anoyFile(*args)


