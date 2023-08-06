import seaborn as sns
import typing as tp


def generate_colors(n: int, style: str = "pastel") -> tp.List[str]:
    """
    Generate random n colors
    """
    return sns.color_palette(style, n)


__all__ = ['generate_colors']