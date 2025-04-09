# ahc-tester
AtCoder Heuristic Contest (AHC) で使用しているツール群です。

## ディレクトリ構成
以下のディレクトリ構成を想定しています。
```
AHCxxx/                  // ルートディレクトリ
├── ahc-tester/           
├── tools/               // 公式ローカルテストツール
└── main.cpp             // 解答コード
```

## 使い方

### Python環境
Pythonにわかなので全てを間違えている気もします。~~(動いてるからヨシ！)~~

以下のコマンド群は、ルートディレクトリで実行することを想定しています。この設計の時点であまり良くないのかもしれないな。
```
$ uv init
$ uv pip install -r ahc-tester/requirements.txt
```
