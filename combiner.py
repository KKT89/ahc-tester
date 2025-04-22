import os
import sys
import re
import setup

def read_file_content(file_name: str) -> str:
    with open(file_name, "r") as f:
        return f.read()

def make_converted_file_content(
        file_path: str,
        stack: list[str],
        added_files: set[str]) -> str:
    
    content = read_file_content(file_path)
    lines = content.splitlines()
    output_lines: list[str] = []
    base_dir = os.path.dirname(file_path)

    for line in lines:
        stripped = line.strip()
        # Skip include guards and endif
        if (stripped.startswith('#pragma once') or
            stripped.startswith('#ifndef') or
            stripped.startswith('#define') or
            stripped.startswith('#endif')):
            continue

        include_match = re.match(r'^\s*#include\s+"(.+)"\s*$', line)
        if include_match:
            include_name = include_match.group(1)
            include_path = os.path.normpath(os.path.join(base_dir, include_name))
            if include_path not in added_files:
                if include_path in stack:
                    print("Circular dependency detected: " + " > ".join(stack + [include_path]))
                    sys.exit(1)
                # separator comment with filename
                output_lines.append(f"// ── {os.path.basename(include_path)} ──")
                stack.append(include_path)
                inlined = make_converted_file_content(include_path, stack, added_files)
                output_lines.extend(inlined.splitlines())
                added_files.add(include_path)
                stack.pop()
            # skip if already added
        else:
            output_lines.append(line)

    return "\n".join(output_lines)


def main():
    config = setup.load_config()

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    relative_work_dir = config["paths"]["relative_work_dir"]
    work_dir = os.path.abspath(os.path.join(SCRIPT_DIR, relative_work_dir))
    cpp_file_path = os.path.join(work_dir, config["files"]["cpp_file"])
    combined_file_path = os.path.join(work_dir, config["files"]["combined_file"])

    converted_content = make_converted_file_content(cpp_file_path, [cpp_file_path], set())
    with open(combined_file_path, "w") as f:
        f.write(converted_content)
    print(f"Combined file generated: {combined_file_path}")


if __name__ == "__main__":
    main()
