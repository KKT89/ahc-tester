# ahc-tester
AtCoder Heuristic Contest (AHC) で使用しているツール群です。

## 使い方

### Python環境
以下はルートディレクトリで実行します。
```
$ uv venv .venv
$ uv pip install -r ahc-tester/requirements.txt
```

### セットアップ
設定ファイル `config.toml` の作成と、公式ローカルテストツールのビルドを実行します。`objective` と TL は必須、インタラクティブは必要なときだけ `-i` を付けます。

```
$ uv run ahc-tester/setup.py {max|min|maximize|minimize} TL-sec [-i]
```

**主な引数**
- `objective`(位置引数): 最適化方向（必須）。`max|min|maximize|minimize` を受け付け、内部的に `maximize|minimize` に正規化します。
- `TL-sec`(位置引数): タイムリミット（秒、必須）。config にはミリ秒整数（`time_limit_ms`）として保存されます。
- `-i, --interactive`: インタラクティブ問題の場合に指定（省略時は非インタラクティブ）。指定時のみ `tester` をビルドします。

**使用例**
- 非インタラクティブ・最大化（TL=2 秒）:
```
$ uv run ahc-tester/setup.py max 2
```
- インタラクティブ・最大化（TL=2.5 秒）:
```
$ uv run ahc-tester/setup.py max 2.5 -i
```
- 非インタラクティブ・最小化（TL=1 秒）:
```
$ uv run ahc-tester/setup.py min 1
```

ヘルプ表示:
```
$ uv run ahc-tester/setup.py --help
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
以下のコマンドで、ルートディレクトリに存在する `params.json` から、`params.cpp` を作成します。

```
$ uv run ahc-tester/update_param.py
```

**オプション**
- `-j, --json`
  - 指定したパスの、JSONファイルに基づいて、`params.cpp` を作成します。

### テスト実行
以下のコマンドでテストを実行します。

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
