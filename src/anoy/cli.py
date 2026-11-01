import sys
from pathlib import Path
import argparse
import yaml
import logging
import logging.config


from .anoyParser import AnoyParser

VERSION="v0.5.1"

def main():
    """
    "@Summ": CLIを処理するmain関数。
    "@Desc": 引数は標準入力から渡される。
    """
    parser=argparse.ArgumentParser(prog="anoy")
    parser.add_argument("-v","--version", action="version", version="%(prog)s "+f"{VERSION}")
    parser.add_argument("config", type=str, default=None, help="Put in configuration yaml.")
    parser.add_argument("anoy", type=str, default=None, help="Put in annotation yaml.")
    parser.add_argument("-d","--debug", action="store_true", help="Debug mode. Output progress to the terminal.")
    parser.add_argument("-e","--exception", action="store_true", help="Exception mode. Once it raises exectpion, stop the program.")

    # 引数の処理。
    args=parser.parse_args()
    configPath=Path(args.config)
    anoyPath=Path(args.anoy)
    if(args.debug):
        loggingMode="INFO"
    else:
        loggingMode="ERROR"
    exceptionMode=args.exception
    # 前処理
    configDict={
        "version": 1,
        "formatters":{
            "product":{
                "format": "%(message)s"
            }
        },
        "handlers":{
            "prodConsole":{
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "product",
                "stream": "ext://sys.stdout"
            }
        },
        "root":{
            "level": loggingMode,
            "handlers": ["prodConsole"]
        }
    }
    logging.config.dictConfig(configDict)
    LOGGER=logging.getLogger(__name__)
    with open(configPath,mode="r",encoding="utf-8") as f:
        configDict=yaml.safe_load(f)
    tree01=AnoyParser(configDict,exceptionMode)
    tree01.dirDFS(anoyPath)

if(__name__=="__main__"):
    main()

