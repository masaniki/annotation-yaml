import pytest
from pathlib import Path
import sys

#sys.pathを弄る。
projectDir=Path(__file__).parent.parent.parent
sys.path.append(str(projectDir))

from library import module1

testDir=Path(__file__).parent/"test"
sandboxDir=Path(__file__).parent/"sandbox"

#file入力
@pytest.mark.parametrize(
        "x,y",[
        ("case1", 4),
        ("case2", 4),
        ])
def test_validInit(x,y):
    in1Path=testDir/"in1"/f"{x}.txt"
    int1=open(in1Path, mode="r", encoding="utf-8").read()
    proc1=module1(int1)
    assert proc1.getLine()==y

#file入出力になったversion
@pytest.mark.parametrize(
        "x,y,z",[
        ("case1", "title", None),
        ("case2", "title2", "dot"),
        ])
def test_dotWrite(x,y,z):
    folderName="dotWrite"
    in1Path=testDir/folderName/"in1"/f"{x}.txt"
    out1Path=testDir/folderName/"out1"/f"{x}.txt"
    uxpPath=testDir/folderName/"unexpected"/f"{x}.txt"
    in1=open(in1Path, mode="r", encoding="utf-8").read()
    out1=open(out1Path, mode="r", encoding="utf-8").read()
    proc1=module1(in1)
    result=proc1.dotWrite(title=y,layout=z)
    if(result!=out1):
        with open(uxpPath, mode="w", encoding="utf-8") as f:
            f.write(result)
        assert False
    else:
        assert True

if(__name__=="__main__"):
    tup=("case2", 70)
    x=tup[0]
    y=tup[1]
    result=x
    print(result)
    pass


