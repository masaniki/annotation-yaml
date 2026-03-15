from pathlib import Path
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
from .confParser import ConfParser
from .errors import ConfigYamlError
from .cli import main

__all__=[
  AnoyParser,
  ConfParser,
  ConfigYamlError,
  main
]

