import os
import subprocess
import toml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_NAME = "config.toml"
CONFIG_FILE = os.path.join(SCRIPT_DIR, CONFIG_FILE_NAME)

config = {
    "paths": {
        "relative_work_dir": "../", # 作業ディレクトリの相対パス
        "tools_dir": "tools",       # ツールのディレクトリ
    },
    "files": {
        "config_file": CONFIG_FILE_NAME,   # 設定ファイルの名前
        "cpp_file": "main.cpp",            # メインのソースファイル
        "combined_file": "combined.cpp",   # 結合後のソースファイル
        "sol_file": "solution",            # コンパイルしたプログラムの名前
        "gen_file": "gen",                 # テストケース生成プログラムの名前
        "vis_file": "vis",                 # ビジュアライズプログラムの名前
        "tester_file": "tester",           # テスタープログラムの名前
    },
    "build": {
        "compile_options": "-O2", # コンパイルオプション
    },
    "test": {
        "input_dir": "in",                    # テストケースの入力ファイルがあるディレクトリ
        "output_dir": "out",                  # テストケースの出力ファイルを保存するディレクトリ
        "tester_output_score_txt": "Score =", # テスターの出力からスコアを取得するための文字列
    },
    "parameters": {
        "param_cpp_file": "params.cpp", # パラメータファイルの名前
    },
    "optuna": {
        "work_dir": "optuna_work",    # Optuna 用の作業ディレクトリ
        "db_name": "optuna_study.db", # Optuna 用のデータベースファイル
    },
    "problem": {
        "pretest_count": 150,    # プレテストの数
        "interactive": False,    # インタラクティブモードかどうか
        "objective": "maximize", # 最大化 or 最小化
    },
}


def create_config_file(config, config_path):
    with open(config_path, "w") as f:
        toml.dump(config, f)
    print(f"{config_path} has been overwritten successfully!\n")


def load_config():
    # ./config.toml から設定を読み込む
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} was not found. Please run setup.py first.")
        return None
    with open(CONFIG_FILE, "r") as f:
        return toml.load(f)


def build_tools_with_cargo():
    relative_work_dir = config["paths"]["relative_work_dir"]
    work_dir = os.path.abspath(os.path.join(SCRIPT_DIR, relative_work_dir))
    tools_dir = config["paths"]["tools_dir"]
    tools_path = os.path.join(work_dir, tools_dir)
    cargo_manifest_path = os.path.join(tools_path, "Cargo.toml")

    # cargo_mainfest_path が存在しない場合はエラー
    if not os.path.exists(cargo_manifest_path):
        print(f"Error: {cargo_manifest_path} does not exist.")
        exit(1)
    
    # 最新のコンパイラに更新
    update_cmd = ["rustup", "update"]
    print("Running rustup update ...")
    update_result = subprocess.run(update_cmd, capture_output=True, text=True, cwd=work_dir)
    
    if update_result.returncode == 0:
        print("rustup update succeeded.\n")
    else:
        print("rustup update failed.")
        print(update_result.stderr)
        exit(1)
    
    # 各種ツールをビルド
    binary_list = [config["files"]["gen_file"], config["files"]["vis_file"]]
    if config["problem"]["interactive"]:
        binary_list.append(config["files"]["tester_file"])
        
    # 各バイナリについて cargo build を実行する
    for binary in binary_list:
        cmd = [
            "cargo",
            "build",
            "--manifest-path", cargo_manifest_path,
            "-r",
            "--bin", binary
        ]
        print(f"Running Cargo build command for {binary} ...")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)
    
        if result.returncode == 0:
            print(f"Cargo build succeeded for {binary}.")
            # ビルドしたバイナリを work_dir にコピー
            binary_path = os.path.join(tools_path, "target", "release", binary)
            dest_path = os.path.join(work_dir, binary)
            if os.path.exists(dest_path):
                os.remove(dest_path)
            os.rename(binary_path, dest_path)
            print(f"Copied {binary} to {work_dir}\n")
        else:
            print(f"Cargo build failed for {binary}.")
            print(result.stderr)


def main():
    # 設定ファイルの作成
    if os.path.exists(CONFIG_FILE):
        answer = input("config.toml already exists. Overwrite? (y/n): ").strip().lower()
        if answer == "y":
            create_config_file(config, CONFIG_FILE)
    else:
        create_config_file(config, CONFIG_FILE)

    # Cargo を使ってツールをビルド
    build_tools_with_cargo()
    

if __name__ == "__main__":
    main()