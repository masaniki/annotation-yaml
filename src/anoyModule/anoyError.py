
class AnnotationYamlError(Exception):
  """
  @Summ: annotation yaml上のError。
  """
  def __init__(self, *args):
    super().__init__(*args)


class AnnotationYamlTypeError(Exception):
  """
  @Summ: annotation yaml上のdata型のError。
  """
  def __init__(self,fileName:str,type:str,path:list):
    super().__init__()
    self.fileName=fileName
    self.type=type
    self.path=path
  
  def __str__(self):
    return f"required {self.type} type at:\n    {self.fileName}: {self.path}"

class ConfigurationYamlError(Exception):
  """
  @Summ: annotation yaml上のError。
  """
  def __init__(self, *args):
    super().__init__(*args)

