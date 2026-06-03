"""
🐇 The Rabbit & Tortoise Race — Learn Python Visualisation
A Streamlit-native learning app for kids.

Requires: streamlit>=1.37, matplotlib>=3.7, numpy>=1.24
Run:  streamlit run app.py
"""

import streamlit as st
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse
from matplotlib.animation import FuncAnimation
import tempfile, textwrap

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="🐇 Learn Python — Rabbit & Tortoise",
    page_icon="🐇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# MINIMAL CSS  (only things Streamlit cannot do natively)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800;900&display=swap');
html,body,[class*="css"]{font-family:'Nunito',sans-serif!important}

.story-card{
    background:linear-gradient(135deg,#fffde7,#fff9c4);
    border-left:5px solid #fbc02d;
    border-radius:0 14px 14px 0;
    padding:16px 20px;
    font-size:15px;
    line-height:1.8;
    color:#4e3a00;
    margin:6px 0 14px;
}
.challenge-card{
    background:linear-gradient(135deg,#e8f5e9,#f1f8e9);
    border:2.5px dashed #66bb6a;
    border-radius:14px;
    padding:16px 20px;
    font-size:15px;
    color:#1b5e20;
    line-height:1.7;
}
.win-banner{
    background:linear-gradient(135deg,#fff8e1,#ffecb3);
    border:3px solid #ffa000;
    border-radius:18px;
    padding:28px;
    text-align:center;
    margin:16px 0;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# DRAWING LIBRARY  (shared by static previews + animation)
# ══════════════════════════════════════════════════════════════
C = dict(
    grass="#4CAF50", dgrass="#2E7D32", track="#D7CCC8",
    soil="#8D6E63", sun="#FFD600",
    fur="#F5F5DC", fur_e="#C8A96E", ear="#FFCCBC",
    shell="#558B2F", shell_e="#33691E",
    sky_hi=(100/255, 181/255, 246/255),
    sky_lo=(179/255, 229/255, 252/255),
)

def setup_ax(ax, title=""):
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    for i in range(50):
        t = i / 49
        col = tuple(C["sky_hi"][j] * (1-t) + C["sky_lo"][j] * t for j in range(3))
        ax.axhspan(50+i, 51+i, color=col, zorder=0)
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold",
                     color="#1a237e", pad=8)

def draw_ground(ax):
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 12), 100, 14, boxstyle="round,pad=0",
        fc=C["track"], ec="none", zorder=1))
    ax.fill_between([0, 100], [0, 0], [12, 12], color=C["soil"], zorder=1)
    x = np.linspace(0, 100, 400)
    y = 5 * np.sin(x / 6) + 26
    ax.fill_between(x, 0, y, color=C["grass"], alpha=0.85, zorder=2)
    ax.plot(x, y, color=C["dgrass"], lw=1.5, zorder=3)

def draw_ground_anim(ax, frame):
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 12), 100, 14, boxstyle="round,pad=0",
        fc=C["track"], ec="none", zorder=1))
    ax.fill_between([0, 100], [0, 0], [12, 12], color=C["soil"], zorder=1)
    x = np.linspace(0, 100, 400)
    y = 5 * np.sin(x / 6 + frame / 12) + 26
    ax.fill_between(x, 0, y, color=C["grass"], alpha=0.85, zorder=2)
    ax.plot(x, y, color=C["dgrass"], lw=1.5, zorder=3)

def draw_sun(ax, rf=0):
    ax.add_patch(plt.Circle((90, 90), 7, color=C["sun"], zorder=5))
    for a in range(0, 360, 45):
        ang = np.radians(a + rf * 2)
        ax.plot([90 + 8*np.cos(ang), 90 + 11*np.cos(ang)],
                [90 + 8*np.sin(ang), 90 + 11*np.sin(ang)],
                color=C["sun"], lw=2, zorder=5)

def draw_clouds(ax, offset=0):
    for cx, cy, s in [(18, 85, 1.0), (45, 88, 0.8), (70, 83, 1.2)]:
        ox = (cx + offset) % 105 - 5
        for dx, dy, rx, ry in [(0,0,8,5),(6,2,6,4),(-6,1,5,3)]:
            ax.add_patch(Ellipse((ox+dx, cy+dy), rx*s*2, ry*s*2,
                                 color="white", alpha=0.9, zorder=4))

