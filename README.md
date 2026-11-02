# Index

- **English Document**

  English Document <- Here

- **Japanese Document**

  [Japanese Document](docs/README_JP.md)

- **Annotation YAML(ANOY)**

  A YAML file that allows type checking for Map types.

  More about [ANOY](about_anoy.md)

- **Configuration YAML(Config YAML)**

  A YAML file that defines the data types usable in Annotation YAML.

  More about [Config YAML](about_config.md)

- **ANOY CLI**
  
  A CLI application that verifies whether Annotation YAML adheres to the data type defined in Configuration YAML.

  More about [ANOY CLI](about_anoycli.md)

# Introduction

YAML maps often become nested and complex.

And these requests have come up.

- Detecting typos in map keys.
- Verifying the data type of map values.
- Ensuring the map's nested structure is appropriate.

This library satisfies these requests.

# Installing

`pip install anoy`

# Usage

library_config.yaml

```
"@Books":
  "@Summary": List the book titles.
  "!Child": "!FreeMap"
"@Author":
  "@Summary": Author of the book.
  "!Child": "!Str"
"@PublishYear":
  "@Summary": The year of the publishment.
  "!Child": "!Int"
"@Country":
  "@Summary": The author's native language.
  "!Child": "!Str"
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

Use the `anoy` command to verify data types.

The following is an example of execution in debug mode.

```
$ anoy library_config.yaml valid_library.yaml -d
open: C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\tests\unused\sampleCase\valid_library.yaml
result: 0/1 invalid.
```

If you mistyped `@Auther` as `@Auther`.

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

When there is an issue with the annotation YAML, `anoy` outputs as follows.

```
$ anoy library_config.yaml library.yaml -d
open: C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\docs\sampleCase\invalid_library.yaml
open: C:\Users\tomot\Backup\sourcecode\python\projects\annotation_yaml\docs\sampleCase\invalid_library.yaml
  keyError at:
    ['@Books', "Alice's Adventures in Wonderland", '@Auther']
result: 1/1 invalid.
```

# Others

## Introduction to sub-specifications

ANOY can define sub-specifications based on the definitions in *config yaml*.

### Object-Oriented Document YAML(OODY)

Object-Oriented Document in YAML, or OODY for short.

This is a document for object-oriented system.

Designed to be independent of any specific programming language.

