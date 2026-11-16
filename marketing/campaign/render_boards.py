#!/usr/bin/env python3
"""Render version-neutral workflow diagrams from shapes, without changing the cover."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

W, H = 960, 540
ASSETS = Path(__file__).resolve().parents[2] / "assets/marketing/current"
INK = "#071921"
PANEL = "#102c36"
FRAME = "#315562"
SOFT = "#8cafb8"
PAPER = "#fff0cd"
TEAL = "#58e6d3"
GOLD = "#ffce6d"
CORAL = "#ff8278"


class Board:
    def __init__(self, accent=TEAL):
        self.image = Image.new("RGB", (W, H), INK)
        self.draw = ImageDraw.Draw(self.image)
        for y in range(H):
            self.draw.line((0, y, W, y), fill=(7 + y // 150, 25 + y // 68, 33 + y // 67))
        self.accent = accent
        self.draw.line((52, 66, 155, 66), fill=accent, width=4)
        self.draw.line((805, 476, 908, 476), fill=accent, width=4)
        self.draw.line((52, 476, 771, 476), fill=FRAME, width=1)

    def panel(self, box, *, stroke=FRAME, fill=PANEL, radius=19):
        self.draw.rounded_rectangle(box, radius=radius, fill=fill, outline=stroke, width=2)

    def line(self, points, color=SOFT, width=4):
        self.draw.line(points, fill=color, width=width, joint="curve")

    def dot(self, x, y, radius=9, color=TEAL, fill=None):
        self.draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill or color,
                          outline=color, width=2)

    def bars(self, x, y, lengths, color=SOFT):
        for i, length in enumerate(lengths):
            self.line((x, y + 13 * i, x + length, y + 13 * i), color, 3)

    def arrow(self, x, y, target, color=None):
        color = color or self.accent
        self.line((x, y, target, y), color, 3)
        self.line((target - 14, y - 9, target, y, target - 14, y + 9), color, 3)

    def mark(self, x, y, kind, color=None):
        color = color or self.accent
        d = self.draw
        if kind == "check":
            self.line((x - 11, y, x - 3, y + 8, x + 13, y - 10), color, 4)
        elif kind == "alert":
            d.polygon([(x, y - 17), (x + 16, y + 13), (x - 16, y + 13)], outline=color, width=3)
            self.line((x, y - 6, x, y + 3), color, 3)
            self.dot(x, y + 8, 2, color)
        elif kind == "file":
            self.line((x - 15, y - 19, x + 5, y - 19, x + 15, y - 9, x + 15, y + 19,
                       x - 15, y + 19, x - 15, y - 19), color, 3)
            self.line((x + 5, y - 19, x + 5, y - 9, x + 15, y - 9), color, 2)
            self.bars(x - 8, y + 1, (15, 12), color)
        elif kind == "lock":
            d.arc((x - 9, y - 17, x + 9, y + 2), 180, 360, fill=color, width=3)
            self.panel((x - 14, y - 4, x + 14, y + 13), stroke=color, radius=4)
            self.dot(x, y + 4, 2, color)
        elif kind == "search":
            self.dot(x - 4, y - 4, 11, color, PANEL)
            self.line((x + 4, y + 4, x + 15, y + 15), color, 4)
        elif kind == "person":
            self.dot(x, y - 7, 6, color)
            d.arc((x - 14, y + 1, x + 14, y + 25), 185, 355, fill=color, width=3)
        elif kind == "play":
            d.polygon([(x - 10, y - 14), (x + 13, y), (x - 10, y + 14)], fill=color)
        else:
            self.dot(x, y, 12, color, PANEL)
            self.dot(x, y, 4, color)

    def card(self, x, y, width, kind, color=None, lines=(92, 68, 80)):
        color = color or self.accent
        self.panel((x, y, x + width, y + 98))
        self.mark(x + 30, y + 49, kind, color)
        self.bars(x + 57, y + 36, lines)

    def map(self, bounds):
        x, y, width, height = bounds
        self.panel((x, y, x + width, y + height), fill="#102f3b")
        d = self.draw
        for points in (
            [(0.06, 0.21), (0.25, 0.12), (0.35, 0.25), (0.18, 0.32), (0.08, 0.52)],
            [(0.39, 0.15), (0.75, 0.16), (0.91, 0.36), (0.78, 0.51), (0.92, 0.67),
             (0.69, 0.81), (0.49, 0.67), (0.29, 0.81), (0.13, 0.65), (0.29, 0.50)],
            [(0.12, 0.79), (0.31, 0.86), (0.40, 0.93), (0.09, 0.92)],
        ):
            d.polygon([(x + int(a * width), y + int(b * height)) for a, b in points], fill="#214951")
        a = (x + width // 5, y + height // 2)
        b = (x + width * 4 // 5, y + height // 3)
        via = (x + width // 2, y + height // 4)
        fallback = (x + width // 2, y + height * 3 // 4)
        self.line([a, via, b], CORAL, 3)
        self.line([a, fallback, b], TEAL, 4)
        for px, py in (a, b, fallback):
            self.dot(px, py)
        self.mark(*via, "alert", CORAL)


def product():
    b = Board()
    b.panel((85, 108, 318, 431), stroke=TEAL, fill="#091e28", radius=33)
    b.line((157, 128, 245, 128), SOFT, 3)
    for j, color in enumerate((TEAL, SOFT, GOLD)):
        b.dot(113, 180 + 33 * j, 7, color)
        b.bars(130, 174 + 33 * j, (112, 82))
    b.map((106, 268, 191, 120))
    b.arrow(334, 267, 398)
    b.panel((410, 109, 875, 430), fill="#091e28")
    b.card(435, 137, 193, "file", lines=(91, 64, 73))
    b.card(652, 137, 199, "check", lines=(94, 69, 78))
    b.map((434, 255, 419, 146))
    return b


def game():
    b = Board(GOLD)
    b.panel((80, 111, 440, 414), fill="#193b4d")
    d = b.draw
    d.arc((113, 147, 413, 350), 195, 343, fill=TEAL, width=3)
    d.polygon([(92, 321), (208, 215), (284, 265), (370, 201), (431, 309), (431, 392), (92, 392)],
              fill="#47645a")
    d.polygon([(92, 360), (208, 290), (259, 334), (340, 270), (430, 332), (431, 392), (92, 392)],
              fill="#947251")
    b.dot(341, 171, 23, GOLD)
    b.line((140, 367, 211, 334, 266, 355, 340, 307), PAPER, 4)
    for x, y in ((140, 367), (211, 334), (266, 355), (340, 307)):
        b.dot(x, y, 6, TEAL)
    b.arrow(450, 260, 504)
    for x, kind in ((520, "person"), (702, "file")):
        b.card(x, 131, 172, kind, lines=(75, 58, 42))
    b.card(520, 259, 354, "play", lines=(246, 142, 182))
    return b


def conversation():
    b = Board()
    b.panel((117, 103, 455, 434), stroke=TEAL, fill="#091e28", radius=30)
    for x, y, color in ((156, 141, SOFT), (210, 209, TEAL), (156, 277, GOLD)):
        b.panel((x, y, x + 196, y + 55), stroke=color)
        b.bars(x + 17, y + 22, (142, 100), color)
    b.mark(264, 372, "lock", GOLD)
    b.mark(335, 372, "check", TEAL)
    b.arrow(473, 267, 553)
    b.card(576, 141, 250, "lock", GOLD, (148, 103, 119))
    b.card(576, 272, 250, "file", TEAL, (119, 157, 87))
    return b


def operations():
    b = Board()
    b.map((75, 117, 532, 288))
    b.arrow(618, 259, 665)
    for y, kind, color in ((112, "alert", CORAL), (221, "search", GOLD), (330, "check", TEAL)):
        b.card(677, y, 221, kind, color, (126, 84, 100))
    return b


def documents():
    b = Board()
    b.panel((80, 129, 309, 407), fill="#0a232c")
    for j in range(5):
        for i in range(3):
            x, y = 102 + 62 * i, 158 + 44 * j
            b.panel((x, y, x + 48, y + 30), stroke=GOLD if (j, i) == (3, 2) else FRAME, radius=5)
    b.arrow(320, 268, 391)
    b.panel((405, 157, 562, 379))
    for j in range(4):
        b.mark(435, 194 + j * 46, "alert" if j == 3 else "check", GOLD if j == 3 else TEAL)
        b.bars(468, 185 + 46 * j, (63, 41))
    b.arrow(578, 268, 648)
    for x, y, kind, color in ((666, 140, "file", TEAL), (771, 140, "file", TEAL),
                              (666, 284, "file", TEAL), (771, 284, "alert", GOLD)):
        b.panel((x, y, x + 96, y + 107), stroke=color)
        b.mark(x + 48, y + 52, kind, color)
    return b


def specialists():
    b = Board()
    b.card(76, 220, 194, "file", lines=(101, 75, 83))
    b.arrow(282, 268, 342)
    b.card(356, 115, 232, "person", lines=(139, 77, 100))
    b.card(356, 312, 232, "search", lines=(130, 115, 82))
    b.line((472, 214, 472, 310), b.accent, 4)
    b.arrow(599, 268, 662)
    b.panel((676, 118, 883, 409))
    for y, symbol, color in ((179, "file", SOFT), (261, "alert", CORAL), (348, "check", TEAL)):
        b.mark(705, y, symbol, color)
        b.bars(734, y - 10, (110, 70, 90), color)
    return b


def retrieval():
    b = Board()
    b.card(66, 215, 178, "search", lines=(98, 63, 82))
    b.arrow(255, 264, 307)
    b.panel((321, 109, 548, 424))
    for y, kind, color in ((163, "lock", GOLD), (237, "file", TEAL),
                           (310, "file", TEAL), (378, "alert", CORAL)):
        b.mark(357, y, kind, color)
        b.bars(392, y - 7, (114, 79), color)
    b.arrow(561, 264, 618)
    b.card(633, 136, 244, "file", TEAL, (144, 104, 135))
    b.card(633, 295, 244, "alert", GOLD, (150, 101, 125))
    return b


def evaluation():
    b = Board()
    for y, kind, color in ((124, "check", TEAL), (234, "alert", GOLD), (344, "search", SOFT)):
        b.card(68, y, 223, kind, color, (114, 84, 100))
    b.arrow(308, 281, 374)
    b.panel((389, 132, 562, 427))
    for y, kind, color in ((181, "play", TEAL), (266, "search", GOLD), (355, "file", SOFT)):
        b.mark(423, y, kind, color)
        b.bars(450, y - 7, (90, 63), color)
    b.arrow(575, 281, 643)
    b.panel((656, 132, 889, 427))
    for j, color in enumerate((TEAL, GOLD, CORAL, TEAL)):
        y = 176 + j * 61
        b.dot(684, y, 8, color)
        b.line((705, y, 842 - j * 14, y), color, 7)
    return b


def workbench():
    b = Board()
    b.panel((89, 110, 871, 430), stroke=TEAL, fill="#0a222d", radius=22)
    for x, color in ((113, CORAL), (131, GOLD), (149, TEAL)):
        b.dot(x, 130, 4, color)
    for x, width in ((110, 198), (328, 249), (598, 252)):
        b.panel((x, 153, x + width, 407))
    for y, kind in ((195, "file"), (256, "file"), (321, "lock")):
        b.mark(134, y, kind)
        b.bars(159, y - 9, (104, 73))
    b.mark(362, 199, "search")
    b.bars(392, 191, (151, 108, 76))
    b.mark(362, 293, "play", GOLD)
    b.bars(392, 285, (124, 94))
    b.mark(630, 195, "check")
    b.bars(659, 184, (145, 119, 103))
    b.mark(630, 294, "file")
    b.bars(659, 283, (124, 96, 151))
    return b


BOARDS = {
    "product": product, "game": game, "conversation": conversation, "operations": operations,
    "documents": documents, "specialists": specialists, "retrieval": retrieval,
    "evaluation": evaluation, "workbench": workbench,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ASSETS)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for identifier, compose in BOARDS.items():
        compose().image.save(args.output / f"{identifier}.png", optimize=True)


if __name__ == "__main__":
    main()
