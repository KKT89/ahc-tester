import json
import os
import config as config_module

def generate_param_cpp(json_file, output_file):
    with open(json_file, "r") as f:
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

    lines.append('} Params;')
    lines.append('')

    lines.append('void updateParams(int argc, char* argv[]) {')
    lines.append('    for (int i = 1; i < argc; i += 2) {')
    lines.append('        string key = argv[i];')
    lines.append('        string value = argv[i + 1];')
    lines.append('        istringstream iss(value);')

    for key, info in params.items():
        lines.append(f'        if (key == "{key}") {{')
        lines.append(f'            iss >> Params.{key};')
        lines.append('        }')

    lines.append('    }')
    lines.append('}')

    lines.append('')
    lines.append('#endif // PARAMS_CPP')

    with open(output_file, "w") as f:
        f.write("\n".join(lines))
    
    print(f"Generated: {output_file}")


if __name__ == "__main__":
    config = config_module.load_config()
    WORK_DIR = config["work_dir"]
    JSON_FILE_PATH = os.path.join(WORK_DIR, config["param_json_file"])
    CPP_FILE_PATH = os.path.join(WORK_DIR, config["param_cpp_file"])
    generate_param_cpp(JSON_FILE_PATH, CPP_FILE_PATH)