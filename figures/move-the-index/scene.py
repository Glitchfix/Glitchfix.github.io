"""fig 1 of /blog/move-the-index: the index tensor before and after.
render: manim -ql --format=gif scene.py IndexExpansion"""
from manim import *

BG = "#141414"

class IndexExpansion(Scene):
    def construct(self):
        self.camera.background_color = BG

        idx = Square(0.7, color=BLUE, stroke_width=3).shift(LEFT * 5)
        idx_l = Text("idx (T·k)", font="Menlo", font_size=20, color=BLUE).next_to(idx, DOWN, 0.3)
        small = Text("0.26 MB", font="Menlo", font_size=18, color=BLUE).next_to(idx, UP, 0.3)
        self.play(Create(idx), FadeIn(idx_l), FadeIn(small))
        self.wait(0.4)

        arrow = Arrow(LEFT * 4.1, LEFT * 2.6, color=GREY_B, stroke_width=3)
        op = Text(".expand(H)", font="Menlo", font_size=20, color=WHITE).next_to(arrow, UP, 0.2)
        self.play(GrowArrow(arrow), FadeIn(op))

        big = Rectangle(width=4.6, height=3.2, color=RED, stroke_width=3).shift(RIGHT * 0.4)
        big.set_stroke(RED)
        gb = Text("1.07 GB", font="Menlo", font_size=34, color=RED).move_to(big)
        copies = Text("(T·k) × H copies of the same numbers",
                      font="Menlo", font_size=18, color=RED).next_to(big, DOWN, 0.3)
        ghost = idx.copy()
        self.play(Transform(ghost, big), run_time=1.4)
        self.play(FadeIn(gb), FadeIn(copies))
        self.wait(0.8)

        arrow2 = Arrow(RIGHT * 3.0, RIGHT * 4.3, color=GREY_B, stroke_width=3)
        op2 = Text("index_select", font="Menlo", font_size=20, color=WHITE).next_to(arrow2, UP, 0.2)
        out = Square(0.7, color=GREEN, stroke_width=3).shift(RIGHT * 5.2)
        out_l = Text("0.26 MB", font="Menlo", font_size=18, color=GREEN).next_to(out, DOWN, 0.3)
        self.play(GrowArrow(arrow2), FadeIn(op2))
        self.play(Create(out), FadeIn(out_l))
        ratio = Text("4096x less index traffic", font="Menlo", font_size=22,
                     color=GREEN).to_edge(UP, buff=0.4)
        self.play(FadeIn(ratio))
        self.wait(1.2)
