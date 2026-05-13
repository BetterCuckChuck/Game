"""
Hệ thống phát hiện va chạm event-based.

Cung cấp CollisionEvent để mô tả một cặp va chạm có phân loại,
và CollisionDispatcher để phát hiện → phân loại → dispatch sự kiện
đến các handler đã đăng ký.

Tất cả thực thể (thiên thạch, tàu, đĩa bay, đạn) đều được chèn
vào cùng một QuadTree hoặc duyệt brute-force, sau đó phân loại
theo kiểu cặp va chạm.

Last Modified: 2026-05-13
"""

import pygame
from dsa.quadtree import QuadTree


# Hằng số kiểu va chạm
ROCK_ROCK = 'rock_rock'
BULLET_ROCK = 'bullet_rock'
BULLET_SAUCER = 'bullet_saucer'
BULLET_SHIP = 'bullet_ship'
ROCK_SHIP = 'rock_ship'
ROCK_SAUCER = 'rock_saucer'
SAUCER_SHIP = 'saucer_ship'


class CollisionEvent:
    """
    Sự kiện va chạm giữa hai thực thể.

    Attributes:
        event_type: Hằng số kiểu va chạm (ROCK_ROCK, BULLET_ROCK, ...).
        entity_a: Thực thể thứ nhất trong cặp.
        entity_b: Thực thể thứ hai trong cặp.

    Last Modified: 2026-05-13
    """
    __slots__ = ('event_type', 'entity_a', 'entity_b')

    def __init__(self, event_type, entity_a, entity_b):
        """
        Khởi tạo sự kiện va chạm.

        Args:
            event_type: Hằng số kiểu va chạm.
            entity_a: Thực thể thứ nhất.
            entity_b: Thực thể thứ hai.

        Last Modified: 2026-05-13
        """
        self.event_type = event_type
        self.entity_a = entity_a
        self.entity_b = entity_b


class CollisionDispatcher:
    """
    Phát hiện va chạm và dispatch sự kiện đến handler.

    Chèn toàn bộ thực thể vào QuadTree (hoặc list cho brute-force),
    truy vấn candidate cho từng thực thể, phân loại cặp va chạm,
    loại bỏ trùng lặp, rồi gọi handler tương ứng.

    Attributes:
        handlers: Dictionary ánh xạ event_type → callable.
        screen_width: Chiều rộng màn hình (pixel).
        screen_height: Chiều cao màn hình (pixel).

    Last Modified: 2026-05-13
    """

    def __init__(self, screen_width, screen_height):
        """
        Khởi tạo dispatcher với kích thước màn hình.

        Args:
            screen_width: Chiều rộng (pixel).
            screen_height: Chiều cao (pixel).

        Last Modified: 2026-05-13
        """
        self.handlers = {}
        self.screen_width = screen_width
        self.screen_height = screen_height

    def register(self, event_type, handler):
        """
        Đăng ký handler cho một kiểu va chạm.

        Args:
            event_type: Hằng số kiểu va chạm.
            handler: Callable nhận CollisionEvent làm tham số.

        Last Modified: 2026-05-13
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def detect_and_dispatch(self, rocks, ship, saucers, all_bullets,
                            use_quadtree=True, classify_fn=None):
        """
        Phát hiện va chạm và dispatch sự kiện.

        Args:
            rocks: Danh sách thiên thạch.
            ship: Instance Ship người chơi (hoặc None).
            saucers: Danh sách Saucer đang hoạt động.
            all_bullets: Danh sách toàn bộ Bullet đang hoạt động.
            use_quadtree: True dùng QuadTree, False dùng brute-force.
            classify_fn: Hàm phân loại (entity_a, entity_b) → event_type.

        Returns:
            Tuple (quadtree_instance, all_objects) để caller có thể
            tái sử dụng cho range query (cluster multiplier).

        Last Modified: 2026-05-13
        """
        all_objects = list(rocks)
        if ship:
            all_objects.append(ship)
        for s in saucers:
            all_objects.append(s)
        for b in all_bullets:
            all_objects.append(b)

        quadtree = None
        if use_quadtree:
            bounds = pygame.Rect(0, 0, self.screen_width, self.screen_height)
            quadtree = QuadTree(bounds, 4)
            for obj in all_objects:
                quadtree.insert(obj)

        seen_pairs = set()
        events = []

        for obj in all_objects:
            if use_quadtree:
                candidates = quadtree.get_potential_intersections(obj)
            else:
                candidates = all_objects

            for other in candidates:
                if other is obj:
                    continue
                pair_key = (id(obj), id(other)) if id(obj) < id(other) else (id(other), id(obj))
                if pair_key in seen_pairs:
                    continue

                if obj.collidesWith(other):
                    event_type = classify_fn(obj, other) if classify_fn else None
                    if event_type is not None:
                        seen_pairs.add(pair_key)
                        events.append(CollisionEvent(event_type, obj, other))

        for event in events:
            if event.event_type in self.handlers:
                for handler in self.handlers[event.event_type]:
                    handler(event)

        return quadtree, all_objects
