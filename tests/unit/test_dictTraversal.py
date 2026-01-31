import pytest
from pathlib import Path
import sys
import yaml

#sys.pathを弄る。
projectDir=Path(__file__).parent.parent.parent
sys.path.append(str(projectDir))

from src.modules import DictTraversal
from src.modules import AnnotationKeyError, AnnotationTypeError, ConfigYamlError

testDir=Path(__file__).parent/"test"
sandboxDir=Path(__file__).parent/"sandbox"


@pytest.mark.parametrize(
        "x,y",[
        ("case01/config01.yaml", "case01/valid_anoy.yaml"),
        ("valid_parent01/config.yaml", "valid_parent01/anoy.yaml"),
        ("valid_parent02/config.yaml", "valid_parent02/anoy.yaml"),
        ("valid_str01/config.yaml", "valid_str01/anoy.yaml"),
        ("valid_int01/config.yaml", "valid_int01/anoy.yaml"),
        ("valid_list01/config.yaml", "valid_list01/anoy.yaml"),
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
    tree01=DictTraversal(configDict)
    tree01.dirDFS(anoyPath)
    assert True

@pytest.mark.parametrize(
        "x,y,z",[
        ("case02/config01.yaml", "case02/invalid_int.yaml", AnnotationTypeError),
        ("typo01/config.yaml", "typo01/anoy.yaml", AnnotationKeyError),
        ("invalid_parent01/config.yaml", "invalid_parent01/anoy.yaml", AnnotationTypeError),
        ("invalid_parent02/config.yaml", "invalid_parent02/anoy.yaml", AnnotationTypeError),
        ("invalid_str01/config.yaml", "invalid_str01/anoy.yaml", AnnotationTypeError),
        ("invalid_str02/config.yaml", "invalid_str02/anoy.yaml", AnnotationTypeError),
        ("invalid_str03/config.yaml", "invalid_str03/anoy.yaml", AnnotationTypeError),
        ("invalid_int01/config.yaml", "invalid_int01/anoy.yaml", AnnotationTypeError),
        ("invalid_list01/config.yaml", "invalid_list01/anoy.yaml", AnnotationTypeError),
        ("invalid_list02/config.yaml", "invalid_list02/anoy.yaml", AnnotationTypeError),
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
        tree01=DictTraversal(configDict)
        tree01.dirDFS(anoyPath)
    assert e.type==z

@pytest.mark.parametrize(
        "x,y",[
        ("case04/config.yaml", "case04/anoy"),
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
        ("case05/config.yaml", "case05/anoy", AnnotationTypeError),
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
    args=("invalid_str01/config01.yaml", "invalid_str01/invalid_anoy.yaml")
    test_valid_anoyFile(*args)


