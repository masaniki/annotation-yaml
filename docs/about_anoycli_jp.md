# 目次

- **Annotation YAML(ANOY)**

  YAMLのMap型にdata型の概念を導入したYAML file。

  More about [ANOY](about_anoy_jp.md)

- **Configuration YAML(Config YAML)**

  Annotation YAMLで使えるdata型を定義するYAML file。

  More about [Config YAML](about_config_jp.md)

- **ANOY CLI**
  
  Annotation YAMLがConfiguration YAMLのdata型を守っているかを確認するCLI application。

  More about ANOY <- Here

# ANOY CLI

ANOYの型確認を行うためのCLI(Command Line Interface) applicationを **ANOY CLI** と呼ぶ。

ANOY CLIは、command名`anoy`で起動する。

`anoy [-v|--version]`

- anoyのversion情報を表示する。

`anoy [-h|--help]`

- anoyのhelp情報を表示する。

`anoy <config_yaml> <anoy>`

- `<config_yaml>`で`<anoy>`を型確認する。
- `<anoy>`にはfileやdirectory名が入る。
- 拡張子[".yaml", ".yml, ".anoy"]のfileをANOY fileとして認識する。
- directory名の時は、directory内を再帰的に探索してANOY fileを探す。
