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

Map型の入れ子は以下のような構造になる。

```
  <parent>:
    <me>:
      <child>
```

`!Parent`は、`<me>`と`<parent>`の関係を指定するためのkeywordである。

`!Child`は、`<me>`と`<child>`の関係を指定するkeywordである。

### `!Parent`
- @Summary: 親要素を指定するための *config key*。
- @Description:
  - 親要素になれる *annotation key* のlist型。
  - listの中にnullを入れることができ、それは親要素が存在しないことを表す。
  - `!Parent`で指定したlistの中に無いannotation keyは親になることができない。
- @Type: *annotation key* のlist.
- @Example:
  ```
  @Something:
    !Parent:
    - "@xxx"
    - "@yyy"
    - "@zzz"
  ```

### `!Child`
- @Summary: annotaiton keyに対応するvalueのdata型を指定する。
- @Description:
  - 親要素になれるannotation keyのlist型。
  - Map型を選択する場合は、keyがと同じである必要がある。
- @Type: `<type_string>` | {`<type_string>`:`<type_option>`(list|dict)}
- @Example:
  ```
  @Something:
    !Child: !Str
  ```
  ```
  @Something:
    !Child:
      !Str:
        min: 4
        max: 8
  ```

## data型を定義する。

`!Child`に対応する値でdata型を指定することができる。

data型の指定には2種類の方法が使える。それは *string-format* と *map-format* である。

### *string-format* について

data型を最も簡単に指定する方法は以下の方法である。

```
@Something:
  !Child: <data型を指定するためのconfig_key(type_stringと呼ばれる)>
```

この構文を *string-format* と呼ぶ。

data型を指定するために用いる *config key* を *type string* と呼ぶ。

以下は *type string* の一覧である。

*type string* であっても、*string-format* には使えないものもある点に注意。

| ANOY       | YAML  | string-format | map-format | 意味 |
| ---        | ----- | :---: | :---: | ---    |
| ---        | null  | ---   | ---   | Null型 |
| `!Bool`    | bool  | o | x | 真理値型 |
| `!Int`     | int   | o | o | 整数型 |
| `!Float`   | float | o | o | 不動小数点型 |
| `!Str`     | str   | o | o | 文字列型 |
| `!Enum`    | ---   | x | o | 列挙型とUnion型 |
| `!List`    | seq   | o | o | リスト型 |
| `!AnnoMap` | map   | o | o | 全てのkeyが`@`から始まるmap型 |
| `!FreeMap` | map   | o | x | `@`から始まるkeyを持たないmap型 |

Example:
```
@Something:
  !Child: "!Str"
```
以上の記述で、"@Something"に対応する値には文字列型が入ることを表現できる。

### *map-foramt* について

文字列の長さや最大値最小値のように、より詳細にdata型を指定したい場合は、以下のような構文を用いることができる。

```
@Something:
  !Child:
    <type_string>:
      <List型もしくはMap型(type_optionと呼ぶ。)>
```

この構文を *map-format* と呼ぶ。

## *map-format* 一覧

`!Str`:
- @TypeOption:
  - length:
    - @Summary: 文字列の長さ(固定長)。
    - @Type: !Int
  - min:
    - @Summary: 文字列の長さ(最小値)。
    - @Type: !Int
  - max:
    - @Summary: 文字列の長さ(最大値)。
    - @Type: !Int

`!Int`:
- @TypeOption:
  - min:
    - @Summary: 区間の最小値。
    - @Type: !Int
  - max:
    - @Summary: 区間の最大値。
    - @Type: !Int

`!Float`:
- @TypeOption:
  - min:
    - @Summary: 区間の最小値。
    - @Type: !Int | !Float
  - max:
    - @Summary: 区間の最大値。
    - @Type: !Int | !Float

`!Enum`:
- @Summary: 列挙型を表す。
- @Description:
  - map型を要素にすると、map型のkeyの中から要素を選択することになる。
  - *type_string* を要素にすると、data型を混ぜて列挙型を形成できる。
  これにより、Union型のような使い方ができる。
- @TypeOption:
  - 列挙型の構成要素のlist型。
- @Example:
  ```
  @Something:
    !Child:
      !Enum:
      - "a"
      - "b"
      - "c"
  ```

`!List`:
- @TypeOption:
  - type:
    - @Summary: data型を指定する。
    - @Type: !Str
  - length:
    - @Summary: listの長さを指定する。

`!AnnoMap`:
- @TypeOption:
  - !List:
    - @Summary: 最低限必要なannotation keyを羅列する。
    - @Description: annotationKey型list。


## Example
```
"@Books":
  "@Summary": 本の名前を羅列する。
  "!Child": "!FreeDict"
"@Author":
  "@Summary": 本の筆者を記述する。
  "!Child": "!Str"
"@PublishYear":
  "@Summary": 本が発売された年。
  "!Child": "!Int"
"@Country":
  "@Summary": 筆者の母国語。
  "!Child": "!Str"
```