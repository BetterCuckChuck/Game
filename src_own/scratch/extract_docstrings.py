import os
import ast

BASE_DIR = '/home/kali/work/asteroids/src_own'
OUTPUT_FILE = os.path.join(BASE_DIR, 'all_docstrings.txt')

collected = []

for root, dirs, files in os.walk(BASE_DIR):
    if 'scratch' in root:
        continue
    for filename in files:
        if not filename.endswith('.py'):
            continue
        path = os.path.join(root, filename)
        rel_path = os.path.relpath(path, BASE_DIR)
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            print(f'Syntax error in {rel_path}: {e}')
            continue
        # Module docstring
        module_doc = ast.get_docstring(tree)
        if module_doc:
            collected.append(f'FILE: {rel_path}\n' + '-'*len(rel_path) + '\n' + module_doc + '\n\n')
        # Walk classes and functions
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                if doc:
                    kind = 'Class' if isinstance(node, ast.ClassDef) else 'Function'
                    name = node.name
                    header = f'{kind} {name} in {rel_path}'
                    collected.append(header + '\n' + '-'*len(header) + '\n' + doc + '\n\n')
                # Also check methods inside classes
                if isinstance(node, ast.ClassDef):
                    for sub in node.body:
                        if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            doc2 = ast.get_docstring(sub)
                            if doc2:
                                kind2 = 'Method'
                                name2 = sub.name
                                header2 = f'{kind2} {name}.{name2} in {rel_path}'
                                collected.append(header2 + '\n' + '-'*len(header2) + '\n' + doc2 + '\n\n')
        
with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
    out.write('\n'.join(collected))

print(f'Extracted docstrings to {OUTPUT_FILE}')
