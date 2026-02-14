import sys
from pathlib import Path
import argparse
import yaml

from .anoyParser import AnoyParser

VERSION="v0.3.4"

def main():
    """
    "@Summ": CLIを処理するmain関数。
    "@Desc": 引数は標準入力から渡される。
    """
    parser=argparse.ArgumentParser(prog="anoy")
    parser.add_argument("-v","--version", action="version", version="%(prog)s "+f"{VERSION}")
    parser.add_argument("config", type=str, default=None, help="Put in configuration yaml.")
    parser.add_argument("anoy", type=str, default=None, help="Put in annotation yaml.")
    args=parser.parse_args()
    configPath=Path(args.config)
    anoyPath=Path(args.anoy)
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    tree01=AnoyParser(configDict)
    # configのload終了。
    tree01.dirDFS(anoyPath)

if(__name__=="__main__"):
    main()

