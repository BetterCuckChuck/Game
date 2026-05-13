import os
import ast

def get_signature(node):
    if isinstance(node, ast.ClassDef):
        bases = []
        for b in node.bases:
            if isinstance(b, ast.Name):
                bases.append(b.id)
            elif isinstance(b, ast.Attribute):
                bases.append(b.attr)
        base_str = f"({', '.join(bases)})" if bases else ""
        return f"[Class] class {node.name}{base_str}:"
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        args = []
        if hasattr(node.args, 'posonlyargs'):
            for a in node.args.posonlyargs: args.append(a.arg)
        for a in node.args.args: args.append(a.arg)
        if node.args.vararg: args.append('*' + node.args.vararg.arg)
        for a in node.args.kwonlyargs: args.append(a.arg)
        if node.args.kwarg: args.append('**' + node.args.kwarg.arg)
        
        arg_str = ", ".join(args)
        return f"[Function/Method] {prefix} {node.name}({arg_str}):"
    return ""

base_dir = '/home/kali/work/asteroids/src_own'
output_file = os.path.join(base_dir, 'docstrings.txt')

extracted = []

for root, dirs, files in os.walk(base_dir):
    if 'scratch' in root or '__pycache__' in root:
        continue
    for f in sorted(files):
        if f.endswith('.py'):
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, base_dir)
            with open(path, 'r', encoding='utf-8') as file:
                source = file.read()
            
            try:
                tree = ast.parse(source)
            except Exception as e:
                print(f"Skipping {rel_path} due to parse error: {e}")
                continue
            
            extracted.append(f"FILE: {rel_path}\n" + "="*len(f"FILE: {rel_path}") + "\n")
            
            mod_doc = ast.get_docstring(tree)
            if mod_doc:
                extracted.append("[Module]\n" + mod_doc + "\n--------------------\n")
                
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    doc = ast.get_docstring(node)
                    if doc:
                        sig = get_signature(node)
                        extracted.append(f"{sig}\n{doc}\n--------------------\n")
            
            extracted.append("\n")

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("".join(extracted))
    
print(f"Extraction complete! Saved to {output_file}")
