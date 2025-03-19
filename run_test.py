import os
import subprocess
import sys
import time
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
    SOL_FILE_PATH = os.path.join(WORK_DIR, config["sol_file"])
    COMPILE_OPTIONS = config["compile_options"]

    cmd = ["g++", CPP_FILE_PATH, COMPILE_OPTIONS, "-o", SOL_FILE_PATH]
    print(f"Building: {config['cpp_file']} -> {config['sol_file']}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        # ビルド失敗
        print("Build failed.")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        sys.exit(1)
    else:
        print("Build succeeded.")


def run_test_case(case_num, config):
    WORK_DIR = config["work_dir"]

    SOLUTION_EXE = os.path.join(WORK_DIR, config["sol_file"])
    VIS_EXE = os.path.join(WORK_DIR, config["vis_exe_file"])

    IN_DIR = os.path.join(WORK_DIR, config["test_in_dir"])
    OUT_DIR = os.path.join(WORK_DIR, config["test_out_dir"])

    case_str = f"{case_num:05d}"
    input_path = os.path.join(IN_DIR, case_str + ".txt")
    output_path = os.path.join(OUT_DIR, case_str + ".txt")

    # 出力ファイルをテストケースごとに分ける
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)

    start_time = time.perf_counter()  # 実行前の時刻を取得

    subprocess.run(
        [SOLUTION_EXE],
        stdin=open(input_path, "r"),
        stdout=open(output_path, "w"),
        stderr=subprocess.DEVNULL,  # stderrは不要なら破棄
        text=True
    )

    end_time = time.perf_counter()  # 実行後の時刻を取得

    elapsed_time = end_time - start_time  # 経過時間を計算
    elapsed_time_ms = elapsed_time * 1000  # ミリ秒に変換

    # vis.exe の実行 (stdout から "Score = XXX" をパース)
    proc_vis = subprocess.run(
        [VIS_EXE, input_path, output_path],
        stdout=subprocess.PIPE,
        text=True
    )

    score = None
    for line in proc_vis.stdout.splitlines():
        line = line.strip()
        if line.startswith("Score ="):
            score = int(line.split("=")[1].strip())
            break

    return {
        "case": case_str,
        "score": score,
        "elapsed_ms": elapsed_time_ms
    }


def run_test(config):
    # テストケースの数
    test_case_count = 100

    # 最大並列数
    max_worker_count = config["max_worker_count"]

    results = []
    # スレッドプールで並列実行
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_worker_count) as executor:
        futures = [executor.submit(run_test_case, i, config) for i in range(test_case_count)]

        # 処理が終わった順に結果を受け取って表示
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            results.append(res)
            print(f"seed:{res['case']}  score:{res['score']:,d}  ({res['elapsed_ms']:.2f} ms)")

    # 合計・平均などを表示
    valid_results = [r for r in results if r["score"] is not None]
    if not valid_results:
        print("No valid scores retrieved.")
        return

    sum_score = sum(r["score"] for r in valid_results)
    avg_score = sum_score / test_case_count

    print(f"----- All test cases finished (total {len(valid_results)}) -----")
    print(f"[Visualizer] sum score = {sum_score:,d}")
    print(f"[Visualizer] average score = {avg_score:.2f}")
    pretest_score = int(sum_score * config["pretest_count"] / test_case_count)
    print(f"[Pretest] estimated score = {pretest_score:,d}")


def main():
    # 設定を読み込む
    config = load_config()
    # コンパイル
    compile_program(config)
    # テスト実行
    run_test(config)


if __name__ == "__main__":
    main()