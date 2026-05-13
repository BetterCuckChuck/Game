import re

path = '/home/kali/work/asteroids/src_own/main.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    r'(def displayGameOver\(self, show_reset_prompt=False\):\n\s*""")': 
        r'\1\n        Args:\n            show_reset_prompt: Bật/tắt trạng thái chờ reset.\n',
        
    r'(def _classifyCollision\(self, a, b\):\n\s*""")': 
        r'\1\n        Args:\n            a: Thực thể A.\n            b: Thực thể B.\n',
        
    r'(def _onRockRock\(self, event\):\n\s*""")': 
        r'\1\n        Args:\n            event: Sự kiện va chạm chứa entity_a và entity_b.\n',
        
    r'(def _onBulletRock\(self, event\):\n\s*""")': 
        r'\1\n        Args:\n            event: Sự kiện va chạm.\n',
        
    r'(def _onBulletSaucer\(self, event\):\n\s*""")': 
        r'\1\n        Args:\n            event: Sự kiện va chạm.\n',
        
    r'(def _onBulletShip\(self, event\):\n\s*""")': 
        r'\1\n        Args:\n            event: Sự kiện va chạm.\n',
        
    r'(def _onRockShip\(self, event\):\n\s*""")': 
        r'\1\n        Args:\n            event: Sự kiện va chạm.\n',
        
    r'(def _onRockSaucer\(self, event\):\n\s*""")': 
        r'\1\n        Args:\n            event: Sự kiện va chạm.\n',
        
    r'(def _onSaucerShip\(self, event\):\n\s*""")': 
        r'\1\n        Args:\n            event: Sự kiện va chạm.\n',
        
    r'(def _destroyRock\(self, rock\):\n\s*""")': 
        r'\1\n        Args:\n            rock: Thiên thạch cần phá hủy.\n',
        
    r'(def _getClusterMultiplier\(self, target\):\n\s*""")': 
        r'\1\n        Args:\n            target: Mục tiêu để tính toán.\n        Returns:\n            Hệ số nhân.\n',
        
    r'(def _spawnFloatingText\(self, position, score, multiplier, text=None, color=None\):\n\s*""")': 
        r'\1\n        Args:\n            position: Vị trí xuất hiện.\n            score: Điểm số.\n            multiplier: Hệ số nhân.\n            text: Ký tự tùy chọn.\n            color: Màu sắc tùy chọn.\n'
}

for pattern, replacement in replacements.items():
    content = re.sub(pattern, replacement, content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
