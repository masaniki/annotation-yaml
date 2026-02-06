# 目次

- **English Document**

  [English Document](../README.md)

- **Japanese Document**

  Japanese Document <- Here

- **Annotation YAML(ANOY)**

  Map型について型確認ができるYAML file。

  More about [ANOY](about_anoy_jp.md)

- **Configuration YAML(Config YAML)**

  Annotation YAMLで使えるdata型を定義するYAML file。

  More about [Config YAML](about_config_jp.md)

- **ANOY CLI**
  
  Annotation YAMLがConfiguration YAMLのdata型を守っているかを確認するCLI application。

  More about [ANOY CLI](about_anoycli_jp.md)

# 紹介

YAMLのMap型はしばしば入れ子構造になり、複雑化する。

そこで以下の様な問題が発生しました。

- Map型のkeyのtypoを検出したい。
- Map型のvalueのdata型を確認したい。
- Map型の入れ子構造が適切かを確認したい。

これらの問題を解決するためにANOY libraryは生まれた。

# インストール方法

`pip install anoy`

## パッケージ依存性

以下のpackageをインストールしないと正しく機能しない場合があります。

- [PyYAML](https://pypi.org/project/PyYAML/): 最も人気なPyhton用のYAMLパーサーです。

# 使い方

library_config.yaml

```
"@Book":
  "@Summary": 本の名前を羅列する。
  "!ChildValue": FreeDict
"@Author":
  "@Summary": 本の筆者を記述する。
  "!ChildValue": Str
"@PublishYear":
  "@Summary": 本が発売された年。
  "!ChildValue": Int
"@Country":
  "@Summary": 筆者の母国語。
  "!ChildValue": Str
```

valid_library.yaml:

```
"@Books":
  "Alice's Adventures in Wonderland":
    "@Author": Lewis Carroll
    "@PublishYear": 1865
    "@Country": UK
  "The Little Prince":
    "@Author": Antonie de Saint-Exupéry
    "@PublishYear": 1945
    "@Country": France
  "Harry Potter":
    "@Author": J.K.Rowling
    "@PublishYear": 1997
    "@Country": UK
```

`anoy`コマンドでデータ型の確認を実行する。

データ型に異常が無かったら何も出力しない。

```
>>> anoy library_config.yaml library.yaml
>>> 
```

あなたが`@Auther`を`@Auther`とtypoしたとする。

invalid_library.yaml:

```
"@Books":
  "Alice's Adventures in Wonderland":
    "@Auther": Lewis Carroll
    "@PublishYear": 1865
    "@Country": UK
  "The Little Prince":
    "@Auther": Antonie de Saint-Exupéry
    "@PublishYear": 1945
    "@Country": France
  "Harry Potter":
    "@Auther": J.K.Rowling
    "@PublishYear": 1997
    "@Country": UK
```

annotation YAMLに異常がある時は、以下の様に出力する。

```
>>> anoy library_config.yaml library.yaml
>>> 
>>> 
```

# 詳細

・AnoyKeyErrorは、見つからないkeyを明示する。
・AnoyValueErrorは、矛盾する値を格納するkeyを明示する。

## Next To Do

- [ ] checkAnoyの引数をtypeOptionに統一。
- [ ] checkAnoyの戻り値をBool型にする。
- [ ] anoyの探索方法を関数型深さ優先探索に変更。
- [ ] data型の入れ子を可能にする。

## Ideas

次、実装する可能性があるideaを記述する。

# Others

## 下位規格の紹介

ANOYは *config yaml* の定義次第で下位規格を定義できる。

### Object-Oriented Document YAML(OODY)

Object-Oriented Document in YAML、略してOODY。

object指向を表現するためのdocument。

特定のprogramming言語に依存しないように設計する。

ANOYの下位規格。

### YAML with Summary(YwS)

YAMLの階層構造を説明するためのANOYの規格。

ANOYの下位規格。