def draw_harry(ax, x, y, sleeping=False, speeding=False):
    ax.add_patch(plt.Circle((x, y), 5.5, color=C["fur"],
                             ec=C["fur_e"], lw=2, zorder=8))
    for ex in [-2.2, 2.2]:
        ax.add_patch(Ellipse((x+ex, y+8), 2.5, 6,
                             color=C["fur"], ec=C["fur_e"], lw=2, zorder=7))
        ax.add_patch(Ellipse((x+ex, y+8), 1.2, 3.5,
                             color=C["ear"], zorder=9))
    if sleeping:
        for ex_pair in [(-2, -0.8), (0.8, 2)]:
            ax.plot([x+ex_pair[0], x+ex_pair[1]], [y+1.5, y+1.5],
                    color="#5D4037", lw=2, zorder=10)
        ax.text(x+5, y+9, "zzz", fontsize=9, color="#9575CD",
                fontstyle="italic", zorder=10)
    else:
        for ex in [-1.8, 1.8]:
            ax.add_patch(plt.Circle((x+ex, y+1.5), 1,
                                    color="#5D4037", zorder=10))
            ax.add_patch(plt.Circle((x+ex+0.3, y+1.8), 0.4,
                                    color="white", zorder=11))
    ax.add_patch(plt.Circle((x, y-0.5), 0.7, color="#EF9A9A", zorder=10))
    if speeding:
        for dy in [-2, 0, 2]:
            ax.plot([x-13, x-7], [y+dy, y+dy],
                    color="#90CAF9", lw=1.5, alpha=0.7, zorder=7)
    ax.text(x-4, y-11, "Harry", fontsize=9,
            fontweight="bold", color="#4e342e", zorder=10)

def draw_tommy(ax, x, y):
    ax.add_patch(Ellipse((x, y+2), 13, 8,
                         color=C["shell"], ec=C["shell_e"], lw=2, zorder=8))
    for dx in [-3, 0, 3]:
        ax.plot([x+dx, x+dx], [y-1, y+5],
                color=C["shell_e"], lw=0.8, alpha=0.5, zorder=9)
    ax.plot([x-5, x+5], [y+2, y+2],
            color=C["shell_e"], lw=0.8, alpha=0.5, zorder=9)
    ax.add_patch(plt.Circle((x+7, y+1), 3.2,
                             color="#8BC34A", ec=C["shell_e"], lw=1.5, zorder=8))
    ax.add_patch(plt.Circle((x+8.5, y+2), 0.9, color="#33691E", zorder=10))
    ax.add_patch(plt.Circle((x+8.8, y+2.3), 0.4, color="white", zorder=11))
    for fx, fy in [(x-4, y-3.5), (x-1, y-3.8), (x+2, y-3.8), (x+5, y-3.5)]:
        ax.add_patch(Ellipse((fx, fy), 3, 2,
                             color="#8BC34A", ec=C["shell_e"], lw=1, zorder=7))
    ax.text(x-2, y-12, "Tommy", fontsize=9,
            fontweight="bold", color="#1B5E20", zorder=10)

def draw_flowers(ax):
    cols = ["#F44336", "#FF9800", "#E91E63", "#9C27B0", "#FFEB3B"]
    for i, col in enumerate(cols):
        cx = 8 + i*17; cy = 35
        for a in range(0, 360, 72):
            ang = np.radians(a)
            ax.add_patch(Ellipse(
                (cx + 3*np.cos(ang), cy + 3*np.sin(ang)),
                4, 2.5, angle=np.degrees(ang),
                color=col, alpha=0.85, zorder=5))
        ax.add_patch(plt.Circle((cx, cy), 1.8, color="#FFEB3B", zorder=6))
        ax.plot([cx, cx], [26, 32], color=C["dgrass"], lw=1.5, zorder=4)

def draw_spiral(ax, cx, cy, turns=5, scale=0.45):
    t = np.linspace(0, turns * 2 * np.pi, 1200)
    r = t * scale
    ax.plot(cx + r*np.cos(t), cy + r*np.sin(t),
            color="#9C27B0", lw=1.5, alpha=0.85, zorder=9)

def draw_finish(ax, fx=88):
    ax.plot([fx, fx], [26, 52], color="#212121", lw=3, zorder=6)
    for i in range(9):
        col = "white" if i % 2 == 0 else "#212121"
        ax.add_patch(mpatches.FancyBboxPatch(
            (fx, 26 + i*2.8), 4, 2.8,
            fc=col, ec="#212121", lw=0.5, zorder=6))
    ax.text(fx+5, 48, "FINISH", fontsize=9,
            fontweight="bold", color="#F44336", zorder=10)


