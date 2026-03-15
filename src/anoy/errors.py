
class ConfigYamlError(Exception):
  """
  @Summ: config yamlによる例外の基底class.

  @InsVars:
    configPath:
      @Summ: config yaml内のpath。
      @Type: List
    msg:
      @Summ: 例外message.
      @ComeFrom: message.
      @Type: Str
      @Default: ""
  """
  def __init__(self,configPath:list,msg:str=""):
    super().__init__()
    self.configPath=configPath
    self.msg=msg

  def __str__(self):
    return f"\n    {self.configPath}\n        {self.msg}"


