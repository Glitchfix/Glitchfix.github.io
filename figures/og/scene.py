"""site og:image card. render: manim -s -r 1200,630 scene.py OgCard"""
from manim import *

class OgCard(Scene):
    def construct(self):
        self.camera.background_color = "#141414"
        logo = Text("glitch", font="Menlo", font_size=56, color=WHITE)
        fix = Text("fix", font="Menlo", font_size=56, color="#4cc2b4").next_to(logo, RIGHT, buff=0.05)
        lockup = VGroup(logo, fix).move_to(UP * 1.1)
        name = Text("Shivanjan Chakravorty", font_size=40, color=WHITE,
                    weight=MEDIUM).next_to(lockup, DOWN, buff=0.7)
        line = Text("AI inference · GPU simulation · 3D reconstruction · robot learning",
                    font="Menlo", font_size=22, color="#8b9a91").next_to(name, DOWN, buff=0.55)
        self.add(lockup, name, line)
