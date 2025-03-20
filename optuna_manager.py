import argparse
import json
import os
import shutil
import subprocess
import time
import numpy as np
import optuna
import config as config_module
import build
import warnings
from optuna.exceptions import ExperimentalWarning
warnings.filterwarnings("ignore", category=ExperimentalWarning)


def load_param_config(filepath):
    with open(filepath, 'r') as f:
        config_data = json.load(f)
    return config_data


def suggest_parameters(trial, json_data):
    params = {}
    for name, param in json_data.items():
        if param.get("used", False):
            if param["type"] == "float":
                params[name] = trial.suggest_float(name, param["lower"], param["upper"])
            elif param["type"] == "int":
                params[name] = trial.suggest_int(name, param["lower"], param["upper"])
    return params


def run_test(test_number, params, study_dir, config):
    WORK_DIR = config["work_dir"]

    SOLUTION_EXE = os.path.join(study_dir, config["sol_file"])
    VIS_EXE = os.path.join(WORK_DIR, config["vis_exe_file"])

    IN_DIR = os.path.join(WORK_DIR, config["test_in_dir"])
    OUT_DIR = os.path.join(WORK_DIR, config["test_out_dir"])

    case_str = f"{test_number:05d}"
    input_path = os.path.join(IN_DIR, case_str + ".txt")
    output_path = os.path.join(OUT_DIR, case_str + ".txt")

    cmd_cpp = [SOLUTION_EXE] + [str(item) for pair in params.items() for item in pair]
    subprocess.run(
        cmd_cpp,
        stdin=open(input_path, "r"),
        stdout=open(output_path, "w"),
        stderr=subprocess.DEVNULL,
        text=True
    )

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

    return score


def objective(trial, study_dir, config):
    WORK_DIR = config["work_dir"]
    json_file_path = os.path.join(WORK_DIR, config["param_json_file"])
    json_data = load_param_config(json_file_path)
    params = suggest_parameters(trial, json_data)

    all_test_numbers = np.arange(50)
    shuffled_ids = np.random.permutation(all_test_numbers)

    results = []
    for instance_id in shuffled_ids:
        score = run_test(int(instance_id), params, study_dir, config)
        results.append(score)
        trial.report(score, step=int(instance_id))
        if trial.should_prune():
            print(f"Trial pruned at instance {instance_id:04d} with intermediate avg score {sum(results)/len(results):.2f}")
            return sum(results) / len(results)
    avg_score = sum(results) / len(results)
    print(f"Trial finished. Params={params}, avg_score={avg_score:.2f}")
    return avg_score


def main():
    config = config_module.load_config()

    parser = argparse.ArgumentParser(description="Optuna study with parallel trials.")
    parser.add_argument("--dir", type=str, default="", help="Directory to store study results.")
    args = parser.parse_args()

    WORK_DIR = config["work_dir"]
    OPTUNA_WORK_DIR = os.path.join(WORK_DIR, config["optuna_work_dir"])

    if not os.path.exists(OPTUNA_WORK_DIR):
        os.makedirs(OPTUNA_WORK_DIR, exist_ok=True)

    if args.dir:
        study_dir = os.path.join(OPTUNA_WORK_DIR, args.dir)
    else:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        study_dir = os.path.join(OPTUNA_WORK_DIR, f"study_{timestamp}")

    if not os.path.exists(study_dir):
        os.makedirs(study_dir, exist_ok=True)
        print(f"Created a new directory {study_dir}.")
        build.compile_program(config, False)
        SOL_FILE_PATH = os.path.join(WORK_DIR, config["sol_file"])
        shutil.copy(SOL_FILE_PATH, study_dir)

    # DBファイルパス（SQLite）
    db_path = os.path.join(study_dir, config["optuna_db_name"])
    db_url = f"sqlite:///{db_path}"

    # WilcoxonPruner の設定
    pruner = optuna.pruners.WilcoxonPruner(p_threshold=0.1)

    # Optuna study の作成
    study = optuna.create_study(
        study_name=config["optuna_db_name"],
        storage=db_url,
        load_if_exists=True,
        direction=config["objective"],
        pruner=pruner
    )

    max_worker_count = config["max_worker_count"]
    study.optimize(lambda trial: objective(trial, study_dir, config), n_trials=50, n_jobs=max_worker_count)

    print("Best params:", study.best_params)
    print("Best score:", study.best_value)


if __name__ == "__main__":
    main()