# ══════════════════════════════════════════════════════════════
# STATIC PREVIEW BUILDERS
# ══════════════════════════════════════════════════════════════
def fig_sky():
    fig, ax = plt.subplots(figsize=(7, 4.2))
    setup_ax(ax, "The Rabbit and the Tortoise")
    draw_sun(ax); draw_clouds(ax); draw_ground(ax)
    ax.text(50, 68, "Canvas ready!", fontsize=15, ha="center",
            fontweight="bold", color="#1a237e",
            bbox=dict(fc="white", ec="#5c6bc0", boxstyle="round,pad=0.5"))
    plt.tight_layout(); return fig

def fig_harry():
    fig, ax = plt.subplots(figsize=(7, 4.2))
    setup_ax(ax); draw_sun(ax); draw_clouds(ax); draw_ground(ax)
    draw_harry(ax, 25, 42, speeding=True)
    plt.tight_layout(); return fig

def fig_wave():
    fig, ax = plt.subplots(figsize=(7, 4.2))
    setup_ax(ax); draw_sun(ax); draw_clouds(ax)
    x = np.linspace(0, 100, 400)
    for ph, al in [(0, 0.9), (0.9, 0.45), (1.8, 0.2)]:
        ax.fill_between(x, 0, 5*np.sin(x/6+ph)+26,
                        color=C["grass"], alpha=al, zorder=2)
    ax.plot(x, 5*np.sin(x/6)+26, color=C["dgrass"], lw=2, zorder=3)
    ax.add_patch(mpatches.FancyBboxPatch((0, 12), 100, 14,
        boxstyle="round,pad=0", fc=C["track"], ec="none", zorder=1))
    ax.fill_between([0, 100], [0, 0], [12, 12], color=C["soil"], zorder=1)
    draw_harry(ax, 22, 42, speeding=True); draw_tommy(ax, 55, 33)
    plt.tight_layout(); return fig

def fig_flowers():
    fig, ax = plt.subplots(figsize=(7, 4.2))
    setup_ax(ax); draw_sun(ax); draw_clouds(ax)
    draw_ground(ax); draw_flowers(ax); draw_tommy(ax, 62, 33)
    plt.tight_layout(); return fig

def fig_spiral():
    fig, ax = plt.subplots(figsize=(7, 4.2))
    setup_ax(ax); draw_sun(ax); draw_clouds(ax); draw_ground(ax)
    draw_harry(ax, 55, 42, sleeping=True)
    ax.add_patch(plt.Circle((73, 68), 16,
                             fc="#EDE7F6", ec="#9C27B0",
                             lw=2, alpha=0.92, zorder=8))
    draw_spiral(ax, 73, 68, turns=3, scale=0.42)
    for r, (ox, oy) in zip([2.4, 1.7, 1.1], [(64, 57), (67, 61), (70, 64)]):
        ax.add_patch(plt.Circle((ox, oy), r,
                                fc="#EDE7F6", ec="#9C27B0", lw=1.5, zorder=8))
    plt.tight_layout(); return fig

def fig_anim_preview():
    fig, ax = plt.subplots(figsize=(7, 4.2))
    setup_ax(ax); draw_sun(ax, rf=6); draw_clouds(ax, offset=10)
    draw_ground_anim(ax, 30)
    draw_harry(ax, 32, 42, sleeping=True)
    draw_tommy(ax, 80, 33); draw_finish(ax, 88)
    ax.text(50, 76, "Slow & Steady Wins the Race!",
            fontsize=12, ha="center", fontweight="bold", color="#FF6F00",
            bbox=dict(fc="#FFFDE7", ec="#FFA000", boxstyle="round,pad=0.5"),
            zorder=15)
    plt.tight_layout(); return fig

PREVIEW = dict(sky=fig_sky, harry=fig_harry, wave=fig_wave,
               flowers=fig_flowers, spiral=fig_spiral,
               animation=fig_anim_preview)


