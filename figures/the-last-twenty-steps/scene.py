"""Figure 1 of /blog/the-last-twenty-steps: inspect the end of the schedule.

Render from the repository root:
manim -qm --disable_caching --media_dir /tmp/nanogpt-accepted-manim \
    figures/the-last-twenty-steps/scene.py LastTwentySteps

Only the final 45 steps are drawn, at one cell per step. This is not a time
comparison: the submitted raw time and accepted record have different provenance.
"""
from manim import *

BG = "#141414"


def label(text, size=22, color=WHITE):
    return Text(text, font="Menlo", font_size=size, color=color)


class LastTwentySteps(Scene):
    def construct(self):
        self.camera.background_color = BG

        title = label("the last twenty steps", 30).to_edge(UP, buff=0.45)
        detail = label("final 45 steps only; one cell = one step", 21)
        detail.next_to(title, DOWN, buff=0.35)

        cells = VGroup(*[
            Rectangle(width=0.20, height=0.50, color=BLUE,
                      fill_color=BLUE, fill_opacity=0.35, stroke_width=1.5)
            for _ in range(45)
        ]).arrange(RIGHT, buff=0.04).move_to(UP * 0.75)
        keep = VGroup(*cells[:25])
        tail = VGroup(*cells[25:])
        keep_label = label("steps 1271 to 1295", 20).next_to(keep, DOWN, 0.24)
        tail_label = label("steps 1296 to 1315", 20, YELLOW).next_to(tail, DOWN, 0.24)
        total = label("submitted: 1315 steps", 25).move_to(DOWN * 0.8)

        self.play(FadeIn(title), FadeIn(detail), FadeIn(cells),
                  FadeIn(keep_label), FadeIn(tail_label), FadeIn(total))
        self.wait(1.0)
        self.play(tail.animate.set_color(YELLOW).set_fill(YELLOW, opacity=0.5))
        removed = label("remove 20; recheck the loss", 23, YELLOW)
        removed.move_to(DOWN * 1.5)
        self.play(FadeIn(removed))
        self.wait(1.0)
        accepted = label("accepted: 1295 steps", 25, GREEN).move_to(total)
        self.play(tail.animate.set_opacity(0.10),
                  keep.animate.set_color(GREEN).set_fill(GREEN, opacity=0.5),
                  Transform(total, accepted))

        losses = label("validation: 3.2769   3.2794   3.2785", 24, GREEN)
        losses.move_to(DOWN * 2.2)
        threshold = label("target: 3.28   |   1.52% fewer steps", 22)
        threshold.move_to(DOWN * 2.85)
        self.play(FadeIn(losses), FadeIn(threshold))
        self.wait(3.0)
