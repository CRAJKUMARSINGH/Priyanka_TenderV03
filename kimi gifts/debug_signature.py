#!/usr/bin/env python3
"""
debug_signature.py
Scans the repo for calls to generate_scrutiny_sheet_pdf and fixes wrong arity.
"""
import ast
import os
import sys
from typing import List, Tuple

TARGET_METHOD = "generate_scrutiny_sheet_pdf"

class CallVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.hits: List[Tuple[int, ast.Call]] = []

    def visit_Call(self, node: ast.Call) -> None:
        # We only care about obj.method(...)
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == TARGET_METHOD
        ):
            self.hits.append((node.lineno, node))
        self.generic_visit(node)

def scan_file(path: str) -> List[Tuple[int, ast.Call]]:
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    visitor = CallVisitor(path)
    visitor.visit(tree)
    return visitor.hits

def fix_file(path: str, node: ast.Call, lineno: int) -> None:
    """Rewrite the call to have exactly 3 positional args (after self)."""
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Build the new argument string
    new_args = ast.unparse(ast.Call(func=node.func, args=node.args[:3], keywords=[]))
    old_line = lines[lineno - 1].rstrip()
    new_line = old_line.replace(ast.unparse(node), new_args)

    # Optional: ask before applying
    print(f"\n[PATCH] {path}:{lineno}")
    print(f"  OLD: {old_line.strip()}")
    print(f"  NEW: {new_line.strip()}")
    choice = input("Apply patch? [y/n/q] ").strip().lower()
    if choice == "y":
        lines[lineno - 1] = new_line + "\n"
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("  ✓ patched")
    elif choice == "q":
        sys.exit(0)

def main():
    for root, _, files in os.walk("."):
        for file in files:
            if not file.endswith(".py") or file == os.path.basename(__file__):
                continue
            full_path = os.path.join(root, file)
            for lineno, call in scan_file(full_path):
                arg_count = len(call.args)
                if arg_count != 3:  # self, work, bidders, output_path
                    print(
                        f"[ERROR] {full_path}:{lineno} -> "
                        f"{TARGET_METHOD} called with {arg_count} positional args"
                    )
                    fix_file(full_path, call, lineno)

if __name__ == "__main__":
    main()
