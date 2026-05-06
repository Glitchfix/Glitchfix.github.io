"""fig 1 of /blog/anisotropic-voxels: cubic resampling vs native anisotropic voxels.
render: manim -ql --format=gif scene.py AnisotropicVoxels"""
from manim import *

BG = "#141414"

def grid(cols, rows, w, h, color, sw=2):
    g = VGroup()
    for i in range(cols):
        for j in range(rows):
            g.add(Rectangle(width=w, height=h, color=color, stroke_width=sw)
                  .move_to(RIGHT * i * w + UP * j * h))
    g.center()
    return g

class AnisotropicVoxels(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("the same 64 mm volume, side view", font="Menlo",
                     font_size=22, color=WHITE).to_edge(UP, buff=0.35)
        self.play(FadeIn(title))

        # left: forced cubes at 0.5 mm -> dense grid (12x12 shown)
        cubes = grid(12, 12, 0.24, 0.24, RED, sw=1.5).shift(LEFT * 3.1 + DOWN * 0.4)
        cl1 = Text("0.5 mm cubes", font="Menlo", font_size=20, color=RED)\
            .next_to(cubes, DOWN, 0.35)
        cl2 = Text("2.10M voxels · slices invented", font="Menlo", font_size=17,
                   color=RED).next_to(cl1, DOWN, 0.18)
        self.play(Create(cubes, run_time=1.6), FadeIn(cl1), FadeIn(cl2))
        self.wait(0.5)

        # right: native anisotropic (0.5, 3.0) -> 12 wide, 2 tall slabs
        slabs = grid(12, 2, 0.24, 1.44, GREEN, sw=2).shift(RIGHT * 3.1 + DOWN * 0.4)
        sl1 = Text("(0.5, 0.5, 3.0) native", font="Menlo", font_size=20, color=GREEN)\
            .next_to(slabs, DOWN, 0.35)
        sl2 = Text("0.35M voxels · as measured", font="Menlo", font_size=17,
                   color=GREEN).next_to(sl1, DOWN, 0.18)
        self.play(Create(slabs, run_time=1.2), FadeIn(sl1), FadeIn(sl2))
        ratio = Text("6x memory saved, zero interpolation", font="Menlo",
                     font_size=20, color=GREEN).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(ratio))
        self.wait(1.2)
