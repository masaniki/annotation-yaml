# 目次

- **Annotation YAML(ANOY)**

  YAMLのMap型にdata型の概念を導入したYAML file。

  More about ANOY <- Here

- **Configuration YAML(Config YAML)**

  Annotation YAMLで使えるdata型を定義するYAML file。

  More about [Config YAML](about_config_jp.md)

- **ANOY CLI**
  
  Annotation YAMLがConfiguration YAMLのdata型を守っているかを確認するCLI application。

  More about [ANOY CLI](about_anoycli_jp.md)

# Annotation YAML(ANOY)について

YAMLのMap型にdata型の概念を導入したものが **Annotation YAML(ANOY)** である。

基本的な文法はYAMLと同じである。

しかし、ANOYではMap型を2種類に分解して扱う。

一つは型確認を行うAnnoMap型であり、もう一つは型確認を行わないFreeMap型である。

## AnnoMap型

特殊なkeyには接頭辞`@`を付ける。これを *annotation key* と呼ぶ。

また、annotation keyに対応する値を *annotation value* と呼ぶ。

*annotaiton key* をkeyとする辞書型を *annotation map (AnnoMap)* 型と呼ぶ。

何回も反復的に使うkeywordは *annotation key* として登録すべきである。

## FreeMap型

逆に接頭辞`@`が付いていないkeyを *free key* と呼ぶ。

*free key* をkeyとする辞書型を *free map(FreeMap)* 型と呼ぶ。

こちらはdata型を指定することはできないため、YAMLのMap型と同様に扱える。

こちらは *annotation key* とは対照的に、ANOYを書く人が自由にkeywordを設定できる。

同じ階層で *annotation key* と *free key* を両方使うのは禁止である。

## Example

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