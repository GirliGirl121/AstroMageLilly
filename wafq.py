#!/usr/bin/env python3
# wafq.py — The Science of Magic Squares (Awfaq)

import math
from typing import List, Dict, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from config import COLORS

console = Console()


class MagicSquare:
    """Generate and analyze Islamic Magic Squares (Wafq)."""
    
    def __init__(self):
        self.planet_squares = {
            "Saturn": 3, "Jupiter": 4, "Mars": 5,
            "Sun": 6, "Venus": 7, "Mercury": 8, "Moon": 9
        }
    
    def generate(self, n: int) -> List[List[int]]:
        """Generate a magic square of order n."""
        if n % 2 == 1:
            return self._odd(n)
        elif n % 4 == 0:
            return self._doubly_even(n)
        else:
            return self._singly_even(n)
    
    def _odd(self, n: int) -> List[List[int]]:
        """Siamese method for odd-order squares."""
        square = [[0] * n for _ in range(n)]
        i, j = 0, n // 2
        
        for num in range(1, n * n + 1):
            square[i][j] = num
            new_i, new_j = (i - 1) % n, (j + 1) % n
            if square[new_i][new_j]:
                i += 1
            else:
                i, j = new_i, new_j
        return square
    
    def _doubly_even(self, n: int) -> List[List[int]]:
        """Method for n divisible by 4."""
        square = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                num = i * n + j + 1
                if (i % 4 == j % 4) or ((i % 4 + j % 4) == 3):
                    square[i][j] = n * n - num + 1
                else:
                    square[i][j] = num
        return square
    
    def _singly_even(self, n: int) -> List[List[int]]:
        """Method for n = 4k + 2."""
        half = n // 2
        sub_square = self._odd(half)
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
                if i != half // 2 or j != 0:
                    square[i][j], square[i + half][j] = \
                        square[i + half][j], square[i][j]
        
        square[half // 2][0], square[half // 2 + half][0] = \
            square[half // 2 + half][0], square[half // 2][0]
        
        for i in range(half):
            for j in range(n - k + 1, n):
                square[i][j], square[i + half][j] = \
                    square[i + half][j], square[i][j]
        
        return square
    
    def get_magic_constant(self, n: int) -> int:
        """Calculate the magic constant for order n."""
        return n * (n * n + 1) // 2
    
    def get_planet_square(self, planet: str) -> Dict:
        """Get the magic square associated with a planet."""
        if planet not in self.planet_squares:
            raise ValueError(f"No traditional square for {planet}")
        
        n = self.planet_squares[planet]
        square = self.generate(n)
        magic_sum = self.get_magic_constant(n)
        
        return {
            "planet": planet,
            "order": n,
            "square": square,
            "magic_constant": magic_sum,
            "total_sum": sum(sum(row) for row in square),
        }
    
    def display_square(self, square_data: Dict):
        """Display a magic square beautifully."""
        n = square_data["order"]
        square = square_data["square"]
        
        table = Table(
            title=f"[bold {COLORS['moon']}]Wafq of {square_data['planet']} "
                  f"(Order {n}) — Magic Constant: {square_data['magic_constant']}[/bold {COLORS['moon']}]",
            show_header=False,
            border_style=COLORS["lilac"],
            padding=(1, 2),
        )
        
        for _ in range(n):
            table.add_column(justify="center")
        
        for row in square:
            table.add_row(*[f"[bold {COLORS['sky']}]{num}[/bold {COLORS['sky']}]" 
                          for num in row])
        
        console.print(table)
    
    def abjad_value(self, text: str) -> int:
        """Calculate Abjad numerological value."""
        abjad_map = {
            'a': 1, 'b': 2, 'j': 3, 'd': 4, 'h': 5, 'w': 6, 'z': 7,
            'h': 8, 't': 9, 'y': 10, 'k': 20, 'l': 30, 'm': 40,
            'n': 50, 's': 60, 'f': 80, 'q': 100, 'r': 200,
            'sh': 300, 't': 400, 'th': 500, 'kh': 600,
            'dh': 700, 'd': 800, 'gh': 1000,
        }
        total = 0
        text = text.lower()
        i = 0
        while i < len(text):
            if i + 1 < len(text) and text[i:i+2] in ['sh', 'th', 'kh', 'dh', 'gh']:
                total += abjad_map.get(text[i:i+2], 0)
                i += 2
            else:
                total += abjad_map.get(text[i], 0)
                i += 1
        return total


wafq = MagicSquare()
