"""
test_fileを作るためのpython_file.
"""
import pathlib
import numpy as np

testDir=pathlib.Path(__file__).parent
projectDir=pathlib.Path(__file__).parent.parent
fileDir=testDir/"file"

path1=pathlib.Path(fileDir/"reverseShape"/"case2.txt")
rng=np.random.default_rng()
mat1=rng.integers(20,size=(5,3))
if(path1.is_file()):
    print("this file has already exsisted.")
else:
    np.savetxt(path1, mat1, fmt="%d", delimiter=",", encoding="utf-8")