# ══════════════════════════════════════════════════════════════
# ANIMATION  (cached — built once per server session)
# ══════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def make_animation_html():
    np.random.seed(7)
    confetti = [(np.random.uniform(5, 95),
                 np.random.uniform(32, 88),
                 np.random.choice(["#FF5722","#FFEB3B","#4CAF50",
                                   "#2196F3","#9C27B0","#FF9800"]))
                for _ in range(20)]
    fig, ax = plt.subplots(figsize=(9, 5.2))

    def update(fr):
        ax.clear(); setup_ax(ax)
        draw_sun(ax, rf=fr); draw_clouds(ax, offset=fr*0.15)
        draw_ground_anim(ax, fr)

        if fr < 55:
            draw_harry(ax, min(10 + fr*1.4, 74), 42, speeding=True)
            draw_tommy(ax, 12, 33)
            ax.text(50, 82, "Harry races ahead!", ha="center",
                    fontsize=13, fontweight="bold", color="#1565C0",
                    bbox=dict(fc="white", ec="#1565C0", boxstyle="round,pad=0.4"))

        elif fr < 110:
            draw_harry(ax, 75, 42, sleeping=True)
            bx, by = 73, 70
            ax.add_patch(plt.Circle((bx, by), 14,
                                    fc="#EDE7F6", ec="#9C27B0",
                                    lw=2, alpha=0.92, zorder=8))
            draw_spiral(ax, bx, by,
                        turns=min(1 + (fr-55)/18, 4.5), scale=0.38)
            for r, (ox, oy) in zip([2.2, 1.6, 1.1],
                                   [(65, 59), (68, 62), (71, 65)]):
                ax.add_patch(plt.Circle((ox, oy), r,
                                        fc="#EDE7F6", ec="#9C27B0",
                                        lw=1.5, zorder=8))
            draw_tommy(ax, min(12 + (fr-55)*1.1, 88), 33)
            draw_flowers(ax)
            ax.text(50, 82, "Tommy keeps walking...", ha="center",
                    fontsize=13, fontweight="bold", color="#2E7D32",
                    bbox=dict(fc="white", ec="#2E7D32", boxstyle="round,pad=0.4"))

        else:
            draw_harry(ax, 75, 42, sleeping=True)
            draw_tommy(ax, 90, 33)
            draw_finish(ax, 89)
            prog = min((fr - 110) / 35, 1.0)
            for i, (cx, cy, col) in enumerate(confetti):
                if i / len(confetti) < prog:
                    ax.add_patch(plt.Circle((cx, cy), 1.5, color=col, zorder=14))
            ax.text(50, 78, "Slow & Steady Wins the Race!",
                    ha="center", fontsize=14, fontweight="bold", color="#FF6F00",
                    bbox=dict(fc="#FFFDE7", ec="#FFA000", boxstyle="round,pad=0.5"),
                    zorder=15)

    ani = FuncAnimation(fig, update, frames=160, interval=65)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
        ani.save(f.name, writer="html")
        html_str = open(f.name).read()
    plt.close(fig)
    return html_str


