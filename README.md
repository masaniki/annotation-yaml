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

## Package Dependencies

The following packages may not work properly if they are not installed:

- [PyYAML](https://pypi.org/project/PyYAML/): Most popular YAML parser for Python.

# Usage

library_config.yaml

```
"@Books":
  "@Summary": List the book titles.
  "!ChildValue": FreeDict
"@Author":
  "@Summary": Author of the book.
  "!ChildValue": Str
"@PublishYear":
  "@Summary": The year of the publishment.
  "!ChildValue": Int
"@Country":
  "@Summary": The author's native language.
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

Use the `anoy` command to verify data types.

If data type issues are not found, it outputs nothing.

```
>>> anoy library_config.yaml library.yaml
>>> 
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
>>> anoy library_config.yaml library.yaml
>>> Traceback (most recent call last):
    ... (omission) ...
    src.anoyModule.anoyErrors.ConfigurationYamlError: `@Auther` is not defined.
```
# For Developers

## Testing

This project uses `pytest`.

If you want to test, put in following command.

`pytest tests\unit\test_dictTraversal.py`

## Next To Do

- [ ] test caseを全てのdata型に拡大。
- [ ] `!Float`のtest.
- [ ] `!AnnoMap`のtest.
- [ ] `!FreeMap`のtest.

## Ideas


