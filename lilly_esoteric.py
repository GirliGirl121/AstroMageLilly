"""
Lilly's Esoteric Tools — Abjad, Magic Squares, and Traditional Hermetics
"""
from typing import Dict, List, Tuple

ABJAD_MAP = {
    'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6, 'ز': 7, 'ح': 8, 'ط': 9,
    'ي': 10, 'ك': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80, 'ص': 90,
    'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000,
    'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
    'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
    'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400
}


class EsotericCalculator:
    @staticmethod
    def abjad_value(text: str) -> Dict:
        total = 0
        breakdown = []
        for char in text:
            if char in ABJAD_MAP:
                val = ABJAD_MAP[char]
                total += val
                breakdown.append((char, val))
        reduced = total
        while reduced >= 10:
            reduced = sum(int(d) for d in str(reduced))
        return {
            "text": text,
            "total_value": total,
            "reduced_value": reduced,
            "breakdown": breakdown,
            "letter_count": len(breakdown)
        }

    @staticmethod
    def magic_square(n: int) -> Dict:
        if n < 3:
            return {"error": "Magic squares require n >= 3"}
        if n % 2 == 1:
            square = EsotericCalculator._odd_magic_square(n)
        elif n % 4 == 0:
            square = EsotericCalculator._doubly_even_magic_square(n)
        else:
            square = EsotericCalculator._singly_even_magic_square(n)
        magic_constant = n * (n * n + 1) // 2
        return {
            "order": n,
            "magic_constant": magic_constant,
            "square": square,
            "planetary_correspondence": EsotericCalculator._planetary_correspondence(n)
        }

    @staticmethod
    def _odd_magic_square(n: int) -> List[List[int]]:
        square = [[0] * n for _ in range(n)]
        row, col = 0, n // 2
        for num in range(1, n * n + 1):
            square[row][col] = num
            new_row = (row - 1) % n
            new_col = (col + 1) % n
            if square[new_row][new_col]:
                row += 1
            else:
                row, col = new_row, new_col
        return square

    @staticmethod
    def _doubly_even_magic_square(n: int) -> List[List[int]]:
        square = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                square[i][j] = (n * i) + j + 1
        for i in range(n):
            for j in range(n):
                if (i % 4 == j % 4) or ((i % 4 + j % 4) == 3):
                    square[i][j] = n * n + 1 - square[i][j]
        return square

    @staticmethod
    def _singly_even_magic_square(n: int) -> List[List[int]]:
        half = n // 2
        sub_square = EsotericCalculator._odd_magic_square(half)
        square = [[0] * n for _ in range(n)]
        add = [0, 2 * half * half, 3 * half * half, half * half]
        for i in range(half):
            for j in range(half):
                for k in range(4):
                    r = i + (k // 2) * half
                    c = j + (k % 2) * half
                    square[r][c] = sub_square[i][j] + add[k]
        k = (n - 2) // 4
        for i in range(half):
            for j in range(k):
                square[i][j], square[i + half][j] = square[i + half][j], square[i][j]
            for j in range(n - k + 1, n):
                square[i][j], square[i + half][j] = square[i + half][j], square[i][j]
        square[k][0], square[k + half][0] = square[k + half][0], square[k][0]
        square[k][k], square[k + half][k] = square[k + half][k], square[k][k]
        return square

    @staticmethod
    def _planetary_correspondence(n: int) -> str:
        correspondences = {
            3: "Saturn (Agrippa, De Occulta Philosophia, Lib. II, Cap. 22)",
            4: "Jupiter (Agrippa, De Occulta Philosophia, Lib. II, Cap. 22)",
            5: "Mars (Agrippa, De Occulta Philosophia, Lib. II, Cap. 22)",
            6: "Sun (Agrippa, De Occulta Philosophia, Lib. II, Cap. 22)",
            7: "Venus (Agrippa, De Occulta Philosophia, Lib. II, Cap. 22)",
            8: "Mercury (Agrippa, De Occulta Philosophia, Lib. II, Cap. 22)",
            9: "Moon (Agrippa, De Occulta Philosophia, Lib. II, Cap. 22)"
        }
        return correspondences.get(n, "No traditional planetary correspondence recorded")

    @staticmethod
    def format_square(square: List[List[int]]) -> str:
        n = len(square)
        max_width = len(str(n * n))
        lines = []
        for row in square:
            line = " | ".join(f"{num:>{max_width}}" for num in row)
            lines.append(line)
        return "\\n".join(lines)

    @staticmethod
    def numerology_reduce(number: int) -> Dict:
        digital_root = number
        steps = [number]
        while digital_root >= 10:
            digital_root = sum(int(d) for d in str(digital_root))
            steps.append(digital_root)
        master_numbers = [11, 22, 33]
        is_master = number in master_numbers or (len(steps) > 1 and steps[-2] in master_numbers)
        meanings = {
            1: "Initiation, leadership, the Monad",
            2: "Duality, balance, receptivity",
            3: "Expression, creativity, the Triad",
            4: "Structure, foundation, stability",
            5: "Change, freedom, the quintessence",
            6: "Harmony, service, beauty",
            7: "Mystery, introspection, wisdom",
            8: "Power, abundance, karma",
            9: "Completion, compassion, the Ennead",
            11: "Master number — spiritual illumination",
            22: "Master number — master builder",
            33: "Master number — master teacher"
        }
        return {
            "original": number,
            "digital_root": digital_root,
            "steps": steps,
            "is_master_number": is_master,
            "meaning": meanings.get(digital_root, "Beyond conventional enumeration")
        }
