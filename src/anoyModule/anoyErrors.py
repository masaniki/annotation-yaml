
class AnoyError(Exception):
  """
  @Summ: annotation yaml上のError。
  """
  def __init__(self, *args):
    super().__init__(*args)


class AnoyTypeError(Exception):
  """
  @Summ: annotation yaml上のdata型のError。
  """
  def __init__(self,type:str,fileName:str,path:list):
    super().__init__()
    self.type=type
    self.fileName=fileName
    self.path=path
  
  def __str__(self):
    return f"required {self.type} type at:\n    {self.fileName}: {self.path}"

class ConfigYamlError(Exception):
  """
  @Summ: annotation yaml上のError。
  """
  def __init__(self, *args):
    super().__init__(*args)

