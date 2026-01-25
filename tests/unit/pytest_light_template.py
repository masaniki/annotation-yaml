import pytest
from pathlib import Path
import sys

#sys.pathを弄る。
projectDir=Path(__file__).parent.parent
sys.path.append(str(projectDir))

from library import module1

testDir=Path(__file__).parent/"test"
sandboxDir=Path(__file__).parent/"sandbox"

#通常test
@pytest.mark.parametrize(
        "a0,a1",[
        ("(abc,xyz)","(abc,xyz)"),
        ("(a,bacd)","(a,bacd)"),
        ])
def test_name1(a0,a1):
    answer=module1.function1(a0)
    assert answer==a1

#例外test
@pytest.mark.parametrize(
        "a0,a1,a2",[
        ("ab{c", ValueError, "message1"),
        ("ab}c", ValueError, "message2")
        ])
def test_name2(a0,a1,a2):
    with pytest.raises(a1) as e:
        module1.fuction2(a0)
    assert e.type==a1
    assert str(e.value)==a2


if(__name__=="__main__"):
    tup=(["a","b","c"], ["d","e"], {"a":0, "b":1, "c":2, "d":3, "e":4})
    a0=tup[0]
    a1=tup[1]
    a2=tup[2]
    result=module1.fuction1(a0)
    print(result)
    pass
