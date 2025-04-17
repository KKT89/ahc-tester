import os
import make_param
import setup
import subprocess
import sys

def compile_program(config):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    relative_work_dir = config["paths"]["relative_work_dir"]
    work_dir = os.path.abspath(os.path.join(SCRIPT_DIR, relative_work_dir))
    
    cpp_file_path = os.path.join(work_dir, config["files"]["cpp_file"])
    sol_file_path = os.path.join(work_dir, config["files"]["sol_file"])
    if not os.path.exists(cpp_file_path):
        print(f"Error: {cpp_file_path} was not found.")
        sys.exit(1)

    COMPILE_OPTIONS = config["build"]["compile_options"]
    cmd = ["g++", cpp_file_path, COMPILE_OPTIONS, "-o", sol_file_path]
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
    make_param.main()
    compile_program(config)
