import os
import fnmatch

NUMBER_OF_LINE_CHARS = 100

IGNORE_FILE = ".catignore"


class CatDir:
    def __init__(self, target, recursive, reconstruct=False):
        self.file_tree = {}
        self.target = target
        self.recursive = recursive
        self.reconstruct = reconstruct
        self.ignore_patterns = self.load_ignore_patterns() if not reconstruct else []
        if not reconstruct:
            self.ignore_patterns.append(IGNORE_FILE)

    def load_ignore_patterns(self):
        ignore_file = os.path.join(self.target, IGNORE_FILE)
        ignore_patterns = []

        if os.path.exists(ignore_file):
            try:
                with open(ignore_file, "r") as f:
                    ignore_patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            except Exception as e:
                print(f"Error reading {IGNORE_FILE}: {e}")

        return ignore_patterns

    def should_ignore(self, file_path):
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
        return False

    def create_tree(self):
        self.file_tree = {}

        for root, dirs, files in os.walk(self.target):
            if not self.recursive:
                dirs.clear()

            for filename in files:
                file_path = os.path.join(root, filename)

                if self.should_ignore(file_path):
                    continue

                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        self.file_tree[file_path] = file_content
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

    def render_tree(self):
        # Print the list of files first
        print("#" * NUMBER_OF_LINE_CHARS)
        print("# TREE:")
        print("#" * NUMBER_OF_LINE_CHARS)
        for file_path in self.file_tree.keys():
            print(file_path)

        print("#" * NUMBER_OF_LINE_CHARS)
        print("# FILES")
        print("#" * NUMBER_OF_LINE_CHARS)

        for file_path, content in self.file_tree.items():
            print(f">> File: {file_path}")
            print(f">> Type:", "text" if self.is_text_file(content) else "binary")
            print("-" * NUMBER_OF_LINE_CHARS)
            content = content.decode('utf-8', errors='replace') if self.is_text_file(content) else content
            print(content)
            print("=" * NUMBER_OF_LINE_CHARS)

    def reconstruct_tree(self, input_text):
        lines = input_text.splitlines()
        file_path = None
        file_content = []
        is_text_file = True

        for line in lines:
            if line.startswith(">> File:"):
                # Save the previous file content
                if file_path and file_content:
                    self.write_file(file_path, file_content, is_text_file)

                # Reset for the new file
                file_path = line.split(">> File:")[1].strip()
                file_content = []
            elif line.startswith(">> Type:"):
                is_text_file = "text" in line
            elif line.startswith("-" * NUMBER_OF_LINE_CHARS):
                continue
            elif line.startswith("=" * NUMBER_OF_LINE_CHARS):
                # End of file content
                if file_path and file_content:
                    self.write_file(file_path, file_content, is_text_file)
                file_path = None
                file_content = []
            else:
                file_content.append(line)

    def write_file(self, file_path, content, is_text_file):
        abs_path = os.path.join(self.target, file_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        mode = 'w' if is_text_file else 'wb'
        content = "\n".join(content) if is_text_file else b"\n".join([line.encode() for line in content])

        try:
            with open(abs_path, mode) as f:
                f.write(content)
            print(f"Reconstructed file: {file_path}")
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")

    @staticmethod
    def is_text_file(content):
        try:
            content.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
