import os

# Define what to ignore and what to include
IGNORE_DIRS = {'.venv', '__pycache__', '.git', '.idea', 'node_modules'}
ALLOWED_EXTENSIONS = {'.py', '.txt', '.md', '.json'}
OUTPUT_FILENAME = "project_dump.txt"

def generate_tree(dir_path, prefix=""):
    """Recursively generates a tree structure of the directory."""
    tree_str = ""
    try:
        items = sorted(os.listdir(dir_path))
    except PermissionError:
        return ""
        
    # Filter out ignored directories and the output file itself
    items = [item for item in items if item not in IGNORE_DIRS and item != OUTPUT_FILENAME]

    for i, item in enumerate(items):
        path = os.path.join(dir_path, item)
        is_last = (i == len(items) - 1)
        connector = "└── " if is_last else "├── "
        tree_str += f"{prefix}{connector}{item}\n"

        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            tree_str += generate_tree(path, prefix + extension)
            
    return tree_str

def export_project(root_dir):
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as out_file:
        # 1. Write the Project Tree
        out_file.write("PROJECT STRUCTURE:\n")
        out_file.write("==================\n")
        out_file.write(f"{os.path.basename(os.path.abspath(root_dir))}/\n")
        out_file.write(generate_tree(root_dir))
        out_file.write("\n\n")
        
        # 2. Write the File Contents
        out_file.write("FILE CONTENTS:\n")
        out_file.write("==============\n")

        for root, dirs, files in os.walk(root_dir):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in sorted(files):
                if file == OUTPUT_FILENAME or file == "export_project.py":
                    continue  # Don't export the dump file or the script itself
                    
                if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, root_dir)

                    out_file.write(f"\n\n--- {rel_path} ---\n\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as in_file:
                            out_file.write(in_file.read())
                    except Exception as e:
                        out_file.write(f"[Error reading file: {e}]\n")

if __name__ == "__main__":
    export_project(".")
    print(f"✅ Project successfully exported to {OUTPUT_FILENAME}")