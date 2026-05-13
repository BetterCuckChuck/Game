"""Tiện ích xác định đường dẫn tài nguyên cho cả môi trường dev và bundled executable.

Khi chạy từ source: trả về đường dẫn tương đối bình thường (../res/).
Khi chạy từ PyInstaller bundle: trả về đường dẫn trong thư mục tạm _MEIPASS.

Highscores là file duy nhất cần ghi, nên được lưu cạnh executable thay vì
bên trong bundle (vì _MEIPASS là read-only).

Last Modified: 2026-05-13
"""

import os
import sys


def _is_bundled():
    """Kiểm tra xem ứng dụng có đang chạy từ PyInstaller bundle không.

    Returns:
        True nếu đang chạy từ bundle, False nếu không.

    Last Modified: 2026-05-13
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def resource_path(relative_path):
    """Trả về đường dẫn tuyệt đối đến file tài nguyên (read-only).

    Args:
        relative_path: Đường dẫn tương đối từ thư mục res/ (ví dụ: 'Hyperspace.otf').

    Returns:
        Đường dẫn tuyệt đối đến file tài nguyên.

    Last Modified: 2026-05-13
    """
    if _is_bundled():
        return os.path.join(sys._MEIPASS, 'res', relative_path)
    return os.path.join(os.path.dirname(__file__), '..', 'res', relative_path)


def writable_path(filename):
    """Trả về đường dẫn ghi được cho file dữ liệu (highscores).

    Khi bundled: lưu cạnh file executable.
    Khi dev: lưu trong ../res/ như cũ.

    Args:
        filename: Tên file (ví dụ: 'highscores.json').

    Returns:
        Đường dẫn tuyệt đối ghi được.

    Last Modified: 2026-05-13
    """
    if _is_bundled():
        return os.path.join(os.path.dirname(sys.executable), filename)
    return os.path.join(os.path.dirname(__file__), '..', 'res', filename)
