"""
Các hàm tiện ích hình học cho bài toán giao điểm đoạn thẳng.

Cung cấp các hàm tính hệ số góc, tung độ gốc, và xác định
giao điểm giữa hai đoạn thẳng bằng phương pháp giải tích.

Last Modified: 2026-05-06
"""

from pygame import Rect


def calculateGradient(p1, p2):
    """
    Tính hệ số góc (gradient) của đường thẳng đi qua hai điểm.

    Args:
        p1: Điểm thứ nhất, dạng tuple (x, y).
        p2: Điểm thứ hai, dạng tuple (x, y).

    Returns:
        Hệ số góc dạng float, hoặc None nếu đường thẳng đứng.

    Last Modified: 2026-05-06
    """
    if (p1[0] != p2[0]):
        m = (p1[1] - p2[1]) / (p1[0] - p2[0])
        return m
    else:
        return None


def calculateYAxisIntersect(p, m):
    """
    Tính tung độ gốc (y-intercept) của đường thẳng.

    Args:
        p: Một điểm trên đường thẳng, dạng tuple (x, y).
        m: Hệ số góc của đường thẳng.

    Returns:
        Giá trị tung độ gốc (b) dạng float.

    Last Modified: 2026-05-06
    """
    return p[1] - (m * p[0])


def getIntersectPoint(p1, p2, p3, p4):
    """
    Tìm giao điểm của hai đường thẳng kéo dài vô hạn.

    Đường thẳng thứ nhất xác định bởi p1, p2; đường thứ hai bởi p3, p4.
    Xử lý các trường hợp đường thẳng đứng và đường song song.

    Args:
        p1: Điểm đầu đường thẳng 1.
        p2: Điểm cuối đường thẳng 1.
        p3: Điểm đầu đường thẳng 2.
        p4: Điểm cuối đường thẳng 2.

    Returns:
        Tuple chứa tọa độ giao điểm, hoặc None nếu hai đường song song
        và không trùng nhau.

    Last Modified: 2026-05-06
    """
    m1 = calculateGradient(p1, p2)
    m2 = calculateGradient(p3, p4)

    if (m1 != m2):

        if (m1 is not None and m2 is not None):
            b1 = calculateYAxisIntersect(p1, m1)
            b2 = calculateYAxisIntersect(p3, m2)
            x = (b2 - b1) / (m1 - m2)
            y = (m1 * x) + b1
        else:
            if (m1 is None):
                b2 = calculateYAxisIntersect(p3, m2)
                x = p1[0]
                y = (m2 * x) + b2
            elif (m2 is None):
                b1 = calculateYAxisIntersect(p1, m1)
                x = p3[0]
                y = (m1 * x) + b1
            else:
                assert False

        return ((x, y),)
    else:
        b1, b2 = None, None  
        if m1 is not None:
            b1 = calculateYAxisIntersect(p1, m1)

        if m2 is not None:
            b2 = calculateYAxisIntersect(p3, m2)

        if b1 == b2:
            return p1, p2, p3, p4
        else:
            return None


def calculateIntersectPoint(p1, p2, p3, p4):
    """
    Kiểm tra giao điểm có nằm trong phạm vi của hai đoạn thẳng hữu hạn.

    Mở rộng getIntersectPoint bằng cách xác nhận giao điểm tính được
    nằm trong hình chữ nhật bao (bounding rect) của cả hai đoạn thẳng.

    Args:
        p1: Điểm đầu đoạn thẳng 1.
        p2: Điểm cuối đoạn thẳng 1.
        p3: Điểm đầu đoạn thẳng 2.
        p4: Điểm cuối đoạn thẳng 2.

    Returns:
        Giao điểm dạng list [x, y], hoặc None nếu hai đoạn không giao nhau.

    Last Modified: 2026-05-06
    """
    p = getIntersectPoint(p1, p2, p3, p4)

    if p is not None:
        width = p2[0] - p1[0]
        height = p2[1] - p1[1]
        r1 = Rect(p1, (width, height))
        r1.normalize()

        width = p4[0] - p3[0]
        height = p4[1] - p3[1]
        r2 = Rect(p3, (width, height))
        r2.normalize()

        tolerance = 1
        if r1.width < tolerance:
            r1.width = tolerance

        if r1.height < tolerance:
            r1.height = tolerance

        if r2.width < tolerance:
            r2.width = tolerance

        if r2.height < tolerance:
            r2.height = tolerance

        for point in p:
            try:
                res1 = r1.collidepoint(point)
                res2 = r2.collidepoint(point)
                if res1 and res2:
                    point = [int(pp) for pp in point]
                    return point
            except:
                str = "point was invalid  ", point
                print(str)

        return None

    else:
        return None
