# app.py — Clickable board (no bottom buttons), clean turn logic
import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates
from game import ConnectFour
from ai import ConnectFourAI

st.set_page_config(page_title="Connect Four", page_icon="🎮", layout="centered")

# ----- Visual constants (same look as your tkinter board) -----
BOARD_BLUE = "#1557d5"
HOLE_COLOR = "#ffffff"
EDGE_COLOR = "#000000"
RED       = "#e11d48"
YELLOW    = "#facc15"
BG        = "#0f172a"     # page bg is dark; board has its own bg

CELL    = 86              # px per cell
PADDING = 14              # hole inset
STROKE  = 3
RADIUS  = (CELL // 2) - PADDING

# ----- Draw the whole board as a PIL image -----
def draw_board_img(board):
    rows, cols = board.shape
    w, h = cols * CELL, rows * CELL
    img = Image.new("RGBA", (w, h), BOARD_BLUE)
    d = ImageDraw.Draw(img)

    # holes (white with black stroke)
    for r in range(rows):
        for c in range(cols):
            cx = c * CELL + CELL // 2
            cy = r * CELL + CELL // 2
            bbox = [cx - RADIUS, cy - RADIUS, cx + RADIUS, cy + RADIUS]
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
            bbox = [cx - RADIUS, cy - RADIUS, cx + RADIUS, cy + RADIUS]
            d.ellipse(bbox, fill=color, outline=EDGE_COLOR, width=STROKE)

    return img

# ----- Session bootstrap -----
if "game" not in st.session_state:
    st.session_state.game = ConnectFour()
if "ai" not in st.session_state:
    st.session_state.ai = ConnectFourAI(st.session_state.game)
    st.session_state.ai.set_player_number(2)  # AI = player 2 (Yellow)

g  = st.session_state.game
ai = st.session_state.ai
human = 1 if ai.AI == 2 else 2  # human is the other player

st.title("Connect Four")

c1, c2, _ = st.columns([1,1,2])
with c1:
    ai_starts = st.toggle("AI starts", value=False)
with c2:
    if st.button("Restart Game", use_container_width=True):
        st.session_state.game = ConnectFour()
        st.session_state.ai   = ConnectFourAI(st.session_state.game)
        if ai_starts:
            st.session_state.ai.set_player_number(1)   # AI = Red
            st.session_state.game.current_player = 1
            # AI opening move (no animation to keep UX snappy)
            ai_col = st.session_state.ai.get_best_move()
            g = st.session_state.game
            g.make_move(ai_col, 1)
        else:
            st.session_state.ai.set_player_number(2)   # AI = Yellow
            st.session_state.game.current_player = 1    # Human starts
        st.rerun()

# Status line
winner = g.check_winner()
if winner is None and not g.is_board_full():
    turn = "🔴 Human" if g.current_player == human else "🟡 AI"
    st.write(f"**Turn:** {turn}")

# ----- Render board as one image and make it clickable -----
img = draw_board_img(g.board)
# IMPORTANT: width=img.width keeps 1:1 pixels so columns map perfectly
evt = streamlit_image_coordinates(img, width=img.width, key="board-click")

# If the human clicked and it's the human's turn, compute the column and play
if evt and winner is None and g.current_player == human and not g.is_board_full():
    x = evt["x"]  # pixel X within the displayed image
    col = int(x // CELL)
    if 0 <= col < g.COLS and g.is_valid_move(col):
        if g.make_move(col, human):
            # let AI respond immediately if game not over
            if g.check_winner() is None and not g.is_board_full():
                ai_col = ai.get_best_move()
                g.make_move(ai_col, ai.AI)
            st.rerun()

# Footer
if winner is not None:
    st.success("You win! 🎉") if winner != ai.AI else st.error("AI wins! 🤖")
elif g.is_board_full():
    st.info("It’s a tie.")
st.caption("Click a column to drop a piece. Red = Human, Yellow = AI.")
