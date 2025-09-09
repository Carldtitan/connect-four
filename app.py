# app.py — Click-on-column UI + tkinter-like board + falling animation
import time
import streamlit as st
from game import ConnectFour
from ai import ConnectFourAI

st.set_page_config(page_title="Connect Four", page_icon="🎮", layout="centered")

# ------------------- STYLE -------------------
BOARD_BLUE = "#1557d5"      # classic board blue
HOLE_COLOR = "#ffffff"
EDGE_COLOR = "#000000"
RED = "#e11d48"             # red disc
YELLOW = "#facc15"          # yellow disc
BG = "#e5e7eb"              # outer background (behind board)

CELL = 86                   # px per cell
PADDING = 14                # "hole" padding inside each cell
STROKE = 3

st.markdown("""
    <style>
    /* subtle, thin click target row above the board (one per column) */
    .hitrow button {
      background: transparent !important;
      border: 0 !important;
      height: 34px !important;      /* thin bar */
      width: 100% !important;
      font-size: 0 !important;      /* hide text */
      box-shadow: none !important;
    }
    .hitrow button:hover {
      background: rgba(255,255,255,0.08) !important; /* gentle hover cue */
      border-radius: 8px !important;
      cursor: pointer;
    }

    .legend { color: #6b7280; }
    </style>
""", unsafe_allow_html=True)


# ------------------- HELPERS -------------------
def render_svg(board, falling=None):
    """
    Draw the board as an SVG like tkinter:
      - blue rectangle with circular holes (white)
      - tokens with black stroke
      - optional falling=(row, col, player) draws a token overlay
    """
    rows = len(board)
    cols = len(board[0]) if rows else 0
    width = cols * CELL
    height = rows * CELL

    def cx(c): return c * CELL + CELL // 2
    def cy(r): return r * CELL + CELL // 2
    radius = (CELL // 2) - PADDING

    parts = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" style="background:{BG};">'
    ]

    # blue board
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="{BOARD_BLUE}" />')

    # holes
    for r in range(rows):
        for c in range(cols):
            parts.append(
                f'<circle cx="{cx(c)}" cy="{cy(r)}" r="{radius}" '
                f'fill="{HOLE_COLOR}" stroke="{EDGE_COLOR}" stroke-width="{STROKE}" />'
            )

    # placed tokens
    for r in range(rows):
        for c in range(cols):
            v = board[r][c]
            if v == 0:
                continue
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
    """Redraw the SVG with a falling overlay until the landing row."""
    target_row = next_empty_row(game.board, col)
    if target_row is None:
        return False

    for r in range(0, target_row + 1):
        container.markdown(render_svg(game.board, falling=(r, col, player)), unsafe_allow_html=True)
        time.sleep(delay)

    # Commit actual move (make_move also toggles current_player)
    ok = game.make_move(col, player)
    container.markdown(render_svg(game.board), unsafe_allow_html=True)
    return ok


# ------------------- SESSION -------------------
if "game" not in st.session_state:
    st.session_state.game = ConnectFour()
if "ai" not in st.session_state:
    st.session_state.ai = ConnectFourAI(st.session_state.game)
    st.session_state.ai.set_player_number(2)  # AI is player 2 (Yellow)

g = st.session_state.game
ai = st.session_state.ai
human = 1 if ai.AI == 2 else 2

st.title("Connect Four")

# Controls
c1, c2, _ = st.columns([1,1,2])
with c1:
    ai_starts = st.toggle("AI starts", value=False)
with c2:
    if st.button("Restart Game", use_container_width=True):
        st.session_state.game = ConnectFour()
        st.session_state.ai   = ConnectFourAI(st.session_state.game)
        if ai_starts:
            st.session_state.ai.set_player_number(1)      # AI = Red
            st.session_state.game.current_player = 1
            # prime the board then animate AI opening
            board_placeholder = st.empty()
            board_placeholder.markdown(render_svg(st.session_state.game.board), unsafe_allow_html=True)
            ai_col = st.session_state.ai.get_best_move()
            animate_drop(board_placeholder, st.session_state.game, ai_col, 1)
        else:
            st.session_state.ai.set_player_number(2)      # AI = Yellow
            st.session_state.game.current_player = 1      # Human starts
        st.rerun()

# Status
winner = g.check_winner()
if winner is None and not g.is_board_full():
    turn = "🔴 Human" if g.current_player == human else "🟡 AI"
    st.write(f"**Turn:** {turn}")

# ---------- CLICK TARGET ROW (one invisible button per column) ----------
hit = None
hitrow = st.columns(g.COLS, gap="small")
for c in range(g.COLS):
    with hitrow[c]:
        st.markdown('<div class="hitrow">', unsafe_allow_html=True)
        enabled = (winner is None) and (not g.is_board_full()) and (g.current_player == human) and g.is_valid_move(c)
        if st.button(" ", key=f"hit-{c}", disabled=not enabled):
            hit = c
        st.markdown('</div>', unsafe_allow_html=True)

# Board area (SVG) — rendered after the hit row so it sits visually *under* the click targets
board_area = st.empty()
board_area.markdown(render_svg(g.board), unsafe_allow_html=True)

# Handle a click on a column
if hit is not None:
    if animate_drop(board_area, g, hit, human):
        if g.check_winner() is None and not g.is_board_full():
            ai_col = ai.get_best_move()
            animate_drop(board_area, g, ai_col, ai.AI)
    st.rerun()

# Footer
st.markdown("<p class='legend'>Click a column to drop a piece. Red = Human, Yellow = AI.</p>",
            unsafe_allow_html=True)
