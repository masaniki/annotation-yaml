# For Developers

開発者向けのmessageを記述する。

## 環境構築。

dockerを用いた環境構築。

current directory = project directoryの状態にして、以下のcommandをっ実行する。

```
docker build .
docker run -it <image_ID>
```

## Deploy

### build

`Python -m build .`

### upload

test PyPIへのupload.

`twine upload -r testpypi "dist/*"`

PyPIへのupload

`twine upload "dist/*"`

## Testing

Ubuntu環境で、以下のcommandを実行する。

```
python test_valid_anoy.py
python test_invalid_anoy.py
pytest test_compare.py
```

## Branchs

branch戦略を記述する。

### `master`

現在公開中のbranch。

### `develop`

非破壊的commitのみが許されているbranch。

masterへmergeする。

### `feat/*`

破壊的commitができるbranch。

developへmergeする。

merge後は削除。
