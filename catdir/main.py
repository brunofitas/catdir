#!/usr/bin/env python3

import argparse
import sys
from catdir.catdir import CatDir

def main():
    parser = argparse.ArgumentParser(description="Cat over directory, respecting .catignore or reconstruct from input.")
    parser.add_argument("target", nargs='?', default=".", help="Target directory (default: current directory)")
    parser.add_argument("--recursive", type=str, default="true", help="Recurse into subdirectories (default: true)")
    parser.add_argument("--reconstruct", action="store_true", help="Reconstruct the directory structure from input")

    args = parser.parse_args()
    target = args.target
    recursive = args.recursive.lower() == "true"
    reconstruct = args.reconstruct

    catdir = CatDir(target=target, recursive=recursive, reconstruct=reconstruct)

    if reconstruct:
        input_text = sys.stdin.read()
        catdir.reconstruct_tree(input_text)
    else:
        catdir.create_tree()
        catdir.render_tree()


if __name__ == "__main__":
    main()
