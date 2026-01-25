# exception directoryで例外testする関数。
from pathlib import Path
import sys
import yaml

#sys.pathを弄る。
projectDir=Path(__file__).parent.parent.parent
sys.path.append(str(projectDir))

from library.symnetVer01 import SymNet
from library.symnetVer01 import Deductor01

exceptionDir=Path(__file__).parent/"exception"

# {例外testのfile名(str):[例外class(Exception),例外のinstance変数(str),...]}
EXCEPTION_DICT={
    "test_link01":[SyntaxError,"The argument B is not defined."],
    "test_use01": [KeyError,"arg1"],
}

def test_exception_example(exampleName:str,outName:str=None,isTest:bool=None)->bool:
    """
    Abst: 1つの例外をtestする関数。

    Args:
        exampleName(str): test例のdirecotry名。
        outName(str): 出力先のfile名。拡張子は不要。
        isTest(bool): 期待出力と実際出力を比較する⇒True。
    Returns:
        bool: 期待通りの例外⇒True.
    """
    if(outName is None):
        outName="output"
    if(isTest is None):
        isTest=True
    exampleDir=exceptionDir/exampleName
    inDir=exampleDir/"in"
    labnetFile=inDir/"input_labnet.yaml"
    programFile=inDir/"program.txt"
    outDir=exampleDir/f"{outName}"
    if(not outDir.is_dir()):
        outDir.mkdir()
    labnetFile=inDir/"input_labnet.yaml"
    programFile=inDir/"program.txt"
    with open(labnetFile,mode="r",encoding="utf-8") as f:
        labnetDict=yaml.safe_load(f)
    sn1=SymNet.initFromLabDict(labnetDict)
    inputDot=sn1.getDot(title=exampleName)
    inputDot.format="svg"
    inputDot.render(outDir/"input.dot")
    exceptionList=EXCEPTION_DICT[exampleName]
    exceptionType=exceptionList[0]
    exceptionArgs=tuple(exceptionList[1:])
    if(isTest):
        try:
            deductor1=Deductor01(sn1)
            deductor1.parseFromFile(programFile)
            return False
        except exceptionType as e:
            if(e.args==exceptionArgs):  #例外classの引数が全て等しい。
                return True
            else:
                return False
    else:
        deductor1=Deductor01(sn1)
        deductor1.parseFromFile(programFile)

def test_exception_all(outName:str=None,isTest:bool=None)->dict:
    """
    Abst: 全ての例外をtestする関数。

    Args:
        outName(str): 出力先のfile名。拡張子は不要。
        isTest(bool): 期待出力と実際出力を比較する⇒True。
    Returns:
        dict: {例名(str):結果(bool)}。
    """
    resultDict={}
    for exampleDir in exceptionDir.iterdir():
        exampleName=exampleDir.name
        result=test_exception_example(exampleName,outName=outName,isTest=isTest)
        resultDict[exampleName]=result
    return resultDict

if(__name__=="__main__"):
    tup=("case2", 70)
    x=tup[0]
    y=tup[1]
    bool1=test_exception_example("test_use01","out",isTest=False)
    # dict1=bool1=test_exception_all("out",isTest=True)
    # print(dict1)
    # test_all("out",isTest=False)