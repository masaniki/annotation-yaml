# 目次

- **Annotation YAML(ANOY)**

  YAMLのMap型にdata型の概念を導入したYAML file。

  More about [ANOY](about_anoy_jp.md)

- **Configuration YAML(Config YAML)**

  Annotation YAMLで使えるdata型を定義するYAML file。

  More about [Config YAML](about_config_jp.md)

- **ANOY CLI**
  
  Annotation YAMLがTypedef YAMLのdata型を守っているかを確認するCLI application。

  More about ANOY <- Here

# 紹介

YAMLのMap型はしばしば入れ子構造になり、複雑化する。

そこで以下の様な問題が発生しました。

- Map型のkeyのtypoを検出したい。
- Map型のvalueのdata型を確認したい。
- Map型の入れ子構造が適切かを確認したい。

これらの問題を解決するためにANOY libraryは生まれた。


# インストール方法


# ANOY CLI

ANOYの型確認を行うためのCLI(Command Line Interface) applicationを **ANOY CLI** と呼ぶ。

ANOY CLIは、command名`anoy`で起動する。

`anoy [-v|--version]`

- anoyのversion情報を提供する。

`anoy [-h|--help]`

- anoyのhelp情報を提供する。

`anoy <config_yaml> <anoy>`

- `<config_yaml>`で`<anoy>`を型確認する。

# 下位規格の紹介

ANOYは *typedef yaml* の定義次第で下位規格を定義できる。

## Object-Oriented Document YAML(OODY)

object oriented document in YAML、略してOODY。

object指向を表現するためのdocument。

特定のprogramming言語に依存しないように設計する。

ANOYの下位規格。

## YAML with Summary(YwS)

YAMLの階層構造を説明するためのANOYの規格。

ANOYの下位規格。
