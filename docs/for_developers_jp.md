# For Developers

開発者向けのmessageを記述する。


## Next To Do

- [x] logging機能の追加。
- [x] ANOY CLIにmessage modeとexception modeの追加。
- [ ] 列挙型が正しく判定されないbugを直す。
- [x] infomation modeで実行した時に、anoyのfile名が分からない問題の解消。
- [ ] test_invalid_config.pyの追加。

## Ideas


## 環境構築。

dockerを用いた環境構築。

current directory = project directoryの状態にして、以下のcommandを実行する。

```
docker build . -t anoyenv
docker run -it anoyenv
```

## Deploy

### build

`Python -m build .`

### upload

test PyPIへのupload.

`twine upload -r testpypi "dist/*"`

PyPIへのupload

`twine upload "dist/*"`

## Test戦略

Ubuntu環境で、以下のcommandを実行する。

```
python tests/test_valid_anoy.py
python tests/test_invalid_anoy.py
pytest tests/test_compare.py
```

### tests/valid_anoy
- tset_valid_anoy.pyが使用するfileを格納するdirectory.

### tests/valid_anoy/testsuite/in
- tset_valid_anoy.pyが使用するtest_suite.
- 各directoryの中にanoy_fileとconfig_fileが入っている。

### tests/valid_anoy/testsuite/output_log.txt
- tset_valid_anoy.pyの実行結果のログを格納する。

### tests/valid_anoy/testsuite/expected_log.txt
- tset_valid_anoy.pyの期待値のログを格納する。

### tests/invalid_anoy
- tset_invalid_anoy.pyが使用するfileを格納するdirectory.

### tests/invalid_anoy
- tset_invalid_anoy.pyが使用するfileを格納するdirectory.

### tests/invalid_anoy/testsuite/in
- tset_invalid_anoy.pyが使用するtest_suite.
- 各directoryの中にanoy_fileとconfig_fileが入っている。

### tests/invalid_anoy/testsuite/output_log.txt
- tset_valid_anoy.pyの実行結果のログを格納する。

### tests/invalid_anoy/testsuite/expected_log.txt
- tset_valid_anoy.pyの期待値のログを格納する。

### tests/test_valid_anoy.py
- 正しい構文で記述されたanoy_fileとconfig_fileに対して、anoy cliを実行するprogram.
- 全てのcaseで例外が出ないはず。
- 結果はfileに出力する。

### tests/test_invalid_anoy.py
- 正しくない構文で記述されたanoy fileでtestを行うprogram.
- 全てのcaseで例外が出るはず。
- 結果はfileに出力する。

### tests/test_compare_file.py
- test_valid_anoy.pyやtest_valid_anoy.pyを実行した時に、出力されたfileが期待値に等しいか否かを調べるprogam.
- ここのfileの比較の時にpytestを使うことで例外を出す。



## Branch戦略

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
