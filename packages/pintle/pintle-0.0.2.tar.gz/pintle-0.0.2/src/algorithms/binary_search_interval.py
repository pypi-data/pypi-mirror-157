import typing as tp

T = tp.TypeVar('T', bound=tp.Container)


def binary_search_interval(intervals: tp.List[T], item: T) -> bool:
    f"""
    The problem is as follows. There are given set of not overlapped intervals {intervals}.
    These intervals are sorted by beginning. Find out if one of intervals contains {item} interval. 
    """
    if not intervals:
        return False

    l_pointer, m_pointer, r_pointer = 0, 0, len(intervals) - 1

    while l_pointer < r_pointer:
        m_pointer = (l_pointer + r_pointer) // 2

        if intervals[m_pointer] < item:
            l_pointer = m_pointer + 1

        elif intervals[m_pointer] > item:
            r_pointer = m_pointer - 1

        else:
            if item in intervals[m_pointer]:
                return True
            return False

    return item in intervals[l_pointer]
