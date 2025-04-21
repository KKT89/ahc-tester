import argparse
import json
import os
import setup
import sys

# ====================================================================
# === パラメータは以下を編集すること！ ===

# (name, (lower, upper, value), used_in_optuna)
integer_params = [
    ("sample_int", (1, 100, 50), False),
]

# (name, (lower, upper, value), used_in_optuna, log_mode)
float_params = [
    ("sample_float", (1.0, 10.0, 1.5), False, False),
]

# ====================================================================


def make_cpp(param_cpp_file):
    lines = [
        'struct Params {',
    ]

    # 整数パラメータ
    for name, (l, u, v), used in integer_params:
        lines.append(f'    int {name} = {v};')
    # 浮動小数点パラメータ
    for name, (l, u, v), used, log_mode in float_params:
        lines.append(f'    double {name} = {v};')

    lines += [
        '} Params;',
        '',
        'void updateParams(int argc, char* argv[]) {',
        '    for (int i = 1; i < argc; i += 2) {',
        '        std::string key = argv[i];',
        '        std::string value = argv[i + 1];',
        '        std::istringstream iss(value);'
    ]

    # 整数パラメータ
    for name, (l, u, v), used in integer_params:
        lines.append(f'        if (key == "{name}") {{')
        lines.append(f'            iss >> Params.{name};')
        lines.append('        }')
    # 浮動小数点パラメータ
    for name, (l, u, v), used, log_mode in float_params:
        lines.append(f'        if (key == "{name}") {{')
        lines.append(f'            iss >> Params.{name};')
        lines.append('        }')

    lines += [
        '    }',
        '}',
        '',
    ]

    os.makedirs(os.path.dirname(param_cpp_file), exist_ok=True)
    with open(param_cpp_file, "w") as f:
        f.write("\n".join(lines))
    print(f"cpp file generated: {param_cpp_file}")


def main():
    # コマンドライン引数をパース
    parser = argparse.ArgumentParser(
        description="Generate C++ Params header from JSON or defaults"
    )
    parser.add_argument(
        "-j",
        help="JSON parameter file to load",
        dest="param_json",
        default=None
    )
    args = parser.parse_args()

    # 設定読み込み
    config = setup.load_config()
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    relative_work_dir = config["paths"]["relative_work_dir"]
    work_dir = os.path.abspath(os.path.join(SCRIPT_DIR, relative_work_dir))
    param_cpp_file = os.path.join(work_dir, config["parameters"]["param_cpp_file"])

    if args.param_json is None:
        # JSONファイルが指定されていない場合は、新規作成
        param_json = os.path.join(work_dir, config["parameters"]["param_json_file"])
        payload = {
            "integer_params": [
                {"name": n, "lower": l, "upper": u, "value": v, "used": used}
                for n,(l,u,v),used in integer_params
            ],
            "float_params": [
                {"name": n, "lower": l, "upper": u, "value": v, "used": used, "log": log_mode}
                for n,(l,u,v),used,log_mode in float_params
            ]
        }
        os.makedirs(os.path.dirname(param_json), exist_ok=True)
        with open(param_json, "w") as jf:
            json.dump(payload, jf, indent=4)
        print(f"Generated default JSON: {param_json}")
    else:
        # JSONファイルが指定された場合は、読み込み
        param_json = args.param_json
        # JSONファイルの存在確認
        if not os.path.isfile(param_json):
            print(f"Error: JSON file not found: {param_json}", file=sys.stderr)
            sys.exit(1)
        # JSONファイルを読み込み
        with open(args.param_json, "r") as jf:
            payload = json.load(jf)
        integer_params.clear()
        float_params.clear()
        for p in payload["integer_params"]:
            integer_params.append((p["name"], (p["lower"], p["upper"], p["value"]), p["used"]))
        for p in payload["float_params"]:
            float_params.append((p["name"], (p["lower"], p["upper"], p["value"]), p["used"], p["log"]))

    # C++ 用のパラメータファイルを生成
    make_cpp(param_cpp_file)


if __name__ == "__main__":
    main()