# ══════════════════════════════════════════════════════════════
# LESSON DATA
# ══════════════════════════════════════════════════════════════
LESSONS = [
    dict(
        id=1, key="sky", emoji="🌈",
        title="Drawing the Sky",
        concept="Setting up the canvas",
        color="blue",
        story="Harry the Rabbit wants to draw a racetrack! Every matplotlib "
              "picture starts with <b>plt.subplots()</b> — it gives us a canvas "
              "(fig) and a drawing area (ax). Let's paint the sky!",
        code=textwrap.dedent("""\
            import matplotlib.pyplot as plt

            # Create canvas (fig) and drawing area (ax)
            fig, ax = plt.subplots(figsize=(10, 6))

            # Paint the background
            ax.set_facecolor("skyblue")

            # Set coordinate grid: 0–100 wide, 0–100 tall
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)

            # Add a title
            ax.set_title("The Rabbit and the Tortoise",
                         fontsize=16, fontweight='bold')

            plt.tight_layout()
            plt.show()
        """),
        tips=[
            ("🖼️", "**plt.subplots()** creates two things: `fig` (the whole image) and `ax` (where you draw)"),
            ("🎨", "**set_facecolor()** paints the background — try `'lightgreen'` or `'lightyellow'`!"),
            ("📏", "**set_xlim(0,100)** + **set_ylim(0,100)** make a grid where every point is 0–100"),
            ("🏷️", "**set_title()** adds a label above the picture"),
        ],
        challenge="🎯 **Try it!**  Change `'skyblue'` to `'lightyellow'` — what happens to the sky?",
    ),
    dict(
        id=2, key="harry", emoji="🐇",
        title="Drawing Harry",
        concept="ax.plot() — placing markers",
        color="orange",
        story="Time to place Harry on the track! <b>ax.plot(x, y)</b> puts a "
              "point at any coordinate. We choose a big circle marker for his "
              "body, and <b>ax.text()</b> to write his name.",
        code=textwrap.dedent("""\
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_facecolor("skyblue")
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)

            # Draw a brown ground line
            ax.plot([0, 100], [15, 15],
                    color='brown', linewidth=6)

            # Harry at position (20, 50)
            # 'o' = circle marker
            ax.plot(20, 50, 'o',
                    markersize=30,
                    color='#F5F5DC',
                    markeredgecolor='#C8A96E',
                    markeredgewidth=2)

            # Label him
            ax.text(14, 38, "Harry",
                    fontsize=13, fontweight='bold',
                    color='#4e342e')

            plt.tight_layout()
            plt.show()
        """),
        tips=[
            ("📍", "**ax.plot(x, y)** places a point at coordinate (x, y) on the canvas"),
            ("⭕", "`'o'` = circle — try `'s'` (square), `'^'` (triangle) or `'*'` (star)!"),
            ("📐", "**markersize** controls size — bigger number = bigger dot"),
            ("✏️", "**ax.text(x, y, 'words')** writes any text at that position"),
        ],
        challenge="🎯 **Try it!**  Change `ax.plot(20, 50, ...)` to `ax.plot(50, 50, ...)` — Harry moves to the centre!",
    ),
    dict(
        id=3, key="wave", emoji="〰️",
        title="Making Grass Waves",
        concept="NumPy arrays + np.sin()",
        color="green",
        story="The track has rolling green hills! <b>np.linspace()</b> creates "
              "hundreds of x values, then <b>np.sin()</b> makes them go up and "
              "down like a wave. <b>fill_between()</b> fills the area with colour.",
        code=textwrap.dedent("""\
            import matplotlib.pyplot as plt
            import numpy as np

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_facecolor("skyblue")
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)

            # 400 evenly-spaced x values from 0 to 100
            x = np.linspace(0, 100, 400)

            # Wavy y values:
            # 5  → height of wave (amplitude)
            # /6 → width  of wave (period)
            # +26 → shifts the whole wave upwards
            y = 5 * np.sin(x / 6) + 26

            # Fill green below the wave
            ax.fill_between(x, 0, y,
                            color='#4CAF50', alpha=0.85)
            ax.plot(x, y, color='#2E7D32', linewidth=2)

            plt.tight_layout()
            plt.show()
        """),
        tips=[
            ("📊", "**np.linspace(0, 100, 400)** makes 400 evenly-spaced numbers between 0 and 100"),
            ("🌊", "**np.sin()** creates a wave — the `5` in `5 * np.sin(...)` controls the **HEIGHT**"),
            ("↔️", "Dividing x by `6` controls the **WIDTH** — try `x/2` (very narrow) or `x/15` (very wide)"),
            ("🎨", "**fill_between(x, 0, y)** fills the area between y=0 and y=wave with green"),
        ],
        challenge="🎯 **Try it!**  Change the `5` before `np.sin` to `14` — the hills turn into mountains!",
    ),
    dict(
        id=4, key="flowers", emoji="🌸",
        title="Flower Garden",
        concept="Functions + for loops",
        color="violet",
        story="Tommy passes a beautiful garden. We write a <b>def</b> function "
              "once — the recipe for one flower — then a <b>for loop</b> bakes "
              "five flowers automatically, each a different colour.",
        code=textwrap.dedent("""\
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.patches import Ellipse

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_facecolor("skyblue")
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)

            # ── Recipe for ONE flower ──────────────────
            def draw_flower(ax, cx, cy, color):
                # 5 petals spaced 72° apart (360 / 5 = 72)
                for angle in range(0, 360, 72):
                    rad = np.radians(angle)
                    px = cx + 3 * np.cos(rad)
                    py = cy + 3 * np.sin(rad)
                    ax.add_patch(Ellipse(
                        (px, py), 4, 2.5,
                        angle=angle, color=color, alpha=0.85))
                # Yellow centre dot
                ax.add_patch(plt.Circle(
                    (cx, cy), 1.8, color='#FFEB3B'))

            # ── Bake 5 flowers with a for loop ─────────
            colors = ['red', 'orange', '#E91E63',
                      '#9C27B0', '#FFEB3B']
            for i, color in enumerate(colors):
                draw_flower(ax, 8 + i * 17, 35, color)

            plt.tight_layout()
            plt.show()
        """),
        tips=[
            ("🔧", "**def draw_flower():** defines a function — write the recipe once, use it many times!"),
            ("🌸", "Each petal is an **Ellipse** placed around the centre using `cos()` and `sin()`"),
            ("🔁", "**for i, color in enumerate(colors):** loops over the list giving both index AND value"),
            ("📋", "`enumerate()` is useful when you need both the position (`i`) and the item (`color`)"),
        ],
        challenge="🎯 **Try it!**  Change `range(0, 360, 72)` to `range(0, 360, 60)` — flowers get 6 petals!",
    ),
    dict(
        id=5, key="spiral", emoji="💤",
        title="Harry's Dream Spiral",
        concept="Polar coordinates",
        color="violet",
        story="Harry falls asleep and dreams in spirals! <b>Polar coordinates</b> "
              "describe a point by its angle (theta) and distance (r). When r "
              "grows with theta, the result is a perfect spiral.",
        code=textwrap.dedent("""\
            import matplotlib.pyplot as plt
            import numpy as np

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_facecolor("skyblue")
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)

            # Dream bubble
            bubble = plt.Circle((72, 68), 16,
                                 facecolor='#EDE7F6',
                                 edgecolor='#9C27B0',
                                 linewidth=2, alpha=0.9)
            ax.add_patch(bubble)

            # ── Polar coordinates ──────────────────────
            # theta = angle from 0 → 5 full rotations
            theta = np.linspace(0, 5 * 2 * np.pi, 1000)

            # r grows bigger as theta increases → spiral!
            r = theta * 0.45

            # Convert polar (r, theta) → cartesian (x, y)
            x = 72 + r * np.cos(theta)
            y = 68 + r * np.sin(theta)

            ax.plot(x, y, color='#9C27B0', linewidth=1.5)

            plt.tight_layout()
            plt.show()
        """),
        tips=[
            ("🌀", "`r = theta * 0.45` means the radius **grows** with the angle — that's what makes a spiral!"),
            ("📐", "**np.cos(theta)** and **np.sin(theta)** convert angle into x and y positions"),
            ("🔄", "`5 * 2 * np.pi` = 5 full rotations — one full rotation is always **2π** (≈ 6.28)"),
            ("⚙️", "Change `0.45` to `0.9` — the spiral expands twice as fast outward!"),
        ],
        challenge="🎯 **Try it!**  Change `5 * 2 * np.pi` to `10 * 2 * np.pi` — the dream bubble overflows!",
    ),
    dict(
        id=6, key="animation", emoji="🏆",
        title="The Full Race — Animated!",
        concept="FuncAnimation",
        color="green",
        story="Tommy crosses the finish line! <b>FuncAnimation</b> calls your "
              "<b>update()</b> function 160 times — once per frame — like a "
              "cartoon. Each call draws everything slightly differently.",
        code=textwrap.dedent("""\
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.animation import FuncAnimation
            import streamlit as st
            import tempfile

            fig, ax = plt.subplots(figsize=(9, 5))

            def update(frame):
                ax.clear()
                ax.set_xlim(0, 100)
                ax.set_ylim(0, 100)
                ax.set_facecolor("skyblue")
                ax.axis("off")

                # Grass moves with the frame number
                x = np.linspace(0, 100, 400)
                y = 5 * np.sin(x / 6 + frame / 12) + 26
                ax.fill_between(x, 0, y,
                                color='#4CAF50', alpha=0.85)

                if frame < 55:
                    # Scene 1: Harry sprints
                    ax.plot(10 + frame * 1.4, 42,
                            'o', ms=22, color='#F5F5DC')
                    ax.text(50, 80, "Harry races ahead!",
                            ha='center', fontsize=13,
                            fontweight='bold')

                elif frame < 110:
                    # Scene 2: Harry sleeps, Tommy walks
                    ax.plot(75, 42, 'o', ms=22,
                            color='#F5F5DC')
                    ax.text(80, 55, "zzz", fontsize=11)
                    tommy_x = 12 + (frame - 55) * 1.1
                    ax.plot(tommy_x, 35, 's', ms=18,
                            color='#558B2F')
                    ax.text(50, 80, "Tommy keeps going...",
                            ha='center', fontsize=13,
                            fontweight='bold')

                else:
                    # Scene 3: Tommy wins!
                    ax.plot(88, 35, 's', ms=18,
                            color='#558B2F')
                    ax.text(50, 78,
                            "Slow & Steady Wins!",
                            ha='center', fontsize=15,
                            fontweight='bold', color='#FF6F00')

            # 160 frames, 65 ms apart ≈ 10-second movie
            ani = FuncAnimation(fig, update,
                                frames=160, interval=65)

            # Save HTML and embed with st.iframe
            with tempfile.NamedTemporaryFile(
                    delete=False, suffix='.html') as f:
                ani.save(f.name, writer='html')
                html_str = open(f.name).read()

            st.iframe(html_str, height=480)
        """),
        tips=[
            ("🎬", "**FuncAnimation** calls `update()` 160 times — like 160 frames of a cartoon!"),
            ("🧹", "**ax.clear()** wipes the canvas clean each frame so we can redraw from scratch"),
            ("📺", "`frames=160, interval=65` → 160 pictures, 65 ms apart ≈ a 10-second movie"),
            ("🚶", "`tommy_x = 12 + (frame-55)*1.1` increases every frame — that's how movement works!"),
        ],
        challenge="🎯 **Try it!**  Change `interval=65` to `interval=30` — the whole race runs twice as fast!",
    ),
]


# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
if "stars"   not in st.session_state: st.session_state.stars   = [False] * 6
if "lesson"  not in st.session_state: st.session_state.lesson  = 0
if "toasted" not in st.session_state: st.session_state.toasted = [False] * 6


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🐇 Rabbit & Tortoise")
    st.caption("Learn Python visualisation step by step!")
    st.divider()

    # Progress
    done = sum(st.session_state.stars)
    st.markdown(f"**Your progress — {done}/6 done**")
    st.progress(done / 6)
    st.markdown("")

    # Lesson navigator via pills
    pill_opts = [
        ("⭐" if st.session_state.stars[i] else L["emoji"]) + f"  {L['title']}"
        for i, L in enumerate(LESSONS)
    ]
    chosen = st.pills(
        "Jump to a lesson",
        options=pill_opts,
        default=pill_opts[st.session_state.lesson],
        key="lesson_pill",
    )
    if chosen:
        idx = pill_opts.index(chosen)
        if idx != st.session_state.lesson:
            st.session_state.lesson = idx
            st.rerun()

    st.divider()

    # Colour cheat-sheet inside a popover
    with st.popover("🎨 Colour cheat-sheet", use_container_width=True):
        colours = {
            "skyblue":     "#87CEEB",
            "lightgreen":  "#90EE90",
            "lightyellow": "#FFFFE0",
            "lightcoral":  "#F08080",
            "lavender":    "#E6E6FA",
            "peachpuff":   "#FFDAB9",
            "mintcream":   "#F5FFFA",
            "aliceblue":   "#F0F8FF",
        }
        for name, hx in colours.items():
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;'
                f'margin-bottom:6px;">'
                f'<div style="width:22px;height:22px;border-radius:5px;'
                f'background:{hx};border:1px solid #ccc"></div>'
                f'<code>{name!r}</code></div>',
                unsafe_allow_html=True)

    # Quick reference inside a popover
    with st.popover("📋 Quick reference", use_container_width=True):
        cmds = [
            ("plt.subplots()",       "Create figure + axes"),
            ("ax.set_facecolor()",   "Set background colour"),
            ("ax.set_xlim/ylim()",   "Set coordinate range"),
            ("ax.plot(x, y)",        "Draw points or lines"),
            ("ax.text(x, y, s)",     "Write text anywhere"),
            ("ax.add_patch()",       "Add shapes (circles, ellipses…)"),
            ("np.linspace()",        "Evenly-spaced numbers"),
            ("np.sin() / np.cos()",  "Wave & spiral math"),
            ("ax.fill_between()",    "Fill between two curves"),
            ("def func():",          "Define a function"),
            ("for i in range(n):",   "Loop n times"),
            ("FuncAnimation()",      "Animate the figure"),
            ("st.iframe(html)",      "Show animation in Streamlit"),
        ]
        for cmd, desc in cmds:
            st.markdown(f"**`{cmd}`** — {desc}")

    st.divider()
    st.markdown("**Install & run:**")
    st.code("pip install streamlit matplotlib numpy\nstreamlit run app.py",
            language="bash")
    st.caption("Built with ❤️ using Streamlit + Matplotlib")


