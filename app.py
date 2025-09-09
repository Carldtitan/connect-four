# app.py — Streamlit UI with a clickable Connect Four board
# Human is always Red (player 1). AI is always Yellow (player 2).

import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates
from game import ConnectFour
from ai import ConnectFourAI

st.set_page_config(page_title="Connect Four", page_icon="🎮", layout="centered")

# ------------------- VISUAL CONSTANTS -------------------
BOARD_BLUE = "#1557d5"
HOLE_COLOR = "#ffffff"
EDGE_COLOR = "#000000"
RED       = "#e11d48"
YELLOW    = "#facc15"

CELL    = 86      # pixels per cell (controls image width/height)
PADDING = 14      # hole inset from the cell edge
STROKE  = 3       # black outline width

# ------------------- HELPERS -------------------
def next_empty_row(board, col):
    """Return the row index where a token would land in this column, or None if full."""
    for r in range(board.shape[0] - 1, -1, -1):
        if board[r, col] == 0:
            return r
    return None

def draw_board_img(board):
    """Draw the full board as a raster image (used for the clickable component)."""
    rows, cols = board.shape
    w, h = cols * CELL, rows * CELL
    img = Image.new("RGBA", (w, h), BOARD_BLUE)
    d = ImageDraw.Draw(img)

    radius = (CELL // 2) - PADDING

    # holes
    for r in range(rows):
        for c in range(cols):
            cx = c * CELL + CELL // 2
            cy = r * CELL + CELL // 2
            bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
            d.ellipse(bbox, fill=HOLE_COLOR, outline=EDGE_COLOR, width=STROKE)

    # tokens
    for r in range(rows):
        for c in range(cols):
            v = int(board[r, c])
            if v == 0:
                continue
            color = RED if v == 1 else YELLOW
            cx = c * CELL + CELL // 2
            cy = r * CELL + CELL // 2
            bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
            d.ellipse(bbox, fill=color, outline=EDGE_COLOR, width=STROKE)

    return img

# ------------------- SESSION -------------------
if "game" not in st.session_state:
    st.session_state.game = ConnectFour()
if "ai" not in st.session_state:
    st.session_state.ai = ConnectFourAI(st.session_state.game)

# Lock colors: Human = 1 (red), AI = 2 (yellow)
HUMAN = 1
AI_PLAYER = 2
st.session_state.ai.set_player_number(AI_PLAYER)

g = st.session_state.game
ai = st.session_state.ai

# ------------------- UI HEADER -------------------
st.title("Connect Four")
c1, c2, _ = st.columns([1, 1, 2])
with c1:
    ai_starts = st.toggle("AI starts", value=False)
with c2:
    if st.button("Restart Game", use_container_width=True):
        # reset objects
        st.session_state.game = ConnectFour()
        st.session_state.ai   = ConnectFourAI(st.session_state.game)
        st.session_state.ai.set_player_number(AI_PLAYER)  # keep AI = yellow

        # decide who starts (do not swap colors)
        if ai_starts:
            st.session_state.game.current_player = AI_PLAYER
            # let AI make the opening move instantly
            first_col = st.session_state.ai.get_best_move()
            st.session_state.game.make_move(first_col, AI_PLAYER)
        else:
            st.session_state.game.current_player = HUMAN
        st.rerun()

# Status line
winner = g.check_winner()
if winner is None and not g.is_board_full():
    st.write(f"**Turn:** {'🔴 Human' if g.current_player == HUMAN else '🟡 AI'}")

# ------------------- CLICKABLE BOARD -------------------
# Draw once; pass 1:1 pixels so x//CELL maps perfectly to a column
img = draw_board_img(g.board)
evt = streamlit_image_coordinates(img, width=img.width, key="board-click")

# Handle a click on the board (human turn only)
if evt and (winner is None) and (g.current_player == HUMAN) and (not g.is_board_full()):
    x = evt["x"]                # pixel x within the displayed image
    col = int(x // CELL)        # 0..6
    if 0 <= col < g.COLS and g.is_valid_move(col):
        if g.make_move(col, HUMAN):
            # AI replies if game not over
            if g.check_winner() is None and not g.is_board_full():
                ai_col = ai.get_best_move()
                g.make_move(ai_col, AI_PLAYER)
        st.rerun()

# ------------------- END-STATE MESSAGES -------------------
winner = g.check_winner()
if winner is not None:
    st.success("You win! 🎉") if winner != AI_PLAYER else st.error("AI wins! 🤖")
elif g.is_board_full():
    st.info("It’s a tie.")

st.caption("Click a column to drop a piece. Red = Human, Yellow = AI.")
