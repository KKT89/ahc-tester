import argparse
import build
import json
import numpy as np
import os
import optuna
import run_test
import config_util as config_util
import shutil
import sys
import time
import uuid
import warnings
from optuna.storages import RDBStorage
from optuna.exceptions import ExperimentalWarning

warnings.filterwarnings("ignore", category=ExperimentalWarning)


def suggest_parameters(trial, json_file):
    with open(json_file, "r") as f:
        data = json.load(f)

    params = {}
    # 整数パラメータ
    for p in data.get("integer_params", []):
        if p.get("used", False):
            name = p["name"]
            low, high = p["lower"], p["upper"]
            params[name] = trial.suggest_int(name, low, high)

    # 浮動小数点パラメータ
    for p in data.get("float_params", []):
        if p.get("used", False):
            name = p["name"]
            low, high = p["lower"], p["upper"]
            log = p.get("log", False)
            params[name] = trial.suggest_float(name, low, high, log=log)

    return params


def objective(trial, input_dir, output_dir, sol_file, vis_file, score_txt, is_interactive, param_json_file, env_prefix=None):
    params = suggest_parameters(trial, param_json_file)

    # 固定順序（Prunerの影響を安定化）: 環境変数 OPTUNA_OBJECTIVE_SEED で制御
    seed_env = os.environ.get("OPTUNA_OBJECTIVE_SEED")
    if seed_env is not None:
        try:
            seed_val = int(seed_env)
        except Exception:
            seed_val = 0
        rng = np.random.default_rng(seed_val)
        shuffled_ids = rng.permutation(np.arange(50))
    else:
        all_test_numbers = np.arange(50)
        shuffled_ids = np.random.permutation(all_test_numbers)

    results = []
    for instance_id in shuffled_ids:
        case_str = f"{instance_id:04d}"
        input_file = os.path.join(input_dir, case_str + ".txt")
        uid = uuid.uuid4().hex[:8]
        output_file = os.path.join(output_dir, uid + ".txt")
        if not os.path.exists(input_file):
            print(f"Error: {input_file} was not found.")
            exit(1)
        
        # Optuna の各試行で得たパラメータを環境変数として子プロセスへ注入
        res = run_test.run_test_case(
            case_str,
            input_file,
            output_file,
            sol_file,
            vis_file,
            score_txt,
            is_interactive,
            params,
            cleanup=True,
            use_env=True,
            env_prefix=env_prefix,
        )
        score = res['score']
        if score <= 0:
            results.append(-1)
        else:
            results.append(score)
        trial.report(score, step=int(instance_id))
        if trial.should_prune():
            print(f"Trial pruned at instance {instance_id:04d} with intermediate avg score {sum(results) / len(results):.2f}")
            return sum(results) / len(results)
    avg_score = sum(results) / len(results)
    print(f"Trial finished. Params={params}, avg_score={avg_score:.2f}")
    return avg_score


