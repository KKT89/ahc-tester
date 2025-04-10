import toml
import os

# スクリプトのあるディレクトリ
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 作業ディレクトリは1つ上のディレクトリにあると想定
WORK_DIR = os.path.join(SCRIPT_DIR, "..")
# `config.toml` を ahc-tester 内に作成
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.toml")

# 既存の設定ファイルがある場合、上書きするか確認
if os.path.exists(CONFIG_FILE):
    answer = input(f"config.toml already exists. Overwrite? (y/n): ").strip().lower()
    if answer != "y":
        print("Exiting script.")
        exit(0)

# 設定ファイルの内容
config = {
    "script_dir": SCRIPT_DIR,  # スクリプトのあるディレクトリ
    "work_dir": WORK_DIR,  # 作業ディレクトリ
    "cpp_file": "main.cpp",  # メインのソースファイル
    "sol_file": "solution",  # コンパイルしたプログラムの名前
    "combinined_file": "combined.cpp",  # 結合後のソースファイル
    "compile_options": "-O2",  # コンパイルオプション

    "max_worker_count": 12,  # 並列実行するテストケースの数
    "test_in_dir": "in",  # テストケースの入力ファイルがあるディレクトリ
    "test_out_dir": "out",  # テストケースの出力ファイルを保存するディレクトリ
    "gen_exe_file": "gen.exe",  # テストケース生成プログラムの名前
    "vis_exe_file": "vis.exe",  # ビジュアライザの名前
    "tester_output_score_txt": "Score =",  # テスターの出力からスコアを取得するための文字列

    "debug_file": "debug",  # デバッグ用のプログラムの名前
    "param_json_file": "params.json",  # パラメータファイルの名前
    "param_cpp_file": "params.cpp",  # パラメータファイルの名前
    "optuna_work_dir": "optuna_work",  # Optuna 用の作業ディレクトリ
    "optuna_db_name": "optuna_study.db",  # Optuna 用のデータベースファイル

    "pretest_count": 150,  # プレテストの数
    "interactive": False,  # インタラクティブモードか
    "objective": "maximize",  # 最大化 or 最小化
}

# config.toml を作成
with open(CONFIG_FILE, "w") as f:
    toml.dump(config, f)

print(f"{CONFIG_FILE} created successfully!")
