import sys
from pathlib import Path
import argparse
import yaml
import logging
import logging.config

# loggingの生成。
PACKAGE_DIR=Path(__file__).parent
CONFIG_FILE=PACKAGE_DIR/"logging_config.yaml"
with open(CONFIG_FILE,mode="r",encoding="utf-8") as f:
  configDict=yaml.safe_load(f)
logging.config.dictConfig(configDict)
LOGGER=logging.getLogger(__name__)

from .anoyParser import AnoyParser

LOGGER=logging.getLogger(__name__)
VERSION="v0.5.0"

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

