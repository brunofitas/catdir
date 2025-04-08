import os
import fnmatch

NUMBER_OF_LINE_CHARS = 100
IGNORE_FILE = ".catignore"


class CatDir:
    def __init__(self, target, recursive, reconstruct=False):
        # Initialize directory traversal settings
        self.file_tree = {}
        self.target = target
        self.recursive = recursive
        self.reconstruct = reconstruct
        self.ignore_patterns = self.load_ignore_patterns() if not reconstruct else []

        # Always ignore the ignore file itself
        if not reconstruct:
            self.ignore_patterns.append(IGNORE_FILE)

    def load_ignore_patterns(self):
        # Load patterns from .catignore
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
        # Determine whether a file or folder should be ignored based on .catignore rules
        rel_path = os.path.relpath(file_path, self.target).replace(os.sep, "/")
        filename = os.path.basename(file_path)

        for pattern in self.ignore_patterns:
            pattern = pattern.strip()
            if not pattern:
                continue

            normalized_pattern = pattern.replace("\\", "/")

            # Ignore folders exactly matching e.g. `.git/`, not `.github/`
            if normalized_pattern.endswith("/"):
                folder = normalized_pattern.rstrip("/")
                path_parts = rel_path.split("/")
                if folder in path_parts:
                    folder_index = path_parts.index(folder)
                    if "/".join(path_parts[:folder_index + 1]) == folder:
                        return True

            # Ignore by extension or exact filename
            if fnmatch.fnmatch(filename, normalized_pattern):
                return True

            # Ignore full relative path match
            if fnmatch.fnmatch(rel_path, normalized_pattern):
                return True

        return False

    def create_tree(self):
        # Walk the directory and populate file_tree with non-ignored files
        self.file_tree = {}

        for root, dirs, files in os.walk(self.target):
            if not self.recursive:
                dirs.clear()

            dirs[:] = [d for d in dirs if not self.should_ignore(os.path.join(root, d))]

            for filename in files:
                file_path = os.path.join(root, filename)

                if self.should_ignore(file_path):
                    continue

                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        rel_path = os.path.relpath(file_path, self.target)
                        self.file_tree[rel_path] = file_content
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

    def render_tree(self):
        # Print the file tree and contents in a structured format
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
        # Parse rendered output and reconstruct the file tree
        lines = input_text.splitlines()
        file_path = None
        file_content = []
        is_text_file = True

        for line in lines:
            if line.startswith(">> File:"):
                if file_path and file_content:
                    self.write_file(file_path, file_content, is_text_file)
                file_path = line.split(">> File:")[1].strip()
                file_content = []
            elif line.startswith(">> Type:"):
                is_text_file = "text" in line
            elif line.startswith("-" * NUMBER_OF_LINE_CHARS):
                continue
            elif line.startswith("=" * NUMBER_OF_LINE_CHARS):
                if file_path and file_content:
                    self.write_file(file_path, file_content, is_text_file)
                file_path = None
                file_content = []
            else:
                file_content.append(line)

    def write_file(self, file_path, content, is_text_file):
        # Write reconstructed file to disk
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
        # Detect whether content is valid UTF-8 text
        try:
            content.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
