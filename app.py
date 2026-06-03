"""
🐇 The Rabbit & Tortoise Race — Learn Python Visualization
A Streamlit app for kids to learn matplotlib step by step.

Compatible with Streamlit ≥ 1.37 (uses st.iframe for animations,
NOT the deprecated st.components.v1.html).
"""

import streamlit as st
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse, FancyBboxPatch
from matplotlib.animation import FuncAnimation
import tempfile, os, textwrap

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="🐇 Rabbit & Tortoise — Learn Python!",
    page_icon="🐇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# GLOBAL STYLES
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"], .stMarkdown, .stButton, .stTabs,
button, p, span, li, div { font-family: 'Nunito', sans-serif !important; }

/* ── Tab styling ─────────────────────────────── */
.stTabs [data-baseweb="tab-list"]  { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0 !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
}

/* ── Story box ───────────────────────────────── */
.story-box {
    background: linear-gradient(135deg, #fffde7, #fff9c4);
    border-left: 5px solid #fbc02d;
    border-radius: 0 14px 14px 0;
    padding: 14px 18px;
    margin: 10px 0 18px;
    font-size: 15px;
    line-height: 1.7;
    color: #4e3a00;
}

/* ── Explanation card ────────────────────────── */
.expl-row {
    display: flex; gap: 10px; align-items: flex-start;
    background: #f0f4ff;
    border-radius: 10px;
    padding: 9px 13px;
    margin-bottom: 7px;
    font-size: 14px;
    color: #1a2060;
    line-height: 1.5;
    border-left: 3px solid #5c6bc0;
}

/* ── Challenge box ───────────────────────────── */
.challenge-box {
    background: linear-gradient(135deg, #e8f5e9, #dcedc8);
    border: 2px dashed #66bb6a;
    border-radius: 14px;
    padding: 15px 20px;
    margin: 14px 0 4px;
    font-size: 15px;
    color: #1b5e20;
    line-height: 1.6;
}

/* ── Concept tag ─────────────────────────────── */
.concept-tag {
    display: inline-block;
    background: #ede7f6;
    color: #4527a0;
    border-radius: 8px;
    padding: 3px 12px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

/* ── Win banner ──────────────────────────────── */
.win-box {
    background: linear-gradient(135deg, #fff8e1, #ffecb3);
    border: 3px solid #ffa000;
    border-radius: 18px;
    padding: 28px 24px;
    text-align: center;
    margin: 20px 0;
}

/* ── Ref card ────────────────────────────────── */
.ref-card {
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 8px;
    transition: transform 0.15s;
}
.ref-card:hover { transform: translateY(-2px); }

/* ── Star progress ───────────────────────────── */
.star-box {
    background: linear-gradient(135deg, #fffde7, #fff3e0);
    border: 2px solid #ffa000;
    border-radius: 14px;
    padding: 12px 18px;
    text-align: center;
}

/* ── Metric card ─────────────────────────────── */
.metric-card {
    background: white;
    border-radius: 12px;
    border: 1.5px solid #e0e0e0;
    padding: 14px 16px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DRAWING HELPERS  (reused across preview + animation)
# ══════════════════════════════════════════════════════════════
GRASS_GREEN  = "#4CAF50"
DARK_GREEN   = "#2E7D32"
SKY_TOP      = "#64B5F6"
SKY_BOT      = "#B3E5FC"
SUN_COLOR    = "#FFD600"
CLOUD_COLOR  = "#FFFFFF"
HARRY_FUR    = "#F5F5DC"
HARRY_EDGE   = "#C8A96E"
HARRY_EAR    = "#FFCCBC"
TOMMY_SHELL  = "#558B2F"
TOMMY_BODY   = "#33691E"
TRACK_COLOR  = "#D7CCC8"
FINISH_COLOR = "#F44336"


def setup_ax(ax, title=""):
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    # sky gradient via rectangle stack
    for i in range(50):
        t = i / 49
        r = int(100 + (179 - 100) * t)
        g = int(181 + (229 - 181) * t)
        b = int(246 + (252 - 246) * t)
        ax.axhspan(50 + i, 51 + i, color=(r/255, g/255, b/255), zorder=0)
    if title:
        ax.set_title(title, fontsize=15, fontweight="bold",
                     color="#1a237e", pad=10)


def draw_ground(ax):
    # Track
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 12), 100, 12, boxstyle="round,pad=0",
        fc=TRACK_COLOR, ec="none", zorder=1))
    # Grass on top of track
    x = np.linspace(0, 100, 400)
    y_grass = 5 * np.sin(x / 6) + 26
    ax.fill_between(x, 0, y_grass, color=GRASS_GREEN, alpha=0.85, zorder=2)
    ax.plot(x, y_grass, color=DARK_GREEN, lw=1.5, zorder=3)
    # Ground under track
    ax.fill_between([0, 100], [0, 0], [12, 12], color="#8D6E63", zorder=1)


def draw_ground_animated(ax, frame):
    x = np.linspace(0, 100, 400)
    y_grass = 5 * np.sin(x / 6 + frame / 12) + 26
    ax.fill_between(x, 0, y_grass, color=GRASS_GREEN, alpha=0.85, zorder=2)
    ax.plot(x, y_grass, color=DARK_GREEN, lw=1.5, zorder=3)
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 12), 100, 14, boxstyle="round,pad=0",
        fc=TRACK_COLOR, ec="none", zorder=1))
    ax.fill_between([0, 100], [0, 0], [12, 12], color="#8D6E63", zorder=1)


