import sys
import os
import config as config_module
import subprocess
import uuid

def main_with_params(L: int, R: int):
    if L > R:
        print("L must be less than or equal to R.")
        sys.exit(1)

    config = config_module.load_config()
    unique_id = uuid.uuid4().hex

    TMP_FILE = os.path.join(config["script_dir"], f"tmp_{unique_id}.txt")
    with open(TMP_FILE, "w") as f:
        for x in range(L, R):
            f.write(f"{x}\n")

    TMP_DIR = os.path.join(config["script_dir"], f"tmp_dir_{unique_id}")
    os.makedirs(TMP_DIR, exist_ok=True)
    GEN_EXE = os.path.join(config['work_dir'], config["gen_exe_file"])
    cmd = [GEN_EXE, TMP_FILE, f"--dir={TMP_DIR}"]
    subprocess.run(cmd, check=True)

    IN_DIR = os.path.join(config["work_dir"], config["test_in_dir"])
    os.makedirs(IN_DIR, exist_ok=True)
    total_cases = R - L
    for i in range(total_cases):
        src_path = os.path.join(TMP_DIR, f"{i:04d}.txt")
        new_file_name = f"{L + i:05d}.txt"
        dst_path = os.path.join(IN_DIR, new_file_name)
        if os.path.exists(src_path):
            os.rename(src_path, dst_path)

    os.remove(TMP_FILE)
    os.rmdir(TMP_DIR)

def main():
    if len(sys.argv) < 3:
        print("Usage: python make_test.py <L> <R>")
        sys.exit(1)
    L = int(sys.argv[1])
    R = int(sys.argv[2])
    main_with_params(L, R)

if __name__ == "__main__":
    main()
