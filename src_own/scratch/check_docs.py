import os
import ast

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return

    issues = []
    
    def check_docstring(doc, name, kind, node=None):
        if not doc:
            issues.append(f"Missing docstring for {kind} {name}")
            return
        
        if "Last Modified:" not in doc:
            issues.append(f"Missing Last Modified in {kind} {name}")
            
        # Check Args/Returns if it's a function
        if kind == "Function/Method" and node:
            args = [a.arg for a in node.args.args if a.arg != 'self']
            if args and "Args:" not in doc:
                issues.append(f"Missing Args section in {kind} {name}")
            
            # Simple check for Returns
            has_return = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node))
            if has_return and "Returns:" not in doc:
                issues.append(f"Missing Returns section in {kind} {name}")
                
    module_doc = ast.get_docstring(tree)
    check_docstring(module_doc, filepath, "Module")
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            check_docstring(ast.get_docstring(node), node.name, "Class")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            check_docstring(ast.get_docstring(node), node.name, "Function/Method", node)
            
    if issues:
        print(f"\nIssues in {filepath}:")
        for i in issues:
            print(" -", i)

base_dir = '/home/kali/work/asteroids/src_own'
for root, dirs, files in os.walk(base_dir):
    if 'scratch' in root or '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            process_file(os.path.join(root, f))