def draw_sun(ax, ray_frame=0):
    sun = plt.Circle((90, 90), 7, color=SUN_COLOR, zorder=5)
    ax.add_patch(sun)
    for a in range(0, 360, 45):
        ang = np.radians(a + ray_frame * 2)
        ax.plot([90 + 8*np.cos(ang), 90 + 11*np.cos(ang)],
                [90 + 8*np.sin(ang), 90 + 11*np.sin(ang)],
                color=SUN_COLOR, lw=2, zorder=5)


def draw_clouds(ax, offset=0):
    for cx, cy, scale in [(18, 85, 1.0), (45, 88, 0.8), (70, 83, 1.2)]:
        ox = (cx + offset) % 105 - 5
        for dx, dy, rx, ry in [(0,0,8,5),(6,2,6,4),(-6,1,5,3)]:
            ax.add_patch(Ellipse((ox+dx, cy+dy), rx*scale*2, ry*scale*2,
                                 color=CLOUD_COLOR, alpha=0.92, zorder=4))


def draw_harry(ax, x, y, sleeping=False, speed_lines=False):
    # Body
    ax.add_patch(plt.Circle((x, y), 5.5, color=HARRY_FUR,
                             ec=HARRY_EDGE, lw=2, zorder=8))
    # Ears
    ax.add_patch(Ellipse((x-2.2, y+8), 2.5, 6,
                         color=HARRY_FUR, ec=HARRY_EDGE, lw=2, zorder=7))
    ax.add_patch(Ellipse((x+2.2, y+8), 2.5, 6,
                         color=HARRY_FUR, ec=HARRY_EDGE, lw=2, zorder=7))
    # Inner ear pink
    ax.add_patch(Ellipse((x-2.2, y+8), 1.2, 3.5,
                         color=HARRY_EAR, zorder=9))
    ax.add_patch(Ellipse((x+2.2, y+8), 1.2, 3.5,
                         color=HARRY_EAR, zorder=9))
    # Eyes
    if sleeping:
        ax.plot([x-2, x-0.8], [y+1.5, y+1.5], color="#5D4037", lw=2, zorder=10)
        ax.plot([x+0.8, x+2], [y+1.5, y+1.5], color="#5D4037", lw=2, zorder=10)
        ax.text(x+5, y+9, "zzz", fontsize=9, color="#9575CD",
                fontstyle="italic", zorder=10)
    else:
        ax.add_patch(plt.Circle((x-1.8, y+1.5), 1, color="#5D4037", zorder=10))
        ax.add_patch(plt.Circle((x+1.8, y+1.5), 1, color="#5D4037", zorder=10))
        ax.add_patch(plt.Circle((x-1.5, y+1.8), 0.4, color="white", zorder=11))
        ax.add_patch(plt.Circle((x+2.1, y+1.8), 0.4, color="white", zorder=11))
    # Nose
    ax.add_patch(plt.Circle((x, y-0.5), 0.7, color="#EF9A9A", zorder=10))
    # Speed lines
    if speed_lines:
        for dy in [-2, 0, 2]:
            ax.plot([x-12, x-7], [y+dy, y+dy],
                    color="#90CAF9", lw=1.5, alpha=0.7, zorder=7)
    ax.text(x-4.5, y-10, "Harry", fontsize=9, fontweight="bold",
            color="#4e342e", zorder=10)


def draw_tommy(ax, x, y, celebrating=False):
    # Shell
    ax.add_patch(Ellipse((x, y+2), 13, 8,
                         color=TOMMY_SHELL, ec=TOMMY_BODY, lw=2, zorder=8))
    # Shell pattern lines
    for dx in [-3, 0, 3]:
        ax.plot([x+dx, x+dx], [y-1, y+5],
                color=TOMMY_BODY, lw=0.8, alpha=0.6, zorder=9)
    ax.plot([x-5, x+5], [y+2, y+2],
            color=TOMMY_BODY, lw=0.8, alpha=0.6, zorder=9)
    # Head
    ax.add_patch(plt.Circle((x+7, y+1), 3.2,
                             color="#8BC34A", ec=TOMMY_BODY, lw=1.5, zorder=8))
    # Eye
    ax.add_patch(plt.Circle((x+8.5, y+2), 0.9, color="#33691E", zorder=10))
    ax.add_patch(plt.Circle((x+8.8, y+2.3), 0.35, color="white", zorder=11))
    # Feet
    for fx, fy in [(x-4, y-3.5), (x-1, y-3.8), (x+2, y-3.8), (x+5, y-3.5)]:
        ax.add_patch(Ellipse((fx, fy), 3, 2,
                             color="#8BC34A", ec=TOMMY_BODY, lw=1, zorder=7))
    if celebrating:
        for _ in range(10):
            rx = x + np.random.uniform(-15, 15)
            ry = y + np.random.uniform(5, 25)
            col = np.random.choice(["#FF5722","#FFEB3B","#4CAF50",
                                    "#2196F3","#9C27B0","#FF9800"])
            ax.add_patch(plt.Circle((rx, ry), 1.2, color=col, zorder=12))
    ax.text(x-2, y-12, "Tommy", fontsize=9, fontweight="bold",
            color="#1B5E20", zorder=10)


