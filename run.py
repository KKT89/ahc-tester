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
    GEN_EXE = os.path.join(WORK_DIR, config["gen_exe_file"])
    VIS_EXE = os.path.join(WORK_DIR, config["vis_exe_file"])

    IN_DIR = os.path.join(WORK_DIR, config["test_in_dir"])
    OUT_DIR = os.path.join(WORK_DIR, config["test_out_dir"])

    case_str = f"{case_num:04d}"
    input_path = os.path.join(IN_DIR, case_str + ".txt")
    output_path = os.path.join(OUT_DIR, case_str + ".txt")
    

    # # 出力ファイルをテストケースごとに分ける
    # output_dir = "out"
    # os.makedirs(output_dir, exist_ok=True)

    # # 例: out/0000.txt, out/0001.txt, ...
    # output_path = os.path.join(output_dir, case_str + ".txt")

    # # 1) a.out の実行
    # #    - それぞれ専用の out/xxxx.txt に書き込む
    # subprocess.run(
    #     ["./a.out"],
    #     stdin=open(input_path, "r"),
    #     stdout=open(output_path, "w"),  # 個別ファイルへ出力
    #     stderr=subprocess.DEVNULL,  # stderrは不要なら破棄
    #     text=True
    # )

    # # 2) vis.exe の実行 (stdout から "Score = XXX" をパース)
    # proc_vis = subprocess.run(
    #     ["./vis.exe", input_path, output_path],
    #     stdout=subprocess.PIPE,
    #     text=True
    # )

    # score_vis = None
    # for line in proc_vis.stdout.splitlines():
    #     line = line.strip()
    #     if line.startswith("Score ="):
    #         score_vis = int(line.split("=")[1].strip())
    #         break

    # # 戻り値: テストケース番号とスコア
    # return {
    #     "case": case_str,
    #     "score_vis": score_vis
    # }


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
            print(f"Test case {res['case']} finished: score_vis = {res['score_vis']}")

    # 合計・平均などを表示
    valid_results = [r for r in results if r["score_vis"] is not None]
    if not valid_results:
        print("No valid scores retrieved.")
        return

    sum_vis = sum(r["score_vis"] for r in valid_results)
    avg_vis = sum_vis / test_case_count

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