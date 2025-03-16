import os
import subprocess
import sys

def compile_program():
    # このスクリプト (run.py) が存在するディレクトリ
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    # main.cpp は script_dir の 1つ上のディレクトリにあると想定
    MAIN_CPP_PATH = os.path.join(SCRIPT_DIR, "..", "main.cpp")
    MY_PROGRAM_PATH = os.path.join(SCRIPT_DIR, "..", "my_program")

    cmd = ["g++", MAIN_CPP_PATH, "-O2", "-o", MY_PROGRAM_PATH]
    print(f"Building: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        # ビルド失敗
        print("Build failed.")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        sys.exit(1)  # スクリプトを終了
    else:
        print("Build succeeded.")


def main():
    compile_program()


if __name__ == "__main__":
    main()