def draw_finish_line(ax, fx=88):
    # Chequered post
    ax.plot([fx, fx], [26, 50], color="#212121", lw=3, zorder=6)
    for i in range(8):
        col = "white" if i % 2 == 0 else "#212121"
        ax.add_patch(mpatches.FancyBboxPatch(
            (fx, 26 + i*3), 4, 3, fc=col, ec="#212121", lw=0.5, zorder=6))
    ax.text(fx+5, 46, "FINISH", fontsize=9, fontweight="bold",
            color=FINISH_COLOR, zorder=10)


def draw_flowers(ax):
    colors = ["#F44336","#FF9800","#E91E63","#9C27B0","#FFEB3B"]
    for i, col in enumerate(colors):
        cx = 8 + i * 17
        cy = 35
        for a in range(0, 360, 72):
            ang = np.radians(a)
            ax.add_patch(Ellipse(
                (cx + 3*np.cos(ang), cy + 3*np.sin(ang)),
                4, 2.5, angle=np.degrees(ang),
                color=col, alpha=0.85, zorder=5))
        ax.add_patch(plt.Circle((cx, cy), 1.8, color="#FFEB3B", zorder=6))
    # Stems
    for i in range(5):
        cx = 8 + i * 17
        ax.plot([cx, cx], [26, 32], color=DARK_GREEN, lw=1.5, zorder=4)


def draw_spiral(ax, cx, cy, turns=5, scale=0.7):
    theta = np.linspace(0, turns * 2 * np.pi, 1200)
    r = theta * scale
    ax.plot(cx + r * np.cos(theta), cy + r * np.sin(theta),
            color="#9C27B0", lw=1.5, alpha=0.8, zorder=9)
    # Dream stars
    for _ in range(8):
        sx = cx + np.random.uniform(-20, 20)
        sy = cy + np.random.uniform(5, 25)
        ax.plot(sx, sy, "*", color="#FFEB3B", markersize=8, zorder=10)


# ══════════════════════════════════════════════════════════════
# PREVIEW BUILDERS (static matplotlib figures)
# ══════════════════════════════════════════════════════════════
def preview_sky():
    fig, ax = plt.subplots(figsize=(7, 4))
    setup_ax(ax, "The Rabbit and the Tortoise")
    draw_sun(ax)
    draw_clouds(ax)
    draw_ground(ax)
    ax.text(50, 70, "Canvas ready!", fontsize=16,
            ha="center", fontweight="bold", color="#1a237e",
            bbox=dict(fc="white", ec="#5c6bc0", boxstyle="round,pad=0.5"))
    plt.tight_layout(); return fig


def preview_harry():
    fig, ax = plt.subplots(figsize=(7, 4))
    setup_ax(ax)
    draw_sun(ax)
    draw_clouds(ax)
    draw_ground(ax)
    draw_harry(ax, 22, 42, speed_lines=True)
    plt.tight_layout(); return fig


def preview_wave():
    fig, ax = plt.subplots(figsize=(7, 4))
    setup_ax(ax)
    draw_sun(ax)
    draw_clouds(ax)
    # Animated-style grass
    x = np.linspace(0, 100, 400)
    for phase, alpha in [(0, 0.9), (0.8, 0.5), (1.6, 0.3)]:
        y = 5*np.sin(x/6 + phase) + 26
        ax.fill_between(x, 0, y, color=GRASS_GREEN, alpha=alpha, zorder=2)
    ax.plot(x, 5*np.sin(x/6)+26, color=DARK_GREEN, lw=2, zorder=3)
    ax.add_patch(mpatches.FancyBboxPatch((0,12),100,14,
        boxstyle="round,pad=0",fc=TRACK_COLOR,ec="none",zorder=1))
    ax.fill_between([0,100],[0,0],[12,12],color="#8D6E63",zorder=1)
    draw_harry(ax, 22, 42, speed_lines=True)
    draw_tommy(ax, 55, 33)
    plt.tight_layout(); return fig


def preview_flowers():
    fig, ax = plt.subplots(figsize=(7, 4))
    setup_ax(ax)
    draw_sun(ax)
    draw_clouds(ax)
    draw_ground(ax)
    draw_flowers(ax)
    draw_tommy(ax, 60, 33)
    plt.tight_layout(); return fig


