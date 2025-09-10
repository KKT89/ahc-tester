import os
import setup
import subprocess
import sys
import json
import shutil

try:
    # params.cpp 自動生成のために利用
    import update_param
except Exception:
    update_param = None

def compile_program(config):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    relative_work_dir = config["paths"]["relative_work_dir"]
    work_dir = os.path.abspath(os.path.join(SCRIPT_DIR, relative_work_dir))
    
    # params.json があればビルド直前に params.cpp を自動再生成（既存互換）
    try:
        param_json_path = os.path.join(work_dir, config["parameters"]["param_json_file"])
        param_cpp_path = os.path.join(work_dir, config["parameters"]["param_cpp_file"])
        if update_param and os.path.isfile(param_json_path):
            with open(param_json_path, "r") as jf:
                param_json = json.load(jf)
            update_param.make_cpp(param_json, param_cpp_path)
    except Exception as e:
        print(f"Warning: failed to (re)generate params.cpp automatically: {e}")

    # hp_params.hpp をワークディレクトリに配置（C++のみで完結運用を補助）
    try:
        header_src = os.path.join(SCRIPT_DIR, "hp_params.hpp")
        if os.path.isfile(header_src):
            shutil.copy(header_src, os.path.join(work_dir, "hp_params.hpp"))
    except Exception as e:
        print(f"Warning: failed to place hp_params.hpp: {e}")

    cpp_file_path = os.path.join(work_dir, config["files"]["cpp_file"])
    sol_file_path = os.path.join(work_dir, config["files"]["sol_file"])
    if not os.path.exists(cpp_file_path):
        print(f"Error: {cpp_file_path} was not found.")
        sys.exit(1)

    COMPILE_OPTIONS = config["build"]["compile_options"]
    # HP_ENV_PREFIX をコンパイル時マクロで設定（未指定なら hp_params.hpp の既定 HP_ を使用）
    hp_prefix = os.environ.get("HP_ENV_PREFIX")
    cmd = ["g++", cpp_file_path, COMPILE_OPTIONS]
    if hp_prefix:
        cmd += [f"-DHP_ENV_PREFIX=\"{hp_prefix}\""]
    cmd += ["-o", sol_file_path]
    print(f"Building: {config["files"]["cpp_file"]} -> {config["files"]['sol_file']}")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)
    if result.returncode != 0:
        print("Build failed.")
        print(result.stderr)
        sys.exit(1)
    else:
        print("Build succeeded.")


if __name__ == "__main__":
    config = setup.load_config()
    compile_program(config)
