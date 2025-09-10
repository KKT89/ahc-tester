import argparse
import json
import os
import setup
import sys

def make_cpp(param_json, param_cpp_file):
    lines = []
    # 必要なヘッダ
    lines += [
        '#include <string>',
        '#include <sstream>',
        '#include <cstdlib>',
        '',
        '// 自動生成: 環境変数およびCLI引数でパラメータを上書き可能',
        'struct Params {',
    ]

    # 整数パラメータ
    for p in param_json.get("integer_params", []):
        lines.append(f'    int {p["name"]} = {p["value"]};')
    # 浮動小数点パラメータ
    for p in param_json.get("float_params", []):
        lines.append(f'    double {p["name"]} = {p["value"]};')

    lines += [
        '} Params;',
        '',
        '// 環境変数から読み込むユーティリティ',
        'template <typename T>',
        'static T get_env_or(const char* name, T fallback) {',
        '    const char* s = std::getenv(name);',
        '    if (!s) return fallback;',
        '    std::stringstream ss(s);',
        '    T v; ss >> v; return ss.fail() ? fallback : v;',
        '}',
        '',
        '// 起動時に自動で環境変数を反映',
        '#if !defined(ONLINE_JUDGE)',
        'static void loadParamsFromEnv() {',
    ]

    for p in param_json.get("integer_params", []):
        name = p["name"]
        lines.append(f'    Params.{name} = get_env_or<int>("{name}", Params.{name});')
    for p in param_json.get("float_params", []):
        name = p["name"]
        lines.append(f'    Params.{name} = get_env_or<double>("{name}", Params.{name});')

    lines += [
        '}',
        'struct _ParamsEnvAutoload { _ParamsEnvAutoload(){ loadParamsFromEnv(); } } _paramsEnvAutoload;',
        '#endif',
        '',
        '// 互換性のためCLI引数でも上書き可能（既存コード用）',
        'void updateParams(int argc, char* argv[]) {',
        '    for (int i = 1; i + 1 < argc; i += 2) {',
        '        std::string key = argv[i];',
        '        std::string value = argv[i + 1];',
        '        std::istringstream iss(value);'
    ]

    for p in param_json.get("integer_params", []):
        name = p["name"]
        lines.append(f'        if (key == "{name}") {{ iss >> Params.{name}; }}')
    for p in param_json.get("float_params", []):
        name = p["name"]
        lines.append(f'        if (key == "{name}") {{ iss >> Params.{name}; }}')

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
        description="Generate C++ Params header from JSON or defaults."
    )
    parser.add_argument(
        "-j",
        "--json",
        help="JSON parameter file to load.",
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
        json_path = os.path.join(work_dir, config["parameters"]["param_json_file"])
        # ファイルが存在するか確認
        if not os.path.isfile(json_path):
            print(f"Error: params.json not found in current directory: {os.getcwd()}", file=sys.stderr)
            print("Please create params.json or specify path with -j option.", file=sys.stderr)
            sys.exit(1)
        print(f"Using params.json from current directory: {json_path}")
    else:
        # 指定されたパスのJSONファイルを使用
        json_path = args.param_json
        # ファイルが存在するか確認
        if not os.path.isfile(json_path):
            print(f"Error: JSON file not found at specified path: {json_path}", file=sys.stderr)
            sys.exit(1)
        print(f"Using specified JSON file: {json_path}")

    # JSONファイルを読み込む
    try:
        with open(json_path, "r") as jf:
            param_json = json.load(jf)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error: Could not read file {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
        
    # JSONの構造を検証
    if "integer_params" not in param_json or "float_params" not in param_json:
        print(f"Error: JSON file {json_path} must contain 'integer_params' and 'float_params' keys", file=sys.stderr)
        sys.exit(1)

    # C++ 用のパラメータファイルを生成
    make_cpp(param_json, param_cpp_file)


if __name__ == "__main__":
    main()
