import os
import toml
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_NAME = "config.toml"
CONFIG_FILE = os.path.join(SCRIPT_DIR, CONFIG_FILE_NAME)

config = {
    "paths": {
        "relative_work_dir": "../",  # 作業ディレクトリの相対パス
        "tools_dir": "tools",  # ツールのディレクトリ
    },
    "files": {
        "config_file": CONFIG_FILE_NAME,  # 設定ファイルの名前
        "cpp_file": "main.cpp",        # メインのソースファイル
        "combinined_file": "combined.cpp",  # 結合後のソースファイル
        "sol_file": "solution",        # コンパイルしたプログラムの名前
        "gen_file": "gen",             # テストケース生成プログラムの名前
        "vis_file": "vis",             # ビジュアライズプログラムの名前
        "tester_file": "tester",       # テスタープログラムの名前
    },
    "build": {
        "compile_options": "-O2",  # コンパイルオプション
    },
    "test": {
        "test_in_dir": "in",    # テストケースの入力ファイルがあるディレクトリ
        "test_out_dir": "out",  # テストケースの出力ファイルを保存するディレクトリ
        "tester_output_score_txt": "Score =",  # テスターの出力からスコアを取得するための文字列
    },
    "parameters": {
        "param_json_file": "params.json",  # パラメータファイルの名前
        "param_cpp_file": "params.cpp",      # パラメータファイルの名前
    },
    "optuna": {
        "work_dir": "optuna_work",      # Optuna 用の作業ディレクトリ
        "db_name": "optuna_study.db",   # Optuna 用のデータベースファイル
    },
    "problem": {
        "pretest_count": 150,  # プレテストの数
        "interactive": False,  # インタラクティブモードかどうか
        "objective": "maximize",  # 最大化 or 最小化
    },
    "max_worker_count": 12,  # 並列実行するテストケースの数
}


def create_config_file(config, config_path):
    with open(config_path, "w") as f:
        toml.dump(config, f)
    print(f"{config_path} has been overwritten successfully!")


def build_cargo():
    relative_work_dir = config["paths"]["relative_work_dir"]
    work_dir = os.path.abspath(os.path.join(SCRIPT_DIR, relative_work_dir))
    tools_dir = config["paths"]["tools_dir"]
    tools_path = os.path.join(work_dir, tools_dir)

    cargo_manifest_path = os.path.join(tools_path, "Cargo.toml")    
    cmd = [
        "cargo",
        "build",
        "--manifest-path", cargo_manifest_path,
        "-r",
        "--bin", config["files"]["gen_file"]
    ]
    print("Running Cargo build command ...")
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)
    
    if result.returncode == 0:
        print("Cargo build succeeded.")
        print(result.stdout)
    else:
        print("Cargo build failed.")
        print(result.stderr)


def main():
    # 設定ファイルの作成
    if os.path.exists(CONFIG_FILE):
        answer = input("config.toml already exists. Overwrite? (y/n): ").strip().lower()
        if answer == "y":
            create_config_file(config, CONFIG_FILE)
    else:
        create_config_file(config, CONFIG_FILE)

    build_cargo()
    

if __name__ == "__main__":
    main()