# 概要

単体test用のdirecoty。

「1つのmoduleを1つのdirectoryでtestする。」というのが現在の設計思想。

こうすることでmoduleの破棄やmoduleの移動に適応しやすくなる。

## 説明

- assertionよりもTrue,Falseの方が分かりやすい。
- Q.なぜmodule単位で設計するのか？
  - 入出力例同士では類似性が高い。
  - module同士では入出力dataが異なるから類似性が低い。
  - 従って、module内にtest.pyを設置するのが最も良いmodule化だと考えた。

- Q.既存systemの何が気に入らないか？
  - 入出力例を編集するにはtest programを直接編集する必要がある。
  - 入出力例を柔軟に変更できないのが気に入らない。
  - debugするspaceが無いのも気に入らない->sandbox.pyの誕生。

## test設計の手順

まずはsandbox directoryやsandbox.pyでmoduleの挙動を確認する。

次にtest directoryとtest.pyでtest用の関数を設計する。

## directory構造

- "testUnit": 単体test用directory。

- "testUnit"/test.py: 全てのmoduleを単体testするprogram.

- "testUnit"/module: module用のdirectory。

- "testUnit"/module/test.py: module内の自動test用program.

- "testUnit"/module/exception.py: module内の例外test用program.

- "testUnit"/module/sandbox.py: moduleの挙動の確認やdebugのために自由に使えるprogram.

- "testUnit"/module/"test": test.pyで使うdirectory。このdirectoryは汚したくない。

- "testUnit"/module/"exception": exception.pyで使うdirectory。

- "testUnit"/module/"sandbox": sandbox.py用のdirectory。

- "testUnit"/module/"test"/example_name: 1つのtest caseを格納するdirectory。input fileとexpected fileを設置することでtestが機能する。

- "testUnit"/module/"test"/example_name/"in": 入力dataを記録するfileやdirectory。example directory内でtesterが直接編集するのはここだけである。

- "testUnit"/module/"test"/example_name/"out": 出力dataを記録するfileやdirectory。test.pyによって自動生成される。testerは結果を閲覧するのみ。

- "testUnit"/module/"test"/example_name/"exp": 期待する出力dataを記録するfileやdirectory。test.pyによって自動生成するべき。


