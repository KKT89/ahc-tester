import build
import csv
import datetime
import math
import setup
import subprocess
import time
import os
from concurrent.futures import as_completed
from concurrent.futures import ProcessPoolExecutor

def run_test_case(case_str, input_file, output_file, solution_file, vis_file, score_txt, is_interactive):
    start_time = time.perf_counter()  # 実行前の時刻を取得
    subprocess.run(
        [solution_file],
        stdin=open(input_file, "r"),
        stdout=open(output_file, "w"),
        stderr=subprocess.DEVNULL,  # stderrは不要なら破棄
        text=True
    )
    end_time = time.perf_counter()  # 実行後の時刻を取得

    elapsed_time = end_time - start_time  # 経過時間を計算
    elapsed_time_ms = elapsed_time * 1000  # ミリ秒に変換

    res = subprocess.run(
        [vis_file, input_file, output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )

    score = -1
    for line in res.stdout.splitlines():
        line = line.strip()
        if line.startswith(score_txt):
            score = int(line.split("=")[1].strip())
            break

    return {
        "case": case_str,
        "score": score,
        "elapsed_time": elapsed_time_ms,
    }


def main():
    # コンパイル
    config = setup.load_config()
    build.compile_program(config)

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    relative_work_dir = config["paths"]["relative_work_dir"]
    work_dir = os.path.abspath(os.path.join(SCRIPT_DIR, relative_work_dir))
    input_dir = os.path.join(work_dir, config["test"]["input_dir"])
    output_dir = os.path.join(work_dir, config["test"]["output_dir"])
    solution_file = os.path.join(work_dir, config["files"]["sol_file"])
    vis_file = os.path.join(work_dir, config["files"]["vis_file"])
    score_txt = config["test"]["tester_output_score_txt"]
    is_interactive = config["problem"]["interactive"]

    os.makedirs(output_dir, exist_ok=True)
    
    # テストケースの実行結果
    testcase_count = config["problem"]["pretest_count"]
    wrong_answer_count = 0
    results = []

    with ProcessPoolExecutor(max_workers=None) as executor:
        futures = []
        for i in range(testcase_count):
            case_str = f"{i:04d}"
            input_file = os.path.join(input_dir, case_str + ".txt")
            output_file = os.path.join(output_dir, case_str + ".txt")
            if not os.path.exists(input_file):
                print(f"Error: {input_file} was not found.")
                continue
            # テストケースの実行
            futures.append(executor.submit(run_test_case, case_str, input_file, output_file, solution_file, vis_file, score_txt, is_interactive))

        for future in as_completed(futures):
            result = future.result()
            score = result['score']
            if score <= 0:
                wrong_answer_count += 1
                print(f"Error: {result['case']} failed to get score.")
                continue
            results.append(result)
            print(f"seed:{result['case']}  score:{result['score']:,d}  ({result['elapsed_time']:.2f} ms)")

    if len(results) == 0:
        print("No results to display.")
        exit(0)
    
    # スコアの合計を計算
    total_score = sum(result['score'] for result in results)
    ave_score = total_score / len(results)

    # スコアのlogの合計を計算
    log_score = sum(math.log(result['score']) for result in results)
    ave_log_score = log_score / len(results)

    # 最大実行時間を取得
    max_time_result = max(results, key=lambda r: r['elapsed_time'])
    max_time = max_time_result['elapsed_time']
    max_time_case = max_time_result['case']

    print(f"----- All test cases finished (total {testcase_count}) -----")
    print(f"Wrong Answers: {wrong_answer_count} / {testcase_count}")
    print(f"Maximum Execution Time: {max_time:.2f} ms (case: {max_time_case})")
    print(f"Total Score: {total_score:,d}")
    print(f"Average Log Score: {ave_log_score:.2f}")

    return {
        "wrong_answers": wrong_answer_count,
        "total_score": total_score,
        "ave_log_score": ave_log_score,
    }


if __name__ == "__main__":
    res = main()
    wa_count = res["wrong_answers"]
    total_score = res["total_score"]
    ave_log_score = res["ave_log_score"]

    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file = 'summary.tsv'
    write_header = not os.path.exists(file)

    with open(file, "a", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        if write_header:
            writer.writerow(["Timestamp", "Wrong Answers", "Total Score", "Average Log Score"])
        writer.writerow([now_time, wa_count, total_score, f"{ave_log_score:.2f}"])