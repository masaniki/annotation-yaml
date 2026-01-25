# Annotaion YAML(ANOY)

ベースはYAMLで記述する。

特殊なkeyには接頭辞`@`を付ける。これを"annotation key"と呼ぶ。

また、annotation keyに対応するvalueを"annotation value"と呼ぶ。

現在はannotation keyをUpperCammelCaseで記述しているが、これは必須ではない。

逆に接頭辞が付いていないkeyを"free key"と呼ぶ。

free keyが許容されているDict型はFreeDict型として区別する。

annotation keyの一覧を格納したyamlをconfigration yamlと呼ぶ。

configuration yaml専用のkeyには`!`を付ける。これを"configuration key"と呼ぶ。

また、configuration keyに対応するvalueを"configuration value"と呼ぶ。

## config yamlの詳細

configuration key一覧

- !ParentKey:
  - @Summ: 親要素に指定できるkeyを記述する。ここに記述していないannotation keyはこの要素の親要素にはなれない。
  - @Desc: nullは親要素が存在しないことを表す(つまりこの要素がroot要素である)。
  - @Type: AnnotationKeyのList型。
- !ChildValue:
  - @Summ: annotation valueのdata型を指定する。
  - @Desc:
    - null型で記述されるdata型。
      - null:
        - @Summ: data型を指定しないことを表す。
    - str型で記述されるdata型(=type string)
      - Bool
      - Str
      - Int
      - Float
      - List:
        - @Nestable: true
      - AnnoDict:
        - @Summ: annotation keyによるdict型。
        - @Desc: Dict型はAnnoDict型とFreeDict型にMECEに分解される。
        - @Nestable: true
      - FreeDict
        - @Summ: free keyによるdict型。
        - @Nestable: true
    - dict型で記述されるdata型(=type dict)
      - Enum:
        - @Summ: 列挙型
        - @Desc:
          - {Enum:構成要素(list型)}
          - 列挙型の構成要素はliteralのみ。
          - 構成要素はliteralやliteralをkeyとするdict型である。
        - @Nestable: false
        - @Example:
          - {Enum:["a","b","c"]}
  - @Type: Str

# ANOY CLI

ANOY(=annotation yaml)用のCLI(=Command Line Interface)。`anoy`で起動する。

ANOY CLIが提供する機能
- annotation keyのtypoの検出。
- annotation valueの型確認。
- configuration keyによる型確認。

## data型の記述。

JSONに対応するdata型は、defaultで使える用にする。

JSONで使える型
- Null
- Bool
- Str
- Int
- Float
- List
- Dict

それに加えて、EnumやUnion、Array、Ndarrayなどのdata型を加えるか否か。

これらはliteral的な表現ができる。

# 下位規格の紹介

## Object-Oriented Document YAML(OODY)

object oriented document in YAML、略してOODY。

object指向を表現するためのdocument。

特定のprogramming言語に依存しないように設計する。

ANOYの下位規格。

## YAML with Summary(YwS)

YAMLの階層構造を説明するためのANOYの規格。

ANOYの下位規格。

# その他

## メモ

list型とlist型literalは違う、Enum型についても同様だ。

しかしながら、ANOY用のYAML parserの設計costが高すぎて断念。

## Ideas

開いているkey-valueはblock-styleで記述して、閉じているkey-valueはinline-styleで記述する？

ANOYを静的型付け言語にするか否か。

静的型付け言語にするのは本来の目的に逸れる気がする。

厳密な静的型付け言語にするなら、parserと同等の機能を有する必要がある。

それともYAML parserを簡単に設計できるtoolとして公開するか？

