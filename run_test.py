import build
import config_util as config_util
import subprocess
import time
import os


def run_test_case(case_str, input_file, output_file, solution_file, vis_file, score_txt):
    cmd_cpp = [solution_file]

    start_time = time.perf_counter()
    subprocess.run(
        cmd_cpp,
        stdin=open(input_file, "r"),
        stdout=open(output_file, "w"),
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    elapsed_time_ms = (time.perf_counter() - start_time) * 1000.0

    res = subprocess.run(
        [vis_file, input_file, output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )

    score = -1
    for line in res.stdout.splitlines():
        line = line.strip()
        if line.startswith(score_txt):
            try:
                score = int(line.split("=")[-1].strip())
            except Exception:
                score = -1
            break

    return {"case": case_str, "score": score, "elapsed_time": elapsed_time_ms}


def main():
    # コンパイル
    config = config_util.load_config()
    build.compile_program(config)

    work_dir = config_util.work_dir()
    input_dir = os.path.join(work_dir, config["test"]["input_dir"])
    output_dir = os.path.join(work_dir, config["test"]["output_dir"])
    solution_file = os.path.join(work_dir, config["files"]["sol_file"])
    vis_file = os.path.join(work_dir, config["files"]["vis_file"])
    score_txt = config["test"]["tester_output_score_txt"]
    # 非インタラクティブ前提の簡易テスト（interactive は参照のみ）
    is_interactive = config["problem"]["interactive"]

    os.makedirs(output_dir, exist_ok=True)
    
    # テストケースの実行結果
    testcase_count = config["problem"]["pretest_count"]
    wrong_answer_count = 0
    results = []

    # シンプルな逐次実行に限定
    for i in range(testcase_count):
        case_str = f"{i:04d}"
        input_file = os.path.join(input_dir, case_str + ".txt")
        output_file = os.path.join(output_dir, case_str + ".txt")
        if not os.path.exists(input_file):
            print(f"Error: {input_file} was not found.")
            continue
        result = run_test_case(
            case_str,
            input_file,
            output_file,
            solution_file,
            vis_file,
            score_txt,
        )
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
    
    # スコアの合計と平均を計算
    total_score = sum(result['score'] for result in results)
    avg_score = total_score / len(results)

    # 最大実行時間を取得
    max_time_result = max(results, key=lambda r: r['elapsed_time'])
    max_time = max_time_result['elapsed_time']
    max_time_case = max_time_result['case']

    print(f"----- All test cases finished (total {testcase_count}) -----")
    print(f"Wrong Answers: {wrong_answer_count} / {testcase_count}")
    print(f"Maximum Execution Time: {max_time:.2f} ms (case: {max_time_case})")
    print(f"Total Score: {total_score:,d}")
    print(f"Average Score: {avg_score:.2f}")

    return {
        "wrong_answers": wrong_answer_count,
        "total_score": total_score,
        "avg_score": avg_score,
    }


if __name__ == "__main__":
    main()
