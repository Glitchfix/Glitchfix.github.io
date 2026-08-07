"""fig 1 of /blog/scan-once-scatter-once: per-expert rescans vs count-prefix-scatter.
render: manim -ql scene.py ScanOnce"""
from manim import *

BG = "#141414"

class ScanOnce(Scene):
    def construct(self):
        self.camera.background_color = BG

        # left: E expert blocks each scanning the full route list twice
        routes_l = Rectangle(width=0.55, height=3.0, color=WHITE, stroke_width=2).shift(LEFT * 5.4)
        rl = Text("routes R", font="Menlo", font_size=16, color=WHITE).next_to(routes_l, DOWN, 0.25)
        experts = VGroup(*[Square(0.34, color=RED, stroke_width=2) for _ in range(6)])
        experts.arrange(DOWN, buff=0.18).shift(LEFT * 2.9)
        el = Text("E expert blocks", font="Menlo", font_size=16, color=RED).next_to(experts, DOWN, 0.25)
        self.play(Create(routes_l), FadeIn(rl), Create(experts), FadeIn(el))
        arrows = VGroup()
        for e in experts:
            for dy in (0.06, -0.06):
                arrows.add(Arrow(e.get_left(), routes_l.get_right() + UP * dy * 10,
                                 color=RED, stroke_width=2, buff=0.05,
                                 max_tip_length_to_length_ratio=0.08))
        cap_l = Text("every expert scans every route, twice", font="Menlo",
                     font_size=17, color=RED).to_edge(UP, buff=0.35).shift(LEFT * 3.0)
        self.play(Create(arrows, run_time=1.6), FadeIn(cap_l))
        cost_l = Text("P·R + 2·E·R reads", font="Menlo", font_size=19, color=RED)\
            .next_to(cap_l, DOWN, 0.25)
        self.play(FadeIn(cost_l))
        self.wait(0.6)

        # right: count -> prefix -> scatter
        routes_r = Rectangle(width=0.55, height=3.0, color=WHITE, stroke_width=2).shift(RIGHT * 1.6)
        rr = Text("routes R", font="Menlo", font_size=16, color=WHITE).next_to(routes_r, DOWN, 0.25)
        stages = VGroup(
            Text("1 count", font="Menlo", font_size=18, color=GREEN),
            Text("2 prefix", font="Menlo", font_size=18, color=GREEN),
            Text("3 scatter", font="Menlo", font_size=18, color=GREEN),
        ).arrange(DOWN, buff=0.42, aligned_edge=LEFT).shift(RIGHT * 3.6)
        self.play(Create(routes_r), FadeIn(rr), FadeIn(stages))
        a1 = Arrow(routes_r.get_right() + UP * 0.9, stages[0].get_left(), color=GREEN, stroke_width=2.5, buff=0.1)
        a2 = Arrow(stages[1].get_left() + LEFT * 0.05, routes_r.get_right() + DOWN * 0.9, color=GREEN, stroke_width=2.5, buff=0.1)
        cap_r = Text("each route touched once per pass", font="Menlo",
                     font_size=17, color=GREEN).to_edge(UP, buff=0.35).shift(RIGHT * 3.2)
        cost_r = Text("2·P·R reads", font="Menlo", font_size=19, color=GREEN).next_to(cap_r, DOWN, 0.25)
        self.play(GrowArrow(a1), GrowArrow(a2), FadeIn(cap_r), FadeIn(cost_r))
        ratio = Text("384 experts, EP8, top-8: 44.5M -> 0.92M route reads",
                     font="Menlo", font_size=19, color=WHITE).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(ratio))
        self.wait(1.4)
