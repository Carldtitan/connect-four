# app.py — Streamlit UI with tkinter-like board + falling animation
import time
import streamlit as st
from game import ConnectFour
from ai import ConnectFourAI

st.set_page_config(page_title="Connect Four", page_icon="🎮", layout="centered")

# ------------------- STYLE -------------------
BOARD_BLUE = "#1557d5"
HOLE_COLOR = "#ffffff"
EDGE_COLOR = "#000000"
RED = "#e11d48"
YELLOW = "#facc15"
BG = "#e5e7eb"

CELL = 86
PADDING = 14
STROKE = 3

st.markdown("""
<style>
.legend { color: #6b7280; }
.ctrl { margin-top: .25rem }

/* slim, unlabeled buttons that align with the columns */
.hitrow button {
  background: transparent !important;
  border: 0 !important;
  height: 34px !important;
  width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
  font-size: 20px !important;
  line-height: 1 !important;
  box-shadow: none !important;
  cursor: pointer;
}
.hitrow button:hover {
  background: rgba(255,255,255,0.08) !important;
  border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------- HELPERS -------------------
def render_svg(board, falling=None):
    rows = len(board)
    cols = len(board[0]) if rows else 0
    width = cols * CELL
    height = rows * CELL

    def cx(c): return c * CELL + CELL // 2
    def cy(r): return r * CELL + CELL // 2
    radius = (CELL // 2) - PADDING

    parts = [
        f'<svg width="100%" viewBox="0 0 {width} {height}" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'xmlns="http://www.w3.org/2000/svg" style="background:{BG};">'
    ]
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="{BOARD_BLUE}" />')

    # holes
    for r in range(rows):
        for c in range(cols):
            parts.append(
                f'<circle cx="{cx(c)}" cy="{cy(r)}" r="{radius}" '
                f'fill="{HOLE_COLOR}" stroke="{EDGE_COLOR}" stroke-width="{STROKE}" />'
            )

    # tokens
    for r in range(rows):
        for c in range(cols):
            v = board[r][c]
            if v == 0: continue
            fill = RED if v == 1 else YELLOW
            parts.append(
                f'<circle cx="{cx(c)}" cy="{cy(r)}" r="{radius}" '
                f'fill="{fill}" stroke="{EDGE_COLOR}" stroke-width="{STROKE}" />'
            )

    # falling overlay
    if falling is not None:
        fr, fc, p = falling
        fill = RED if p == 1 else YELLOW
        parts.append(
            f'<circle cx="{cx(fc)}" cy="{cy(fr)}" r="{radius}" '
            f'fill="{fill}" stroke="{EDGE_COLOR}" stroke-width="{STROKE}" />'
        )

    parts.append('</svg>')
    return "".join(parts)

def next_empty_row(board, col):
    for r in range(len(board) - 1, -1, -1):
        if board[r][col] == 0:
            return r
    return None

def animate_drop(container, game, col, player, delay=0.055):
    target_row = next_empty_row(game.board, col)
    if target_row is None:
        return False
    for r in range(0, target_row + 1):
        container.markdown(render_svg(game.board, falling=(r, col, player)), unsafe_allow_html=True)
        time.sleep(delay)
    game.make_move(col, player)
    container.markdown(render_svg(game.board), unsafe_allow_html=True)
    return True

# ------------------- SESSION -------------------
if "game" not in st.session_state:
    st.session_state.game = ConnectFour()
if "ai" not in st.session_state:
    st.session_state.ai = ConnectFourAI(st.session_state.game)

# Human is ALWAYS Red (1). AI is ALWAYS Yellow (2).
HUMAN = 1
AI_PLAYER = 2
st.session_state.ai.set_player_number(AI_PLAYER)

g = st.session_state.game
ai = st.session_state.ai

st.title("Connect Four")

# Controls
c1, c2, _ = st.columns([1,1,2])
with c1:
    ai_starts = st.toggle("AI starts", value=False)
with c2:
    if st.button("Restart Game", help="Start a fresh game", use_container_width=True):
        st.session_state.game = ConnectFour()
        st.session_state.ai   = ConnectFourAI(st.session_state.game)
        st.session_state.ai.set_player_number(AI_PLAYER)  # lock colors

        if ai_starts:
            # AI (Yellow) starts
            st.session_state.game.current_player = AI_PLAYER
            board_placeholder = st.empty()
            board_placeholder.markdown(render_svg(st.session_state.game.board), unsafe_allow_html=True)
            ai_col = st.session_state.ai.get_best_move()
            animate_drop(board_placeholder, st.session_state.game, ai_col, AI_PLAYER)
        else:
            # Human (Red) starts
            st.session_state.game.current_player = HUMAN
        st.rerun()

# Turn label
winner = g.check_winner()
if winner is None and not g.is_board_full():
    st.write(f"**Turn:** {'🔴 Human' if g.current_player == HUMAN else '🟡 AI'}")

# ---------- TOP ROW OF UNLABELED BUTTONS (aligned to columns) ----------
clicked_col = None
hit_row = st.columns(g.COLS, gap="small")
for c in range(g.COLS):
    with hit_row[c]:
        st.markdown('<div class="hitrow">', unsafe_allow_html=True)
        disabled = (g.check_winner() is not None) or g.is_board_full() \
                   or (not g.is_valid_move(c)) or (g.current_player != HUMAN)
        if st.button("↓", key=f"hit-{c}", disabled=disabled):
            clicked_col = c
        st.markdown('</div>', unsafe_allow_html=True)

# Board (SVG)
board_area = st.empty()
board_area.markdown(render_svg(g.board), unsafe_allow_html=True)

# Handle a click
if clicked_col is not None:
    if animate_drop(board_area, g, clicked_col, HUMAN):
        if g.check_winner() is None and not g.is_board_full():
            ai_col = ai.get_best_move()
            animate_drop(board_area, g, ai_col, AI_PLAYER)
    st.rerun()

# End-state messages
winner = g.check_winner()
if winner is not None:
    st.success("You win! 🎉") if winner != AI_PLAYER else st.error("AI wins! 🤖")
elif g.is_board_full():
    st.info("It’s a tie.")

st.markdown("<p class='legend'>Click a column to drop a piece. Red = Human, Yellow = AI.</p>",
            unsafe_allow_html=True)
