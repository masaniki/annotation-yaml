# 目次

- **Annotation YAML(ANOY)**

  YAMLのMap型にdata型の概念を導入したYAML file。

  More about [ANOY](about_anoy_jp.md)

- **Configuration YAML(Config YAML)**

  Annotation YAMLで使えるdata型を定義するYAML file。

  More about Config YAML <- Here

- **ANOY CLI**
  
  Annotation YAMLがConfiguration YAMLのdata型を守っているかを確認するCLI application。

  More about [ANOY CLI](about_anoycli_jp.md)

# Configuration YAML(Config YAML)について

> [!Note]
> 以降、configurationはconfigと略す。

*ANOY* を使うには、事前にdata型を定義するYAML fileが必要である。

その記述を行うのが *config yaml* である。

接頭辞`!`から始まる文字列型を *config keyword* と呼ぶ。

*config yaml* 内において、*config keyword* は特殊な役割をする。

## *annotation key* の親子関係を定義する。

Map型の入れ子は以下のような構造になっている。

```
{ <parent_annotation_key> :
  { <current_annotation_key> :
      <current_annotation_value>
  }
}
```

*config yaml* の例

```
@CurrentKey:
  !ParentKey:
  - @XXX
  - @YYY
  - @ZZZ
  !ChildValue: !Str
```


`!ParentKey`は、`<current_annotation_key>`と`<parent_annotaiton_key>`の関係を指定するためのkeywordである。

`!ChildValue`は、`<current_annotation_key>`と`<current_annotation_value>`の関係を指定するkeywordである。

### 詳細

`!ParentKey`:
- @Summary: 上図の`<parent_annotation_key>`の所を指定数するためのkeyword.
- @Description:
  - ここに記述していないannotation keyは`<current_annotaion_key>`の親要素にはなれない。
  - nullは親要素が存在しないことを表す(つまりこの要素がroot要素である)。
- @Type: AnnotationKeyのList型。

`!ChildValue`:
- @Summary: 上図の`<annotation_value>`のdata型を指定する。
- @Description: data型の指定方法については次の項で解説している。

## data型を定義する。

`<current_annotation_key>`に対応するdata型は`!ChildValue` keywordで指定することができる。

data型の種類は基本的にoriginalのYAMLと同じであるが、いくつかの点で異なる。

| YAML  | ANOY       | 意味 |
| ---   | ---        | --- |
| null  | ---        | Null型 |
| bool  | `!Bool`    | 真理値型 |
| int   | `!Int`     | 整数型 |
| float | `!Float`   | 不動小数点型 |
| str   | `!Str`     | 文字列型 |
| ---   | `!Enum`    | 列挙型 |
| seq   | `!List`    | リスト型 |
| map   | `!AnnoMap` | 全てのkeyが`@`から始まるmap型 |
| map   | `!FreeMap` | `@`から始まるkeyを持たないmap型 |

data型の指定には二種類の方法が使える。それは *string-format* と *map-format* である。

### *string-fomat*

*config yaml* 上のstr型literalでdata型を指定する方法。

### *map-format*

*config yaml* 上のmap型literalでdata型を指定する方法。

*string-format* よりもより詳細な情報を指定できる。

*map-format* でdata型を指定する場合は、data型を表す *config keyword* をmap型のkeyに指定すれば良い。


### data型一覧

`!Str`:
- @Summ: 文字列型を表す。
- @MapFormat:
  - !Map:
    - length:
      - @Summ: 文字列の長さ(固定長)。
      - @Type: !Int
    - min:
      - @Summ: 文字列の長さ(最小値)。
      - @Type: !Int
    - max:
      - @Summ: 文字列の長さ(最大値)。
      - @Type: !Int

`!Bool`:
- @Summ: 真理値型を表す。
- @MapFormat: false

`!Int`:
- @Summ: 整数型を表す。
- @MapFormat:
  - !Map:
    - min:
      - @Summ: 区間の最小値。
      - @Type: !Int
    - max:
      - @Summ: 区間の最大値。
      - @Type: !Int

`!Float`:
- @Summ: 不動小数点型を表す。
- @MapFormat:
  - !Map:
    - min:
      - @Summ: 区間の最小値。
      - @Type: !Float
    - max:
      - @Summ: 区間の最大値。
      - @Type: !Float

`!Enum`:
- @Summ: 列挙型を表す。
- @Desc:
  - 列挙型の構成要素はliteralのみ。
  - 構成要素はliteralやliteralをkeyとするdict型である。
- @MapFormat:
  - !List:
    - 
    - {Enum:構成要素(list型)}
- @Nestable: false
- @Example:
  - {Enum:["a","b","c"]}

`!List`:
- @Nestable: true
- @MapFormat:
  - !Map:
    - type:
      - @Summ: data型を指定する。
      - @Type: !Str
    - length:
      - @Summ: listの長さを指定する。

`!AnnoMap`:
- @Summ: annotation keyによるmap型。
- @Desc: Dict型はAnnoDict型とFreeDict型にMECEに分解される。
- @Nestable: true
- 

`!FreeMap`:
- @Summ: free keyによるmap型。
- @Nestable: true

## Example
```
"@Books":
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