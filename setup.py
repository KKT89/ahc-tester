import toml
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_NAME = "config.toml"
CONFIG_FILE = os.path.join(SCRIPT_DIR, CONFIG_FILE_NAME)

# 既存の設定ファイルがある場合、上書きするか確認
if os.path.exists(CONFIG_FILE):
    answer = input(f"config.toml already exists. Overwrite? (y/n): ").strip().lower()
    if answer != "y":
        print("Exiting script.")
        exit(0)

# 設定ファイルの内容
config = {
    "paths": {
        "relative_work_dir": "../",  # 作業ディレクトリの相対パス
    },
    "files": {
        "config_file": "config.toml",  # 設定ファイルの名前
        "cpp_file": "main.cpp",  # メインのソースファイル
        "combinined_file": "combined.cpp",  # 結合後のソースファイル
        "sol_file": "solution",  # コンパイルしたプログラムの名前
        "gen_file": "gen", # テストケース生成プログラムの名前
        "vis_file": "vis", # ビジュアライズプログラムの名前
        "tester_file": "tester",  # テスタープログラムの名前
    },
    "build": {
        "compile_options": "-O2",  # コンパイルオプション
    },
    "test": {
        "test_in_dir": "in",  # テストケースの入力ファイルがあるディレクトリ
        "test_out_dir": "out",  # テストケースの出力ファイルを保存するディレクトリ
        "tester_output_score_txt": "Score =",  # テスターの出力からスコアを取得するための文字列
    },
    "parameters": {
        "param_json_file": "params.json",  # パラメータファイルの名前
        "param_cpp_file": "params.cpp",  # パラメータファイルの名前
    },
    "optuna": {
        "work_dir": "optuna_work",  # Optuna 用の作業ディレクトリ
        "db_name": "optuna_study.db",  # Optuna 用のデータベースファイル
    },
    "problem": {
        "pretest_count": 150,  # プレテストの数
        "interactive": False,  # インタラクティブモードか
        "objective": "maximize",  # 最大化 or 最小化
    },
    "max_worker_count": 12,  # 並列実行するテストケースの数
}

# config.toml を作成
with open(CONFIG_FILE, "w") as f:
    toml.dump(config, f)

print(f"{CONFIG_FILE} created successfully!")
