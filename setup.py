import os
import subprocess
import argparse
import tomllib  # Python 3.11+ 標準: 読み込み専用

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_NAME = "config.toml"
CONFIG_FILE = os.path.join(SCRIPT_DIR, CONFIG_FILE_NAME)

DEFAULT_CONFIG = {
    "paths": {
        "relative_work_dir": "../", # 作業ディレクトリの相対パス
        "tools_dir": "tools",       # ツールのディレクトリ
    },
    "files": {
        "config_file": "config.toml",      # 設定ファイルの名前
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
        "param_json_file": "params.json", # パラメータファイルの名前
        "param_cpp_file": "params.cpp", # パラメータファイルの名前
    },
    "optuna": {
        "work_dir": "optuna_work",    # Optuna 用の作業ディレクトリ
        "db_name": "optuna_study.db", # Optuna 用のデータベースファイル
    },
    "problem": {
        "pretest_count": 150,    # プレテストの数（CLIからは変更不可）
        "time_limit_ms": 2000,   # タイムリミット（ミリ秒）。CLI は秒入力、保存は ms。
        "interactive": False,    # インタラクティブかどうか
        "objective": "maximize", # 最大化 or 最小化
    },
}


def _toml_load(path):
    # tomllib はバイナリモードで受け取る
    with open(path, "rb") as f:
        return tomllib.load(f)


def _toml_dump(data, path):
    # シンプルな TOML 書き出し（現在の構造に限定して対応）
    lines = []
    for section, values in data.items():
        lines.append(f"[{section}]\n")
        for k, v in values.items():
            if isinstance(v, bool):
                val = "true" if v else "false"
            elif isinstance(v, (int, float)):
                val = str(v)
            else:
                val = f'"{v}"'
            lines.append(f"{k} = {val}\n")
        lines.append("\n")
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def create_config_file(cfg, config_path):
    _toml_dump(cfg, config_path)
    print(f"{config_path} has been overwritten successfully!\n")


def load_config():
    # ./config.toml から設定を読み込む
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} was not found. Please run setup.py first.")
        return None
    return _toml_load(CONFIG_FILE)


def build_tools_with_cargo(cfg):
    relative_work_dir = cfg["paths"]["relative_work_dir"]
    work_dir = os.path.abspath(os.path.join(SCRIPT_DIR, relative_work_dir))
    tools_dir = cfg["paths"]["tools_dir"]
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
    binary_list = [cfg["files"]["gen_file"], cfg["files"]["vis_file"]]
    if cfg["problem"]["interactive"]:
        binary_list.append(cfg["files"]["tester_file"])
        
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

def _normalize_objective(obj: str) -> str:
    obj = obj.strip().lower()
    if obj in ("max", "maximize"):
        return "maximize"
    if obj in ("min", "minimize"):
        return "minimize"
    raise ValueError("objective must be 'max'/'maximize' or 'min'/'minimize'")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Setup ahc-tester: write config.toml and build tools.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # objective
    parser.add_argument(
        "objective",
        choices=["max", "min", "maximize", "minimize"],
        help="Optimization direction: max/min (maximize/minimize)",
    )

    # TL
    parser.add_argument(
        "tl",
        type=float,
        help="Time limit in seconds",
    )

    # インタラクティブのときだけ -i を付ける（デフォルトは非インタラクティブ）
    parser.add_argument(
        "-i", "--interactive",
        dest="interactive",
        action="store_true",
        default=False,
        help="Problem is interactive (default: non-interactive)",
    )

    return parser.parse_args()


def build_config_from_args(args) -> dict:
    cfg = {**DEFAULT_CONFIG}
    # Deep-copy nested dicts to avoid mutating DEFAULT_CONFIG
    for k, v in DEFAULT_CONFIG.items():
        if isinstance(v, dict):
            cfg[k] = dict(v)
    cfg["problem"]["objective"] = _normalize_objective(args.objective)
    cfg["problem"]["interactive"] = bool(args.interactive)
    if args.tl is None or args.tl <= 0:
        raise ValueError("tl must be a positive number (seconds)")
    # 秒入力をミリ秒整数へ変換して保存
    cfg["problem"]["time_limit_ms"] = int(args.tl * 1000)
    return cfg


def main():
    args = parse_args()
    cfg = build_config_from_args(args)

    # 設定ファイルの作成
    if os.path.exists(CONFIG_FILE):
        answer = input("config.toml already exists. Overwrite? (y/n): ").strip().lower()
        if answer == "y":
            create_config_file(cfg, CONFIG_FILE)
    else:
        create_config_file(cfg, CONFIG_FILE)

    # Cargo を使ってツールをビルド
    build_tools_with_cargo(cfg)


if __name__ == "__main__":
    main()
