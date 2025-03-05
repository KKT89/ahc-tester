import toml
import os

# スクリプトのあるディレクトリ
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# `config.toml` を ahc-tester の一個上のディレクトリに作成
CONFIG_FILE = os.path.join(SCRIPT_DIR, "..", "config.toml")

# 既存の設定ファイルがある場合、上書きするか確認
if os.path.exists(CONFIG_FILE):
    answer = input(f"{CONFIG_FILE} は既に存在します。上書きしますか？ (y/n): ").strip().lower()
    if answer != "y":
        print("スクリプトを終了します。")
        exit(0)

# 設定ファイルの内容
config = {
    "interactive": False,  # インタラクティブモードか
    "objective": "maximize",  # 最大化 or 最小化
    "compile_options": "-O2 -march=native -std=gnu++20",  # コンパイルオプション
}

# `config.toml` を作成
with open(CONFIG_FILE, "w") as f:
    toml.dump(config, f)

print(f"{CONFIG_FILE} を作成しました！")
