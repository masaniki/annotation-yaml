
class AnoyError(Exception):
  """
  @Summ: ANOYによる例外の基底class.

  @InsVars:
    fileName:
      @Summ: 例外を発したanoyのfile名。
      @Type: Str
    yamlPath:
      @Summ: 例外を発生した位置。
      @SemType: Str型List
    msg:
      @Summ: 例外message.
      @ComeFrom: message.
      @Type: Str
  """
  def __init__(self,fileName:str,yamlPath:list,msg:str):
    super().__init__()
    self.fileName=fileName
    self.yamlPath=yamlPath
    self.msg=msg

  def __str__(self):
    return f"\n    {self.fileName}: {self.yamlPath}:\n    {self.msg}"

class AnnotationKeyError(AnoyError):
  """
  @Summ: annotation keyが存在しないことによるANOYの例外。
  
  @Parent: AnoyError
  """
  def __init__(self,fileName:str,yamlPath:list,annoKey:str):
    """
    @Args:
      fileName:
        @Summ: pass
      yamlPath:
        @Summ: pass
      annoKey:
        @Summ: 例外の原因となったannotation key.
        @Type: Str
    """
    msg=f"{annoKey} is not found."
    super().__init__(fileName,yamlPath,msg)

class AnnotationTypeError(AnoyError):
  """
  @Summ: data型によるANOYの例外。
  
  @Parent: AnoyError
  """
  def __init__(self,fileName:str,yamlPath:list,annoType:str):
    """
    @Args:
      fileName:
        @Summ: pass
      yamlPath:
        @Summ: pass
      annoType:
        @Summ: 例外の原因となったdata型名。
        @Type: Str
    """
    msg=f"{annoType} contradiction."
    super().__init__(fileName,yamlPath,msg)

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
    return f"{self.msg}\n    {self.configPath}"