def preview_spiral():
    fig, ax = plt.subplots(figsize=(7, 4))
    setup_ax(ax)
    draw_sun(ax)
    draw_clouds(ax)
    draw_ground(ax)
    # Harry sleeping mid-track
    draw_harry(ax, 55, 42, sleeping=True)
    # Dream bubble
    ax.add_patch(plt.Circle((72, 68), 16,
                             fc="#EDE7F6", ec="#9C27B0", lw=2,
                             alpha=0.9, zorder=8))
    draw_spiral(ax, 72, 68, turns=3, scale=0.45)
    # Bubble connector dots
    for r, (ox, oy) in zip([2.5, 1.8, 1.2],
                           [(63, 57), (66, 60), (68, 63)]):
        ax.add_patch(plt.Circle((ox, oy), r,
                               fc="#EDE7F6", ec="#9C27B0", lw=1.5, zorder=8))
    plt.tight_layout(); return fig


def preview_animation():
    fig, ax = plt.subplots(figsize=(7, 4))
    setup_ax(ax)
    draw_sun(ax, ray_frame=5)
    draw_clouds(ax, offset=8)
    draw_ground_animated(ax, 30)
    draw_harry(ax, 30, 42, sleeping=True)
    draw_tommy(ax, 80, 33, celebrating=True)
    draw_finish_line(ax, 88)
    ax.text(50, 75, "Slow & Steady Wins the Race!",
            fontsize=13, ha="center", fontweight="bold",
            color="#FF6F00",
            bbox=dict(fc="#FFFDE7", ec="#FFA000",
                      boxstyle="round,pad=0.5"), zorder=15)
    plt.tight_layout(); return fig


PREVIEW_FNS = {
    "sky": preview_sky,
    "harry": preview_harry,
    "wave": preview_wave,
    "flowers": preview_flowers,
    "spiral": preview_spiral,
    "animation": preview_animation,
}

