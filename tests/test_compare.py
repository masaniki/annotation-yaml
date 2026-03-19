import difflib
from pathlib import Path

PARENT_DIR=Path(__file__).parent

def test_valid_anoy_compare():
  validAnoyDir=PARENT_DIR/"valid_anoy"/"testsuite"
  outputValidAnoyDir=validAnoyDir/"output_log.txt"
  expectedValidAnoyDir=validAnoyDir/"expected_log.txt"
  with open(outputValidAnoyDir,mode="r",encoding="utf-8") as f1:
    outputLines=f1.readlines()
  with open(expectedValidAnoyDir,mode="r",encoding="utf-8") as f2:
    expectedLines=f2.readlines()
  diffIter=difflib.unified_diff(outputLines,expectedLines)
  diffList=list(diffIter)
  assert diffList==[]

def test_invalid_anoy_compare():
  invalidAnoyDir=PARENT_DIR/"invalid_anoy"/"testsuite"
  outputValidAnoyDir=invalidAnoyDir/"output_log.txt"
  expectedValidAnoyDir=invalidAnoyDir/"expected_log.txt"
  with open(outputValidAnoyDir,mode="r",encoding="utf-8") as f1:
    outputLines=f1.readlines()
  with open(expectedValidAnoyDir,mode="r",encoding="utf-8") as f2:
    expectedLines=f2.readlines()
  diffIter=difflib.unified_diff(outputLines,expectedLines)
  diffList=list(diffIter)
  assert diffList==[]

if(__name__=="__main__"):
  test_valid_anoy_compare()
  test_invalid_anoy_compare()
