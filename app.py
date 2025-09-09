# app.py — Streamlit UI with tkinter-like board + falling animation
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
BG = "#e5e7eb"

CELL = 86                   # px for each cell
PADDING = 14                # padding inside each cell for hole
STROKE = 3

st.markdown("""
    <style>
    .legend { color: #6b7280; }
    .ctrl { margin-top: .25rem }
    .hitrow button {
  background: transparent !important;
  border: 0 !important;
  height: 34px !important;      /* thin bar */
  width: 100% !important;
  font-size: 20px !important;   /* for the arrow */
  line-height: 1 !important;
  box-shadow: none !important;
}
.hitrow button:hover {
  background: rgba(255,255,255,0.08) !important;
  border-radius: 8px !important;
  cursor: pointer;
}

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

    def hole_cx(c): return c * CELL + CELL // 2
    def hole_cy(r): return r * CELL + CELL // 2
    radius = (CELL // 2) - PADDING

    # Start SVG
    parts = [
        f'<svg width="100%" viewBox="0 0 {width} {height}" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'xmlns="http://www.w3.org/2000/svg" style="background:{BG};">'
    ]

    # Board background
    parts.append(
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{BOARD_BLUE}" />'
    )

    # Holes (drawn as white circles to simulate cut-outs)
    for r in range(rows):
        for c in range(cols):
            parts.append(
                f'<circle cx="{hole_cx(c)}" cy="{hole_cy(r)}" r="{radius}" '
                f'fill="{HOLE_COLOR}" stroke="{EDGE_COLOR}" stroke-width="{STROKE}" />'
            )

    # Tokens
    for r in range(rows):
        for c in range(cols):
            v = board[r][c]
            if v == 0:
                continue
            fill = RED if v == 1 else YELLOW
            parts.append(
                f'<circle cx="{hole_cx(c)}" cy="{hole_cy(r)}" r="{radius}" '
                f'fill="{fill}" stroke="{EDGE_COLOR}" stroke-width="{STROKE}" />'
            )

    # Falling overlay (drawn last so it appears on top)
    if falling is not None:
        fr, fc, p = falling
        fill = RED if p == 1 else YELLOW
        parts.append(
            f'<circle cx="{hole_cx(fc)}" cy="{hole_cy(fr)}" r="{radius}" '
            f'fill="{fill}" stroke="{EDGE_COLOR}" stroke-width="{STROKE}" />'
        )

    parts.append('</svg>')
    return "".join(parts)


def next_empty_row(board, col):
    """Return the row index where a token would land in this column, or None if full."""
    for r in range(len(board) - 1, -1, -1):
        if board[r][col] == 0:
            return r
    return None


def animate_drop(container, game, col, player, delay=0.055):
    """
    Show a simple falling animation by redrawing the board with an overlay token
    moving down the target column until the landing row.
    We only modify the true board state at the end (by calling game.make_move).
    """
    target_row = next_empty_row(game.board, col)
    if target_row is None:
        return False

    # Start above the board (visual nicely)
    for r in range(0, target_row + 1):
        svg = render_svg(game.board, falling=(r, col, player))
        container.markdown(svg, unsafe_allow_html=True)
        time.sleep(delay)

    # Commit the real move
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
c1, c2, c3 = st.columns([1,1,2])
with c1:
    ai_starts = st.toggle("AI starts", value=False)
with c2:
    if st.button("Restart Game", help="Start a fresh game", use_container_width=True):
        # reset objects
        st.session_state.game = ConnectFour()
        st.session_state.ai   = ConnectFourAI(st.session_state.game)

        # lock colors again
        st.session_state.ai.set_player_number(AI_PLAYER)

        # set who goes first (no color swap)
        if ai_starts:
            # AI (Yellow, player 2) starts
            st.session_state.game.current_player = AI_PLAYER
            # AI opening move with animation
            board_placeholder = st.empty()
            board_placeholder.markdown(
                render_svg(st.session_state.game.board), unsafe_allow_html=True
            )
            ai_col = st.session_state.ai.get_best_move()
            animate_drop(board_placeholder, st.session_state.game, ai_col, AI_PLAYER)
            # make_move toggles turn to Human automatically
        else:
            # Human (Red, player 1) starts
            st.session_state.game.current_player = HUMAN

        st.rerun()


# Whose turn
winner = g.check_winner()
if winner is None and not g.is_board_full():
    turn = "🔴 Human" if g.current_player == HUMAN else "🟡 AI"
    st.write(f"**Turn:** {turn}")


# Board placeholder (used for animation)
board_area = st.empty()
board_area.markdown(render_svg(g.board), unsafe_allow_html=True)

st.divider()
st.write("Drop a piece:")
drop = st.columns(g.COLS, gap="small")

# ------------------- GAMEPLAY -------------------
if winner is not None:
    if ai.AI != winner:
        st.success("You win! 🎉")
        st.balloons()
    else:
        st.error("AI wins! 🤖")
elif g.is_board_full():
    st.info("It’s a tie.")
else:
    for c in range(g.COLS):
        with drop[c]:
            disabled = (not g.is_valid_move(c)) or (g.current_player != HUMAN)
            if st.button(f"↓ {c+1}", key=f"drop-{c}", disabled=disabled):
                # Human (Red) move
                if animate_drop(board_area, g, c, HUMAN):
                    # AI (Yellow) replies if game not over
                    if g.check_winner() is None and not g.is_board_full():
                        ai_col = ai.get_best_move()
                        animate_drop(board_area, g, ai_col, AI_PLAYER)
                st.rerun()


st.markdown("<p class='legend'>Red = Human, Yellow = AI. Click a column to drop a piece.</p>",
            unsafe_allow_html=True)
