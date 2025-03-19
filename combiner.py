import os
import sys
import re
import config as config_module

def read_file_content(file_name: str) -> str:
    with open(file_name, "r") as f:
        return f.read()


# def make_converted_file_content(
#         file_name: str,
#         stack: list[str],
#         added_file_names: set) -> str:
#     content = read_file_content(file_name)
#     content_lines = content.splitlines()
#     for i, line in enumerate(content_lines):
#         match = re.match(r'^\s*#include\s+"(.*)"\s*$', line)
#         if match:
#             include_file = match.group(1)
#             if include_file not in added_file_names:
#                 if include_file in stack:
#                     print("Circular dependency detected: " + " > ".join(stack + [include_file]))
#                     sys.exit(1)
#                 stack.append(include_file)
#                 included_content = make_converted_file_content(include_file, stack, added_file_names)
#                 content_lines[i] = included_content
#                 added_file_names.add(include_file)
#                 stack.pop()
#             else:
#                 # 既に読み込んだファイルはスキップ
#                 content_lines[i] = ""
#     return "\n".join(content_lines)


def main():
    config = config_module.load_config()

    WORK_DIR = config["work_dir"]
    CPP_FILE_PATH = os.path.join(WORK_DIR, config["cpp_file"])
    COMBINED_FILE_PATH = os.path.join(WORK_DIR, config["combinined_file"])
    
    # converted_content = make_converted_file_content(CPP_FILE_PATH, [CPP_FILE_PATH], set())
    # with open(COMBINED_FILE_PATH, "w") as f:
    #     f.write(converted_content)
    # print(f"Combined file generated: {COMBINED_FILE_PATH}")


if __name__ == "__main__":
    main()
