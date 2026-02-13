import os

# Các thư mục muốn bỏ qua
IGNORE_DIRS = {"node_modules", "venv", ".git", "__pycache__","uploads","image","extracted"}

def print_tree(start_path=".", prefix="", max_depth=5, current_depth=0):
    if current_depth > max_depth:
        return

    try:
        entries = sorted(os.listdir(start_path))
    except PermissionError:
        return

    entries = [e for e in entries if e not in IGNORE_DIRS]

    for index, entry in enumerate(entries):
        path = os.path.join(start_path, entry)
        is_last = index == len(entries) - 1

        connector = "└── " if is_last else "├── "
        print(prefix + connector + entry)

        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            print_tree(path, prefix + extension, max_depth, current_depth + 1)


if __name__ == "__main__":
    print("```bash")
    print(os.path.basename(os.getcwd()) + "/")
    print_tree(".")
    print("```")
