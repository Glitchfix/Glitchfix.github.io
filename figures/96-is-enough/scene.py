"""fig 1 of /blog/96-is-enough: routing narrows, payload stays, projections pack.
render: manim -ql --format=gif scene.py PackedQKV"""
from manim import *

BG = "#141414"

def bar(w, color, label):
    r = Rectangle(width=w, height=0.62, color=color, stroke_width=3)
    t = Text(label, font="Menlo", font_size=20, color=color)
    return r, t

class PackedQKV(Scene):
    def construct(self):
        self.camera.background_color = BG
        SCALE = 3.2 / 128  # 128 units -> 3.2 manim units

        q, ql = bar(128 * SCALE, BLUE, "Q 128")
        k, kl = bar(128 * SCALE, BLUE, "K 128")
        v, vl = bar(128 * SCALE, GREEN, "V 128")
        rows = VGroup(q, k, v).arrange(DOWN, buff=0.55).shift(LEFT * 2.4 + UP * 0.3)
        for lab, row in ((ql, q), (kl, k), (vl, v)):
            lab.next_to(row, LEFT, 0.35)
        title = Text("head width", font="Menlo", font_size=22, color=WHITE).to_edge(UP, buff=0.4)
        self.play(FadeIn(title), *[Create(x) for x in (q, k, v)],
                  *[FadeIn(x) for x in (ql, kl, vl)])
        self.wait(0.5)

        q2 = Rectangle(width=96 * SCALE, height=0.62, color=YELLOW, stroke_width=3)\
            .align_to(q, LEFT).align_to(q, UP)
        k2 = Rectangle(width=96 * SCALE, height=0.62, color=YELLOW, stroke_width=3)\
            .align_to(k, LEFT).align_to(k, UP)
        ql2 = Text("Q 96", font="Menlo", font_size=20, color=YELLOW).next_to(q2, LEFT, 0.35)
        kl2 = Text("K 96", font="Menlo", font_size=20, color=YELLOW).next_to(k2, LEFT, 0.35)
        note = Text("routing narrows · payload stays", font="Menlo",
                    font_size=20, color=YELLOW).next_to(rows, DOWN, 0.6)
        self.play(Transform(q, q2), Transform(k, k2),
                  Transform(ql, ql2), Transform(kl, kl2), FadeIn(note))
        self.wait(0.8)

        packed = Rectangle(width=(96 + 96 + 128) * SCALE * 0.9, height=0.62,
                           color=WHITE, stroke_width=3).shift(DOWN * 2.4)
        pl = Text("one packed FP8 GEMM · 320 cols (was 384)", font="Menlo",
                  font_size=20, color=WHITE).next_to(packed, DOWN, 0.3)
        self.play(FadeOut(note),
                  ReplacementTransform(VGroup(q.copy(), k.copy(), v.copy()), packed),
                  FadeIn(pl))
        self.wait(1.2)