# ══════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════
L  = LESSONS[st.session_state.lesson]
li = st.session_state.lesson
done = sum(st.session_state.stars)

# ── Top bar ───────────────────────────────────────────────────
top_l, top_r = st.columns([4, 1])
with top_l:
    st.badge(f"Lesson {L['id']} of 6  ·  {L['concept']}", color=L["color"])
    st.markdown(f"# {L['emoji']} {L['title']}")
with top_r:
    stars_str = "⭐" * done + "☆" * (6 - done)
    st.metric(label="Stars earned", value=f"{done}/6",
              delta=stars_str, delta_color="off")

# Story card
st.markdown(f'<div class="story-card">📖 {L["story"]}</div>',
            unsafe_allow_html=True)
st.divider()

# ── Code + Visual ─────────────────────────────────────────────
col_code, col_viz = st.columns([11, 10], gap="large")

with col_code:
    st.markdown("### 🐍 Python Code")
    st.code(L["code"], language="python", line_numbers=True)

with col_viz:
    st.markdown("### 🖼️ Output Preview")
    if L["key"] == "animation":
        with st.status("🎬 Rendering animation — first time only…",
                       expanded=False) as s:
            html_str = make_animation_html()
            s.update(label="✅ Animation ready!", state="complete")
        st.iframe(html_str, height=400)
    else:
        preview_fig = PREVIEW[L["key"]]()
        st.pyplot(preview_fig, use_container_width=True)
        plt.close(preview_fig)

