# 目次

- **Annotation YAML(ANOY)**

  YAMLのMap型にdata型の概念を導入したYAML file。

  More about [ANOY](about_anoy_jp.md)

- **Configuration YAML(Config YAML)**

  Annotation YAMLで使えるdata型を定義するYAML file。

  More about Config YAML <- Here

- **ANOY CLI**
  
  Annotation YAMLがTypedef YAMLのdata型を守っているかを確認するCLI application。

  More about [ANOY CLI](about_anoycli_jp.md)

# Configuration YAML(Config YAML)について

*ANOY* を使うには、事前にdata型を定義する必要である。

そのdata型の記述を行うのが *config yaml* である。

*annotation key* と *annotation value* のdata型の組み合わせを決めるためのYAMLを *config yaml* と呼ぶ。

接頭辞`!`から始まるkeyを *config key* と呼ぶ。

また、*config key* に対応するvalueを *config value* 、*config key* を持つMap型を *config map(TypeMap)* と呼ぶ。

*config key* は *config yaml* 内でしか効力を発揮しない。

## *config key* 一覧

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
      - AnnoMap:
        - @Summ: annotation keyによるmap型。
        - @Desc: Dict型はAnnoDict型とFreeDict型にMECEに分解される。
        - @Nestable: true
      - FreeMap
        - @Summ: free keyによるmap型。
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

## Example
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