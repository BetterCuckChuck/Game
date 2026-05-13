import os
import re

base_dir = '/home/kali/work/asteroids/src_own'
for root, dirs, files in os.walk(base_dir):
    if 'scratch' in root or '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Replace all Last Modified dates
            updated_content = re.sub(r'Last Modified:\s*\d{4}-\d{2}-\d{2}', 'Last Modified: 2026-05-13', content)
            
            if content != updated_content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
