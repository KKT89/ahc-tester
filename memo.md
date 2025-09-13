# 環境変数で回す最適化サイクル（記録）

## 背景
- Optuna のハイパーパラメータを「コマンドライン引数」ではなく「環境変数」で注入できるようにする。
- 並列最適化（`n_jobs=-1`）でも干渉しない方法にする。
- オンラインジャッジでは定数埋め込み（`constexpr`）で環境変数無効化。

## 変更概要
- 追加: `hp_params.hpp`
  - `HP_PARAM(type, name, def, lo, hi)` で宣言。
  - ローカル: 環境変数で上書き（範囲チェック＋クランプ）。
  - 本番: `-DONLINE_JUDGE` で `constexpr` 埋め込み。
  - 既定プレフィックス: `HP_`（`-DHP_ENV_PREFIX="..."` で変更可）。
- 更新: `run_test.py`
  - `run_test_case(..., use_env=True, env_prefix=...)` を導入。子プロセスごとに `env` を付与。
- 更新: `optuna_manager.py`
  - 各試行で提案値を環境変数として注入（既定 `HP_`）。
  - SQLite は WAL＋timeout 設定で並列耐性。
- 更新: `update_param.py`
  - 生成する `params.cpp` で環境変数ロードも可能（互換用）。ただし「ヘッダ運用」なら不要。
- 更新: `build.py`
  - `hp_params.hpp` は `lib/heuristic-lib/` に常駐。コピーは行わない設計に変更。
  - `HP_ENV_PREFIX` 環境変数があれば `-DHP_ENV_PREFIX="..."` を自動付与。
  - （互換）`params.json` があれば `params.cpp` を自動再生成。

## C++ 側の使い方
`main.cpp` 先頭付近で:

```cpp
#include "lib/heuristic-lib/hp_params.hpp"

HP_PARAM(int,    ITER,  500,  1,   5000);
HP_PARAM(double, ALPHA, 0.30, 0.0, 1.0);
```

以降は `ITER`, `ALPHA` をそのまま参照。

- 既存 `Params` 構造体が必要ならブリッジ：

```cpp
struct Params { int ITER; double ALPHA; } Params;
static void initParamsFromHP(){ Params.ITER = ITER; Params.ALPHA = ALPHA; }
// main()の早い段階で initParamsFromHP();
```

## Optuna 最適化フロー
1. 探索空間は `params.json`（名前を C++ の `HP_PARAM` 名と一致）。
2. 実行: `python optuna_manager.py`
   - 各試行: `HP_<NAME>=<VAL>` を子プロセスに注入。
3. 並列安全: `subprocess.run(env=...)` により試行間で独立。

## 手動試行の例
- ビルド: `python build.py`
- 実行: `HP_ITER=1200 HP_ALPHA=0.55 ./solution < in/0000.txt > out.txt`

## プレフィックス変更
- ビルド側: `HP_ENV_PREFIX=MY_ python build.py`
- Optuna側: `OPTUNA_PARAM_ENV_PREFIX=MY_ python optuna_manager.py`
- 両者を揃える。

## オンラインジャッジ（定数埋め込み）
- `config.toml` の `build.compile_options` に `-DONLINE_JUDGE` を付与（例: `-O2 -DONLINE_JUDGE`）。

## 既存 `params.cpp` からの移行
- ヘッダ運用へ移行する場合、`params.cpp` / `updateParams(...)` は不要。
- `hp_params.hpp` は `lib/heuristic-lib/` に配置（コピー不要）。
- 段階移行中は併存しても可。ただし重複上書きに注意。

## 補足（DB）
- Optuna ストレージ: SQLite（`?cache=shared&mode=wal` + `timeout`）で並列実行時のロック待ちを緩和。

