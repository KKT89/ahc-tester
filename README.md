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

### セットアップ
設定ファイル(config.toml)の作成と、公式ローカルテストツールのビルドを実行します。

TODO：objective(最大/最小)と、インタラクティブの有無は現在手動でコード書き換える必要があります。
```
$ uv run ahc-tester/setup.py
```

### テストケース作成
以下のコマンドで、L 以上 R 未満のseed値のテストケースを作成します。

```
$ uv run ahc-tester/make_test.py L R
```

### ビルド
```
$ uv run ahc-tester/build.py
```