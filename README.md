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
設定ファイル `config.toml` の作成と、公式ローカルテストツールのビルドを実行します。

TODO：objective(最大/最小)と、インタラクティブの有無は現在手動でコード書き換える必要があります。
```
$ uv run ahc-tester/setup.py
```

### テストケース作成
以下のコマンドで、L 以上 R 未満のシード値のテストケースを作成します。

```
$ uv run ahc-tester/make_test.py L R
```

### ビルド

```
$ uv run ahc-tester/build.py
```

### ファイル結合

```
$ uv run ahc-tester/combiner.py
```

### パラメータ更新
`update_param.py` の `integer_params` と `float_params` を直接編集する、あまりお作法の良くなさそうな運用を想定しています。以下のコマンドで、ルートディレクトリに `param.cpp` と `param.json` を作成します。

```
$ uv run ahc-tester/update_param.py
```

**オプション**
- `-j`
  - 指定したJSONファイルの内容で、`param.cpp` を作成します。

### テスト実行
以下のコマンドで150ケース分のテストを実行します。TODO：いろいろ作りかけ

```
$ uv run ahc-tester/run_test.py
```

### optuna

以下のコマンドで optuna を使ったパラメータ最適化を実行します。事前にルートディレクトリの `param.json` を最新化する必要があります。

```
$ uv run ahc-tester/optuna_manager.py
```

**オプション**
- `--dir <ディレクトリ>`
  - 指定したディレクトリから最適化を再開します。
- `--last`
  - `optuna_work` 配下で最も新しいサブディレクトリを自動的に選択します。(`--dir` より優先されます)
- `--zero`
  - `n_trials = 0` で実行します。パラメータを即時更新したい時に使います。