st.divider()

# ── Line-by-line breakdown as chat bubbles ────────────────────
st.markdown("### 💬 Line-by-line breakdown")
st.caption("Read these like a friendly tutor explaining each part:")

for icon, text in L["tips"]:
    with st.chat_message("assistant", avatar=icon):
        st.markdown(text)

st.divider()

# ── Challenge ─────────────────────────────────────────────────
st.markdown("### 🎯 Your Challenge")
st.markdown(f'<div class="challenge-card">{L["challenge"]}</div>',
            unsafe_allow_html=True)

# Difficulty rating
st.markdown("")
st.caption("How tricky was this lesson for you?")
st.feedback("faces", key=f"fb_{li}")

st.divider()

# ── Navigation row ────────────────────────────────────────────
nav_l, nav_m, nav_r = st.columns([2, 3, 2])

with nav_l:
    if li > 0:
        if st.button("← Previous lesson", use_container_width=True):
            st.session_state.lesson = li - 1
            st.rerun()

with nav_m:
    if not st.session_state.stars[li]:
        if st.button(f"⭐ Mark Lesson {li+1} Complete!",
                     type="primary", use_container_width=True):
            st.session_state.stars[li] = True
            if not st.session_state.toasted[li]:
                st.session_state.toasted[li] = True
                if sum(st.session_state.stars) == 6:
                    st.balloons()
                else:
                    st.toast(f"⭐ Lesson {li+1} done — great work!",
                             icon="🎉")
            st.rerun()
    else:
        st.success(f"✅ Lesson {li+1} complete!")

with nav_r:
    if li < 5:
        if st.button("Next lesson →", use_container_width=True):
            st.session_state.lesson = li + 1
            st.rerun()
    else:
        st.link_button("📚 Matplotlib gallery →",
                       "https://matplotlib.org/stable/gallery/",
                       use_container_width=True)

# ══════════════════════════════════════════════════════════════
# WIN BANNER
# ══════════════════════════════════════════════════════════════
if sum(st.session_state.stars) == 6:
    st.markdown("""
    <div class="win-banner">
        <div style="font-size:52px;margin-bottom:10px;">
            🏆 🎉 🌈 🎊 ⭐
        </div>
        <h2 style="color:#7a5500;margin:0 0 8px;">
            You completed all 6 lessons — Amazing!
        </h2>
        <p style="font-size:16px;color:#7a5500;line-height:1.8;margin:0;">
            You can now draw skies, place characters, create waves,
            build functions, use polar coordinates, and animate everything!<br>
            <b>Slow and steady wins the race — just like Tommy! 🐢</b>
        </p>
    </div>""", unsafe_allow_html=True)