# ══════════════════════════════════════════════════════════════
# ANIMATION BUILDER  (saved to temp HTML, shown via st.iframe)
# ══════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="Building animation...")
def build_animation_html():
    fig, ax = plt.subplots(figsize=(9, 5.2))
    np.random.seed(42)
    confetti_pos = [(np.random.uniform(5,95), np.random.uniform(30,90),
                     np.random.choice(["#FF5722","#FFEB3B","#4CAF50",
                                       "#2196F3","#9C27B0","#FF9800"]))
                    for _ in range(18)]

    def update(frame):
        ax.clear()
        setup_ax(ax)

        # Sun with rotating rays
        draw_sun(ax, ray_frame=frame)
        # Drifting clouds
        draw_clouds(ax, offset=frame * 0.15)

        # Animated grass
        draw_ground_animated(ax, frame)

        if frame < 55:
            # Scene 1: Harry sprints
            hx = min(10 + frame * 1.4, 75)
            draw_harry(ax, hx, 42, speed_lines=True)
            draw_tommy(ax, 12, 33)
            ax.text(50, 82, "Harry races ahead!", fontsize=13,
                    ha="center", fontweight="bold", color="#1565C0",
                    bbox=dict(fc="white", ec="#1565C0",
                              boxstyle="round,pad=0.4"))

        elif frame < 110:
            # Scene 2: Harry sleeps, Tommy walks
            draw_harry(ax, 75, 42, sleeping=True)
            # Dream bubble
            bx, by = 72, 70
            ax.add_patch(plt.Circle((bx, by), 14,
                                    fc="#EDE7F6", ec="#9C27B0",
                                    lw=2, alpha=0.92, zorder=8))
            spiral_turns = min(1 + (frame - 55) / 20, 4)
            draw_spiral(ax, bx, by, turns=spiral_turns, scale=0.38)
            for r, (ox, oy) in zip([2.2,1.6,1.1],
                                   [(66,59),(68.5,62),(70.5,65)]):
                ax.add_patch(plt.Circle((ox,oy), r,
                                        fc="#EDE7F6", ec="#9C27B0",
                                        lw=1.5, zorder=8))
            # Tommy walks
            tx = min(12 + (frame - 55) * 1.1, 88)
            draw_tommy(ax, tx, 33)
            ax.text(50, 82, "Tommy keeps walking...", fontsize=13,
                    ha="center", fontweight="bold", color="#2E7D32",
                    bbox=dict(fc="white", ec="#2E7D32",
                              boxstyle="round,pad=0.4"))
            draw_flowers(ax)

        else:
            # Scene 3: Tommy wins!
            draw_harry(ax, 75, 42, sleeping=True)
            draw_tommy(ax, 90, 33, celebrating=False)
            draw_finish_line(ax, 89)
            # Confetti burst
            prog = min((frame - 110) / 40, 1.0)
            for i, (cx, cy, col) in enumerate(confetti_pos):
                if i / len(confetti_pos) < prog:
                    ax.add_patch(plt.Circle((cx, cy), 1.4,
                                            color=col, zorder=14))
            ax.text(50, 78, "Slow & Steady Wins the Race!",
                    fontsize=14, ha="center", fontweight="bold",
                    color="#FF6F00",
                    bbox=dict(fc="#FFFDE7", ec="#FFA000",
                              boxstyle="round,pad=0.5"), zorder=15)

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
        id=1, emoji="🌈", output="sky",
        title="Drawing the Sky",
        concept="Setting up the canvas",
        color="#1565C0", badge_bg="#e3f0fb", badge_fg="#1565C0",
        story="Harry the Rabbit wants to draw a racetrack! Every picture "
              "starts with setting up the canvas — our drawing surface. "
              "Let's make a beautiful sky background!",
        code=textwrap.dedent("""\
            import matplotlib.pyplot as plt
            import numpy as np

            # Create the figure (whole image) and axes (drawing area)
            fig, ax = plt.subplots(figsize=(10, 6))

            # Paint the background sky blue
            ax.set_facecolor("skyblue")

            # Set boundaries: our world is 0–100 wide, 0–100 tall
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)

            # Add a title at the top
            ax.set_title("The Rabbit and the Tortoise",
                         fontsize=16, fontweight='bold')

            plt.tight_layout()
            plt.show()
        """),
        explanation=[
            ("🖼️", "plt.subplots() creates our canvas — fig is the whole picture, ax is where we draw"),
            ("🎨", "set_facecolor() paints the background — try 'lightgreen' or 'lightyellow'!"),
            ("📏", "set_xlim(0,100) and set_ylim(0,100) define a 100×100 coordinate grid"),
            ("🏷️", "set_title() places a title above the picture"),
        ],
        challenge="🎯 Change 'skyblue' to 'lightyellow' — you get a sunset sky!",
    ),
    dict(
        id=2, emoji="🐇", output="harry",
        title="Drawing Harry the Rabbit",
        concept="ax.plot() — placing markers",
        color="#E65100", badge_bg="#fff3e0", badge_fg="#e65100",
        story="Now let's put Harry on the racetrack! We use ax.plot() with "
              "a circle marker for his body and ax.text() to write his name.",
        code=textwrap.dedent("""\
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_facecolor("skyblue")
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)

            # Draw the ground line
            ax.plot([0, 100], [15, 15],
                    color='brown', linewidth=6)

            # Place Harry at (20, 50)
            # 'o' = circle  |  markersize = how big
            ax.plot(20, 50, 'o',
                    markersize=30,
                    color='#F5F5DC',
                    markeredgecolor='#C8A96E',
                    markeredgewidth=2)

            # Write his name below
            ax.text(14, 38, "Harry",
                    fontsize=13, fontweight='bold',
                    color='#4e342e')

            plt.tight_layout()
            plt.show()
        """),
        explanation=[
            ("📍", "ax.plot(x, y) places a point at coordinate (x, y) on the canvas"),
            ("⭕", "'o' = circle marker — try 's' (square), '^' (triangle), '*' (star)!"),
            ("📐", "markersize controls the size — bigger number = bigger dot"),
            ("✏️", "ax.text(x, y, 'words') writes text at any (x, y) position"),
        ],
        challenge="🎯 Change 20 to 50 in ax.plot(20, 50, ...) — Harry moves to the middle!",
    ),
    dict(
        id=3, emoji="〰️", output="wave",
        title="Making Grass Waves",
        concept="NumPy arrays + np.sin()",
        color="#2E7D32", badge_bg="#e8f5e9", badge_fg="#1b5e20",
        story="The racetrack has wavy green hills! We use NumPy to make "
              "hundreds of x-values, then the sine function to make them go "
              "up and down like waves.",
        code=textwrap.dedent("""\
            import matplotlib.pyplot as plt
            import numpy as np

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_facecolor("skyblue")
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)

            # 400 evenly-spaced x values from 0 to 100
            x = np.linspace(0, 100, 400)

            # y = wavy line!
            # 5  → wave height  (amplitude)
            # /6 → wave width   (frequency)
            # +26 → moves wave up or down
            y = 5 * np.sin(x / 6) + 26

            # Fill the area below the wave with green
            ax.fill_between(x, 0, y,
                            color='#4CAF50', alpha=0.85)
            ax.plot(x, y, color='#2E7D32', linewidth=2)

            plt.tight_layout()
            plt.show()
        """),
        explanation=[
            ("📊", "np.linspace(0, 100, 400) makes 400 evenly-spaced numbers between 0 and 100"),
            ("🌊", "np.sin() creates a wave — the 5 in front controls the HEIGHT"),
            ("↔️",  "Dividing x by 6 controls the WIDTH — try x/2 (narrow) or x/15 (wide)"),
            ("🎨", "fill_between() fills the area under the line with a solid color"),
        ],
        challenge="🎯 Change the 5 before np.sin to 12 — the hills become mountains!",
    ),
    dict(
        id=4, emoji="🌸", output="flowers",
        title="Flower Garden",
        concept="Functions + for loops",
        color="#880E4F", badge_bg="#fce4ec", badge_fg="#880e4f",
        story="Tommy walks past a beautiful flower garden. Each flower uses "
              "a reusable function — we write the recipe once and bake 5 "
              "flowers with one loop!",
        code=textwrap.dedent("""\
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.patches import Ellipse

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_facecolor("skyblue")
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)

            # ── Define a function: recipe for ONE flower ──────
            def draw_flower(ax, cx, cy, color):
                # 5 petals, equally spaced (360/5 = 72 degrees)
                for angle in range(0, 360, 72):
                    rad = np.radians(angle)
                    px = cx + 3 * np.cos(rad)
                    py = cy + 3 * np.sin(rad)
                    ax.add_patch(Ellipse(
                        (px, py), 4, 2.5,
                        angle=angle, color=color, alpha=0.85))
                # Yellow centre
                ax.add_patch(plt.Circle((cx, cy), 1.8,
                                        color='#FFEB3B'))

            # ── Call the function 5 times (a loop!) ───────────
            flower_colors = ['red','orange','#E91E63','#9C27B0','#FFEB3B']
            for i, color in enumerate(flower_colors):
                cx = 8 + i * 17
                draw_flower(ax, cx, 35, color)

            plt.tight_layout()
            plt.show()
        """),
        explanation=[
            ("🔧", "def draw_flower(): creates a reusable function — write once, use many times!"),
            ("🌸", "Each petal is an Ellipse patch placed around the centre using cos() and sin()"),
            ("🔁", "for i, color in enumerate(flower_colors): loops over both index AND value"),
            ("📋", "A list of colors gives each flower a different color automatically"),
        ],
        challenge="🎯 Change range(0, 360, 72) to range(0, 360, 60) — flowers get 6 petals!",
    ),
    dict(
        id=5, emoji="💤", output="spiral",
        title="Harry's Dream Spiral",
        concept="Polar coordinates",
        color="#4527A0", badge_bg="#ede7f6", badge_fg="#4527a0",
        story="Harry falls asleep and dreams in spirals! Polar coordinates "
              "use an angle and a growing distance — as the angle increases, "
              "so does the radius, making a perfect spiral.",
        code=textwrap.dedent("""\
            import matplotlib.pyplot as plt
            import numpy as np

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_facecolor("skyblue")
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)

            # Draw the dream bubble
            dream = plt.Circle((72, 68), 16,
                                facecolor='#EDE7F6',
                                edgecolor='#9C27B0',
                                linewidth=2, alpha=0.9)
            ax.add_patch(dream)

            # ── Polar coordinates ─────────────────────────────
            # theta = the angle (goes from 0 to 5 full rotations)
            theta = np.linspace(0, 5 * 2 * np.pi, 1000)

            # r = radius — grows bigger as theta increases!
            r = theta * 0.45

            # Convert polar → x, y
            x = 72 + r * np.cos(theta)
            y = 68 + r * np.sin(theta)

            ax.plot(x, y, color='#9C27B0', linewidth=1.5)

            plt.tight_layout()
            plt.show()
        """),
        explanation=[
            ("🌀", "r = theta means the radius GROWS with angle — that's what makes a spiral!"),
            ("📐", "np.cos(theta) and np.sin(theta) convert angle to x and y positions"),
            ("🔄", "5 * 2 * np.pi = 5 full rotations (one full circle = 2π)"),
            ("⚙️", "Multiplying theta by 0.45 controls how quickly the spiral expands"),
        ],
        challenge="🎯 Change 5 * 2 * np.pi to 10 * 2 * np.pi — the dream gets much bigger!",
    ),
    dict(
        id=6, emoji="🏆", output="animation",
        title="The Full Race — Animated!",
        concept="FuncAnimation — bring it to life",
        color="#00695C", badge_bg="#e0f7f4", badge_fg="#00695c",
        story="Tommy the Tortoise crosses the finish line! We combine ALL "
              "our skills and add animation — the update() function is called "
              "once per frame, like 160 frames in a cartoon!",
        code=textwrap.dedent("""\
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.animation import FuncAnimation
            import streamlit as st

            fig, ax = plt.subplots(figsize=(9, 5))

            def update(frame):
                ax.clear()
                ax.set_xlim(0, 100)
                ax.set_ylim(0, 100)
                ax.set_facecolor("skyblue")
                ax.axis("off")

                # Moving grass
                x = np.linspace(0, 100, 400)
                y = 5 * np.sin(x / 6 + frame / 12) + 26
                ax.fill_between(x, 0, y,
                                color='#4CAF50', alpha=0.85)

                if frame < 55:
                    # Scene 1: Harry runs fast
                    harry_x = 10 + frame * 1.4
                    ax.plot(harry_x, 42, 'o', ms=20,
                            color='#F5F5DC')
                    ax.text(50, 80, "Harry races ahead!",
                            ha='center', fontsize=13,
                            fontweight='bold')

                elif frame < 110:
                    # Scene 2: Harry sleeps, Tommy walks
                    ax.plot(75, 42, 'o', ms=20,
                            color='#F5F5DC')
                    ax.text(80, 55, "zzz", fontsize=11)

                    tommy_x = 12 + (frame - 55) * 1.1
                    ax.plot(tommy_x, 35, 's', ms=16,
                            color='#558B2F')
                    ax.text(50, 80, "Tommy keeps walking...",
                            ha='center', fontsize=13,
                            fontweight='bold')

                else:
                    # Scene 3: Tommy wins!
                    ax.plot(88, 35, 's', ms=18,
                            color='#558B2F')
                    ax.text(50, 78,
                            "Slow & Steady Wins the Race!",
                            ha='center', fontsize=14,
                            fontweight='bold', color='#FF6F00')

            # 160 frames, 65ms between each = about 10 seconds
            ani = FuncAnimation(fig, update,
                                frames=160, interval=65)

            # Save and show in Streamlit using st.iframe
            import tempfile
            with tempfile.NamedTemporaryFile(
                    delete=False, suffix='.html') as f:
                ani.save(f.name, writer='html')
                html_str = open(f.name).read()

            # st.iframe works with raw HTML strings
            st.iframe(html_str, height=500)
        """),
        explanation=[
            ("🎬", "FuncAnimation calls update() 160 times — like frames in a cartoon!"),
            ("🧹", "ax.clear() wipes the canvas each frame so we can draw fresh"),
            ("📺", "frames=160 means 160 pictures; interval=65 means 65ms between each"),
            ("🚶", "tommy_x = 12 + (frame-55)*1.1 increases a little each frame → movement!"),
        ],
        challenge="🎯 Change interval=65 to interval=30 — the whole race runs twice as fast!",
    ),
]

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
if "stars" not in st.session_state:
    st.session_state.stars = [False] * 6

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("## 🐇 The Rabbit & Tortoise Race 🐢")
    st.caption("Learn Python data visualisation step by step through a classic fable!")

