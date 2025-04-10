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
Pythonにわかなので全てを間違えている自信があります。~~(動いてるからヨシ！)~~

以下のコマンド群は、全てルートディレクトリで実行することを想定しています。この設計の時点であまり良くないんだろうなという気はしています。
```
$ uv venv .venv
$ uv pip install -r ahc-tester/requirements.txt
```
