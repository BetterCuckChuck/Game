"""Hệ thống lưu trữ và quản lý bảng điểm cao.

Cung cấp các hàm đọc, ghi, và cập nhật bảng xếp hạng top 10
điểm cao nhất, lưu trữ dưới dạng JSON để duy trì giữa các phiên chơi.

Last Modified: 2026-05-13
"""

import json
import os
from res_path import writable_path

SCORE_FILE = writable_path('highscores.json')
MAX_ENTRIES = 10


def load_scores():
    """Đọc bảng điểm cao từ file JSON.

    Returns:
        Danh sách dict [{"name": str, "score": int}, ...] sắp xếp giảm dần,
        tối đa MAX_ENTRIES phần tử. Trả về danh sách rỗng nếu file chưa tồn tại.

    Last Modified: 2026-05-13
    """
    if not os.path.exists(SCORE_FILE):
        return []
    try:
        with open(SCORE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return sorted(data, key=lambda e: e['score'], reverse=True)[:MAX_ENTRIES]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def reset_scores():
    """Xóa toàn bộ điểm số cao và ghi đè file bằng danh sách rỗng.

    Last Modified: 2026-05-13
    """
    if os.path.exists(SCORE_FILE):
        try:
            os.remove(SCORE_FILE)
        except OSError:
            pass
    save_scores([])


def save_scores(scores):
    """Ghi bảng điểm cao ra file JSON.

    Args:
        scores: Danh sách dict [{"name": str, "score": int}, ...].

    Last Modified: 2026-05-13
    """
    os.makedirs(os.path.dirname(SCORE_FILE), exist_ok=True)
    with open(SCORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, indent=2)


def add_score(score, name="PLAYER"):
    """Thêm điểm mới vào bảng xếp hạng nếu đủ điều kiện.

    Điểm được thêm vào nếu bảng chưa đầy hoặc điểm mới cao hơn
    điểm thấp nhất trong bảng. Bảng luôn được giữ tối đa MAX_ENTRIES.

    Args:
        score: Điểm số cần thêm (int).
        name: Tên người chơi (str). Mặc định "PLAYER".

    Returns:
        Vị trí xếp hạng (1-indexed) nếu được thêm, hoặc None nếu không đủ điều kiện.

    Last Modified: 2026-05-13
    """
    scores = load_scores()
    new_entry = {"name": name, "score": score}

    # Thêm vào danh sách và sắp xếp lại
    scores.append(new_entry)
    scores.sort(key=lambda e: e['score'], reverse=True)
    scores = scores[:MAX_ENTRIES]

    # Kiểm tra xem entry mới có nằm trong top không
    rank = None
    for i, entry in enumerate(scores):
        if entry is new_entry:
            rank = i + 1
            break

    if rank is not None:
        save_scores(scores)

    return rank


def get_top_score():
    """Lấy điểm cao nhất trong bảng.

    Returns:
        Điểm cao nhất (int), hoặc 0 nếu bảng trống.

    Last Modified: 2026-05-13
    """
    scores = load_scores()
    if scores:
        return scores[0]['score']
    return 0


def qualifies(score):
    """Kiểm tra xem điểm số có đủ điều kiện vào bảng top 10 hay không.

    Args:
        score: Điểm số cần kiểm tra (int).

    Returns:
        True nếu điểm đủ điều kiện (bảng chưa đầy hoặc cao hơn điểm thấp nhất).

    Last Modified: 2026-05-13
    """
    if score <= 0:
        return False
    scores = load_scores()
    if len(scores) < MAX_ENTRIES:
        return True
    return score > scores[-1]['score']