with col_h2:
    total = sum(st.session_state.stars)
    st.markdown(f"""
    <div class="star-box">
        <div style="font-size:24px; letter-spacing:2px;">
            {"⭐"*total}{"☆"*(6-total)}
        </div>
        <div style="font-size:12px; color:#7a5500;
                    font-weight:800; margin-top:4px;">
            {total} / 6 Lessons Complete
        </div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab_labels = [
    ("⭐" if st.session_state.stars[i] else l["emoji"]) + f"  L{i+1}: {l['title']}"
    for i, l in enumerate(LESSONS)
]
tabs = st.tabs(tab_labels)

for ti, tab in enumerate(tabs):
    with tab:
        L = LESSONS[ti]

        # ── Header ───────────────────────────────────────────
        st.markdown(
            f'<span class="concept-tag">'
            f'Lesson {L["id"]} · {L["concept"]}'
            f'</span>', unsafe_allow_html=True)
        st.markdown(f"### {L['emoji']} {L['title']}")
        st.markdown(
            f'<div class="story-box">📖 {L["story"]}</div>',
            unsafe_allow_html=True)

        # ── Code + Preview ────────────────────────────────────
        col_code, col_viz = st.columns([11, 10], gap="large")

        with col_code:
            st.markdown("##### 🐍 Python Code")
            st.code(L["code"], language="python")

        with col_viz:
            st.markdown("##### 🖼️ What you'll see")

            if L["output"] == "animation":
                with st.spinner("🎬 Rendering animation (first time only)..."):
                    html_str = build_animation_html()
                # Use st.iframe — works with raw HTML, no deprecated components
                st.iframe(html_str, height=420)
            else:
                preview_fig = PREVIEW_FNS[L["output"]]()
                st.pyplot(preview_fig, use_container_width=True)
                plt.close(preview_fig)

            # ── Explanations ──────────────────────────────────
            st.markdown("##### 📚 Line-by-line breakdown")
            for icon, text in L["explanation"]:
                st.markdown(
                    f'<div class="expl-row">'
                    f'<span style="font-size:18px;flex-shrink:0">{icon}</span>'
                    f'<span>{text}</span>'
                    f'</div>',
                    unsafe_allow_html=True)

        # ── Challenge ─────────────────────────────────────────
        st.markdown(
            f'<div class="challenge-box">{L["challenge"]}</div>',
            unsafe_allow_html=True)

        # ── Mark complete ─────────────────────────────────────
        st.markdown("")
        c1, c2, _ = st.columns([2, 2, 4])
        with c1:
            if not st.session_state.stars[ti]:
                if st.button(f"⭐ Mark Lesson {ti+1} Done!",
                             key=f"done_{ti}", type="primary"):
                    st.session_state.stars[ti] = True
                    st.rerun()
            else:
                st.success(f"✅ Lesson {ti+1} complete!")
        with c2:
            if ti < 5 and st.session_state.stars[ti]:
                st.info(f"👉 Head to Lesson {ti+2}!")

# ══════════════════════════════════════════════════════════════
# QUICK REFERENCE TABLE
# ══════════════════════════════════════════════════════════════
st.divider()
st.markdown("### 📋 Quick Reference — All Commands")

ref_rows = [
    ("plt.subplots(figsize=...)", "Create the figure + axes canvas",        LESSONS[0]["color"], 0),
    ("ax.set_facecolor(color)",   "Paint the background color",              LESSONS[0]["color"], 0),
    ("ax.set_xlim() / ylim()",    "Set coordinate boundaries",               LESSONS[0]["color"], 0),
    ("ax.plot(x, y, marker)",     "Draw points, lines, or markers",          LESSONS[1]["color"], 1),
    ("ax.text(x, y, s)",          "Write text at any coordinate",            LESSONS[1]["color"], 1),
    ("ax.add_patch(patch)",       "Add shapes (Circle, Ellipse, etc.)",      LESSONS[1]["color"], 1),
    ("np.linspace(a, b, n)",      "n evenly-spaced numbers from a to b",     LESSONS[2]["color"], 2),
    ("np.sin() / np.cos()",       "Wave & circular math functions",          LESSONS[2]["color"], 2),
    ("ax.fill_between(x, y1, y2)","Fill area between two curves",           LESSONS[2]["color"], 2),
    ("def func(args):",           "Define a reusable function",              LESSONS[3]["color"], 3),
    ("for i in range(n):",        "Loop n times",                            LESSONS[3]["color"], 3),
    ("FuncAnimation(fig, fn, n)", "Call fn() n times to animate",           LESSONS[5]["color"], 5),
    ("st.iframe(html_str)",       "Embed HTML/animation in Streamlit",       LESSONS[5]["color"], 5),
]

cols_per_row = 3
rows = [ref_rows[i:i+cols_per_row] for i in range(0, len(ref_rows), cols_per_row)]
for row in rows:
    rcols = st.columns(cols_per_row)
    for ci, (cmd, desc, color, lesson_idx) in enumerate(row):
        unlocked = sum(st.session_state.stars) > lesson_idx
        with rcols[ci]:
            st.markdown(f"""
            <div class="ref-card"
                 style="background:{color}15;
                        border:1.5px solid {color}55;
                        opacity:{'1.0' if unlocked else '0.35'}">
                <code style="font-size:12px;color:{color};
                             font-weight:800;word-break:break-all;">
                    {cmd}
                </code>
                <div style="font-size:12px;color:#555;margin-top:4px;">
                    {desc}
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# WIN BANNER
# ══════════════════════════════════════════════════════════════
if sum(st.session_state.stars) == 6:
    st.markdown("""
    <div class="win-box">
        <div style="font-size:52px; margin-bottom:10px;">
            🏆 🎉 🌈 🎊 ⭐
        </div>
        <h2 style="color:#7a5500; margin:0 0 8px;">
            You finished ALL 6 lessons — Amazing!
        </h2>
        <p style="font-size:16px; color:#7a5500; margin:0; line-height:1.7;">
            You can now draw backgrounds, place characters, create waves,
            build functions, use polar coordinates, and animate everything.<br>
            <strong>Slow and steady wins the race — just like Tommy! 🐢</strong>
        </p>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🚀 Getting Started")
    st.markdown("""
**Install dependencies:**
```bash
pip install streamlit matplotlib numpy
```
**Run the app:**
```bash
streamlit run app.py
```
---
""")
    st.markdown("## 📦 What You're Learning")
    topics = [
        ("🖼️", "Matplotlib canvas setup"),
        ("📍", "Placing points & shapes"),
        ("〰️", "NumPy arrays & sine waves"),
        ("🌸", "Writing & calling functions"),
        ("🔁", "Loops & repetition"),
        ("🌀", "Polar coordinates"),
        ("🎬", "FuncAnimation basics"),
        ("🌐", "Streamlit st.iframe"),
    ]
    for icon, topic in topics:
        st.markdown(f"{icon} {topic}")

    st.divider()
    st.markdown("## 🎨 Colour Cheat Sheet")
    colors = {
        "skyblue": "#87CEEB", "lightgreen": "#90EE90",
        "lightyellow": "#FFFFE0", "lightcoral": "#F08080",
        "lavender": "#E6E6FA", "peachpuff": "#FFDAB9",
    }
    for name, hex_c in colors.items():
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;'
            f'margin-bottom:5px;">'
            f'<div style="width:20px;height:20px;border-radius:4px;'
            f'background:{hex_c};border:1px solid #ccc;"></div>'
            f'<code style="font-size:12px;">{name!r}</code>'
            f'</div>', unsafe_allow_html=True)

    st.divider()
    st.caption("Built with ❤️ using Streamlit + Matplotlib")
