import os
import subprocess
import sys
import tomllib
import concurrent.futures

def load_config():
    # ./config.toml から設定を読み込む
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.toml")

    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} was not found. Please run setup.py first.")
        sys.exit(1)

    with open(CONFIG_FILE, "rb") as f:
        config = tomllib.load(f)

    return config

def compile_program(config):
    WORK_DIR = config["work_dir"]
    CPP_FILE_PATH = os.path.join(WORK_DIR, config["cpp_file"])
    EXE_FILE_PATH = os.path.join(WORK_DIR, config["exe_file"])
    COMPILE_OPTIONS = config["compile_options"]

    cmd = ["g++", CPP_FILE_PATH, COMPILE_OPTIONS, "-o", EXE_FILE_PATH]
    print(f"Building: {config['cpp_file']} -> {config['exe_file']}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        # ビルド失敗
        print("Build failed.")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        sys.exit(1)
    else:
        print("Build succeeded.")

def run_test(config):
    # テストケースの数
    test_case_count = 100

    results = []
    # スレッドプールで並列実行 (max_workers は環境に合わせる)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_test_case, i, config) for i in range(test_case_count)]

        # 処理が終わった順に結果を受け取って表示
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            results.append(res)
            print(f"Test case {res['case']} finished: score_vis = {res['score_vis']}")

    # 合計・平均などを表示
    valid_results = [r for r in results if r["score_vis"] is not None]
    if not valid_results:
        print("No valid scores retrieved.")
        return

    sum_vis = sum(r["score_vis"] for r in valid_results)
    avg_vis = sum_vis / len(valid_results)

    print(f"----- All test cases finished (total {len(valid_results)}) -----")
    print(f"[Visualizer] sum = {sum_vis}, average = {avg_vis:.2f}")

def main():
    # 設定を読み込む
    config = load_config()
    # コンパイル
    compile_program(config)
    # テスト実行
    run_test(config)

if __name__ == "__main__":
    main()