from pathlib import Path
import sys

#sys.pathを弄る。
projectDir=Path(__file__).parent.parent.parent
sys.path.append(str(projectDir))

from library import module1

testDir=Path(__file__).parent/"test"

def test_example_file(exampleName:str,outName:str=None,isTest:bool=None)->bool:
    """
    Abst: 1つの事例をtestする関数。

    Expl: 入力dataや出力dataがfileの場合。

    Args:
        exampleName(str): test caseのdirecotry名。
        outName(str): 出力先のfile名。拡張子は不要。
        isTest(bool): 期待出力と実際出力を比較する⇒True。
    Returns:
        bool: 期待通りの出力⇒True。
    """
    if(outName is None):
        outName="output"
    if(isTest is None):
        isTest=True
    exampleDir=testDir/exampleName
    inFile=exampleDir/"input.txt"
    outFile=exampleDir/f"{outName}.txt"
    expFile=exampleDir/"expected.txt"
    parser1=module1()
    tree=parser1.parseFromFile(inFile)
    with open(outFile,mode="w",encoding="utf-8") as f:
        f.write(tree.pretty())
    if(isTest):
        with open(outFile,mode="r",encoding="utf-8") as f:
            outText=f.read()
        with open(expFile,mode='r',encoding="utf-8") as f:
            expText=f.read()
        return outText==expText

def test_example_dir(exampleName:str,outName:str=None,isTest:bool=None):
    """
    Abst: 1つの事例をtestする関数。

    Expl: 入力dataや出力dataがdirectoryの場合。

    Args:
        exampleName(str): test caseのdirecotry名。
        outName(str): 出力先のfile名。拡張子は不要。
        isTest(bool): 期待出力と実際出力を比較する⇒True。
    """
    if(outName is None):
        outName="output"
    if(isTest is None):
        isTest=True
    exampleDir=testDir/exampleName
    inDir=exampleDir/"in"
    inFile=inDir/"in.txt"
    outDir=exampleDir/f"{outName}"
    if(not outDir.is_dir()):
        outDir.mkdir()
    outFile=outDir/"out.txt"
    expDir=exampleDir/"exp"
    expFile=expDir/"exp.txt"
    parser1=module1()
    tree=parser1.parseFromFile(inFile)
    with open(outFile,mode="w",encoding="utf-8") as f:
        f.write(tree.pretty())
    if(isTest):
        with open(outFile,mode="r",encoding="utf-8") as f:
            outText=f.read()
        with open(expFile,mode='r',encoding="utf-8") as f:
            expText=f.read()
        return outText==expText   


def test_all(outName:str=None,isTest:bool=None)->dict:
    """
    Abst: 全てのtest caseをtestする関数。

    Args:
        outName(str): 出力先のfile名。拡張子は不要。
        isTest(bool): 期待出力と実際出力を比較する⇒True。
    Returns:
        dict: {testCase名(str):真理値(bool)}
    """
    resultDict={}
    for exampleDir in testDir.iterdir():
        exampleName=exampleDir.name
        result=test_example_dir(exampleName,outName=outName,isTest=isTest)
        resultDict[exampleName]=result
    return resultDict

def test_clear(deleteList:list):
    """
    Abst: test caseのdirectoryを綺麗にする関数。

    Expl: fileの削除にしか対応していない。

    Notes: blacklist方式にすることで、意図しないfile削除を起こさないようにしている。

    Args:
        deleteList(list): 削除するfile名のlist。file名はexample directoryからの相対pathで指定する。
    """
    for exampleDir in testDir.iterdir():
        for fileDir in exampleDir.iterdir():
            fileName=fileDir.name
            if(fileName in deleteList):
                fileDir.unlink()


if(__name__=="__main__"):
    tup=("case2", 70)
    x=tup[0]
    y=tup[1]
    test_example_file("case01","out",isTest=False)
    # test_all("out",isTest=False)


