import os
import subprocess
import sys
import tomllib

def load_config():
    # config.toml から設定を読み込む
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.toml")
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} was not found. Please run setup.py first.")
        sys.exit(1)
    with open(CONFIG_FILE, "rb") as f:
        config = tomllib.load(f)
    return config


def compile_program(config, debug=False):
    WORK_DIR = config["work_dir"]
    CPP_FILE_PATH = os.path.join(WORK_DIR, config["cpp_file"])
    SOL_FILE_PATH = os.path.join(WORK_DIR, config["sol_file"])
    COMPILE_OPTIONS = config["compile_options"]
    if debug:
        SOL_FILE_PATH = os.path.join(WORK_DIR, config["debug_file"])

    cmd = ["g++", CPP_FILE_PATH, COMPILE_OPTIONS, "-o", SOL_FILE_PATH]
    if debug:
        print(f"Building: {config['cpp_file']} -> {config['debug_file']}")
    else:
        print(f"Building: {config['cpp_file']} -> {config['sol_file']}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Build failed.")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        sys.exit(1)
    else:
        print("Build succeeded.")


if __name__ == "__main__":
    # コマンドライン引数をチェックしてデバッグモードかどうか判定
    debug_mode = True
    if len(sys.argv) > 1 and sys.argv[1] in ("-s", "--solve"):
        debug_mode = False

    config = load_config()
    compile_program(config, debug=debug_mode)
