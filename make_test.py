import sys
import os
import tomllib
import subprocess

def load_config():
    # ./config.toml から設定を読み込む
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.toml")

    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} was not found. Please run setup.py first.")
        sys.exit(1)

    with open(CONFIG_FILE, "rb") as f:
        config = tomllib.load(f)

    return config


def main():
    # 引数チェック
    if len(sys.argv) < 3:
        print("Usage: python make_test.py <L> <R>")
        sys.exit(1)

    L = int(sys.argv[1])
    R = int(sys.argv[2])
    if L > R:
        print("L must be less than or equal to R.")
        sys.exit(1)

    # 設定を読み込む
    config = load_config()

    # 1) tmp.txt に L以上R未満の整数を出力
    TMP_FILE = os.path.join(config["script_dir"], "tmp.txt")
    with open(TMP_FILE, "w") as f:
        for x in range(L, R):
            f.write(f"{x}\n")

    # 2) gen.exe を実行して、一時ディレクトリにテストケースを生成
    TMP_DIR = os.path.join(config["script_dir"], "tmp_dir")
    os.makedirs(TMP_DIR, exist_ok=True)  # 一時ディレクトリを用意
    GEN_EXE = os.path.join(config['work_dir'], config["gen_exe_file"])
    cmd = [GEN_EXE, TMP_FILE, f"--dir={TMP_DIR}"]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # 3) 生成したテストケースをリネームして移動
    IN_DIR = os.path.join(config["work_dir"], config["test_in_dir"])
    os.makedirs(IN_DIR, exist_ok=True)
    total_cases = R - L
    for i in range(total_cases):
        src_path = os.path.join(TMP_DIR, f"{i:04d}.txt")
        new_file_name = f"{L + i:05d}.txt"
        dst_path = os.path.join(IN_DIR, new_file_name)
        if os.path.exists(src_path):
            os.rename(src_path, dst_path)

    # 4) 後片付け
    os.remove(TMP_FILE)
    os.rmdir(TMP_DIR)

if __name__ == "__main__":
    main()