def main():
    # コマンドライン引数をパース
    parser = argparse.ArgumentParser(
        description="Optuna study with parallel trials."
    )
    parser.add_argument(
        "--dir",
        help="Directory to store study results.",
        dest="dir",
        default=None
    )
    parser.add_argument(
        "--last",
        help="Use the most recent study directory under optuna work dir.",
        action="store_true",
        dest="last"
    )
    parser.add_argument(
        "--zero",
        help="Run with n_trials = 0 (skip optimization).",
        action="store_true",
        dest="zero"
    )
    args = parser.parse_args()

    # 設定読み込み
    config = config_util.load_config()
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    relative_work_dir = config["paths"]["relative_work_dir"]
    work_dir = os.path.abspath(os.path.join(SCRIPT_DIR, relative_work_dir))
    optuna_work_dir = os.path.join(work_dir, config["optuna"]["work_dir"])

    if not os.path.exists(optuna_work_dir):
        os.makedirs(optuna_work_dir, exist_ok=True)

    if args.last:
        # optuna_work_dir 配下のサブディレクトリを辞書順でソートして最新を取得
        subs = [d for d in os.listdir(optuna_work_dir) if os.path.isdir(os.path.join(optuna_work_dir, d))]
        if not subs:
            print(f"Error: no study directories found in {optuna_work_dir}", file=sys.stderr)
            sys.exit(1)
        lastest = sorted(subs)[-1]
        study_dir = os.path.join(optuna_work_dir, lastest)
    elif args.dir:
        study_dir = args.dir
    else:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        study_dir = os.path.join(optuna_work_dir, f"study_{timestamp}")

    if not os.path.exists(study_dir):
        build.compile_program(config)
        cpp_file = os.path.join(work_dir, config["files"]["cpp_file"])
        sol_file = os.path.join(work_dir, config["files"]["sol_file"])
        param_cpp_file = os.path.join(work_dir, config["parameters"]["param_cpp_file"])
        param_json_file = os.path.join(work_dir, config["parameters"]["param_json_file"])

        if not os.path.isfile(param_json_file):
            print(f"Error: JSON file not found: {param_json_file}", file=sys.stderr)
            sys.exit(1)
        if not os.path.isfile(param_cpp_file):
            print(f"Error: C++ file not found: {param_cpp_file}", file=sys.stderr)
            sys.exit(1)

        os.makedirs(study_dir, exist_ok=True)
        print(f"Created a new directory {study_dir}.")
        shutil.copy(cpp_file, study_dir)
        shutil.copy(sol_file, study_dir)
        shutil.copy(param_cpp_file, study_dir)
        shutil.copy(param_json_file, study_dir)

    input_dir = os.path.join(work_dir, config["test"]["input_dir"])
    output_dir = study_dir
    sol_file = os.path.join(study_dir, config["files"]["sol_file"])
    vis_file = os.path.join(work_dir, config["files"]["vis_file"])
    score_txt = config["test"]["tester_output_score_txt"]
    is_interactive = config["problem"]["interactive"]
    param_json_file = os.path.join(study_dir, config["parameters"]["param_json_file"])

    # DBファイルパス（SQLite）
    db_path = os.path.join(study_dir, config["optuna"]["db_name"])
    db_url = f"sqlite:///{db_path}?cache=shared&mode=wal"

    # WilcoxonPruner の設定
    pruner = optuna.pruners.WilcoxonPruner(p_threshold=0.1)

    # SQLite ストレージの作成
    storage = RDBStorage(
        url=db_url,
        engine_kwargs={
            "connect_args": {
                # ロック待ちを最大20秒まで許容
                "timeout": 20.0,
            }
        },
    )

    # Optuna study の作成
    study = optuna.create_study(
        study_name=config["optuna"]["db_name"],
        storage=storage,
        load_if_exists=True,
        direction=config["problem"]["objective"],
        pruner=pruner,
    )

    n_trials = 500
    if args.zero:
        n_trials = 0

    # 必要なら環境変数名にプレフィックスを付けたい場合はここで設定（例: "HP_")
    # 既定はヘッダのデフォルトに合わせて HP_
    env_prefix = os.environ.get("OPTUNA_PARAM_ENV_PREFIX", "HP_")

    # 並列度は環境変数 OPTUNA_N_JOBS で上書き可能（デフォルト: -1 = 最大）
    n_jobs_env = os.environ.get("OPTUNA_N_JOBS")
    try:
        n_jobs = int(n_jobs_env) if n_jobs_env is not None else -1
    except Exception:
        n_jobs = -1

    study.optimize(
        lambda trial: objective(trial, input_dir, output_dir, sol_file, vis_file, score_txt, is_interactive, param_json_file, env_prefix=env_prefix),
        n_trials=n_trials,
        n_jobs=n_jobs,
    )

    # 最終ベストパラメータで study_dir の JSON の "value" を更新し、ルートの params.json にも反映
    best = study.best_params
    best_score = study.best_value

    def _apply_best_to_json(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in ("integer_params", "float_params"):
            for p in data.get(key, []):
                name = p.get("name")
                if p.get("used") and name in best:
                    p["value"] = best[name]
        data["best_score"] = best_score
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # study ディレクトリ側
    _apply_best_to_json(param_json_file)
    print(f"[Done] Updated {param_json_file} with best params: {best}")

    # ルート側
    root_param_json = os.path.join(work_dir, config["parameters"]["param_json_file"])
    if os.path.isfile(root_param_json):
        _apply_best_to_json(root_param_json)
        print(f"[Done] Also updated {root_param_json} with best params.")

    print("Best params:", study.best_params)
    print("Best score:", study.best_value)


if __name__ == "__main__":
    main()
