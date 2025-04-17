import os
import json
import setup

# ====================================================================
# === パラメータは以下を編集すること！ ===

# (name, (lower, upper, value), used_in_optuna)
integer_params = [
    ("sample_int", (1, 100, 50), False),
]

# (name, (lower, upper, value), used_in_optuna, log_mode)
float_params = [
    ("sample_float", (0.1, 10.0, 2.5), False, False),
]

# ====================================================================

def make_json(param_json_file):
    params = {}

    # 整数パラメータを処理
    for name, (lower, upper, value), used in integer_params:
        # 型変換
        lower, upper, value = int(lower), int(upper), int(value)
        # バリデーション
        if lower > upper:
            raise ValueError(f"{name}: lower({lower}) > upper({upper})")
        if not (lower <= value <= upper):
            raise ValueError(f"{name}: value({value}) not in [{lower}, {upper}]")
        # JSON 用オブジェクトに格納
        params[name] = {
            "type":  "int",
            "lower": lower,
            "upper": upper,
            "value": value,
            "used":  used,
            "log":   False, 
        }

    # 浮動小数点パラメータを処理
    for name, (lower, upper, value), used, log_mode in float_params:
        # 型変換
        lower, upper, value = float(lower), float(upper), float(value)
        # バリデーション
        if lower > upper:
            raise ValueError(f"{name}: lower({lower}) > upper({upper})")
        if not (lower <= value <= upper):
            raise ValueError(f"{name}: value({value}) not in [{lower}, {upper}]")
        # JSON 用オブジェクトに格納
        params[name] = {
            "type":  "float",
            "lower": lower,
            "upper": upper,
            "value": value,
            "used":  used,
            "log":   log_mode,
        }

    os.makedirs(os.path.dirname(param_json_file), exist_ok=True)
    with open(param_json_file, "w") as f:
        json.dump(params, f, indent=4)
    print(f"Parameter file generated: {param_json_file}")


def make_cpp(param_json_file, param_cpp_file):
    with open(param_json_file, "r") as f:
        params = json.load(f)

    lines = []
    lines.append('#ifndef PARAMS_CPP')
    lines.append('#define PARAMS_CPP')
    lines.append('')
    lines.append('struct Params {')

    for key, info in params.items():
        if info["type"] == "int":
            lines.append(f'    int {key} = {info["value"]};')
        else:
            lines.append(f'    double {key} = {info["value"]};')

    lines.append('};')
    lines.append('')
    lines.append('void updateParams(int argc, char* argv[]) {')
    lines.append('    for (int i = 1; i < argc; i += 2) {')
    lines.append('        std::string key = argv[i];')
    lines.append('        std::string value = argv[i + 1];')
    lines.append('        std::istringstream iss(value);')

    for key, info in params.items():
        lines.append(f'        if (key == "{key}") {{')
        lines.append(f'            iss >> Params.{key};')
        lines.append('        }')

    lines.append('    }')
    lines.append('}')
    lines.append('')
    lines.append('#endif // PARAMS_CPP')

    os.makedirs(os.path.dirname(param_cpp_file), exist_ok=True)
    with open(param_cpp_file, "w") as f:
        f.write("\n".join(lines))
    print(f"cpp file generated: {param_cpp_file}")


def main():
    config = setup.load_config()

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    relative_work_dir = config["paths"]["relative_work_dir"]
    work_dir = os.path.abspath(os.path.join(SCRIPT_DIR, relative_work_dir))
    param_json_file = os.path.join(work_dir, config["parameters"]["param_json_file"])
    param_cpp_file = os.path.join(work_dir, config["parameters"]["param_cpp_file"])

    # パラメータファイルを生成
    make_json(param_json_file)
    # C++ 用のパラメータファイルを生成
    make_cpp(param_json_file, param_cpp_file)


if __name__ == "__main__":
    main()
