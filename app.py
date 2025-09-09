# app.py — Streamlit web UI for your Connect Four
import streamlit as st
from game import ConnectFour
from ai import ConnectFourAI

st.set_page_config(page_title="Connect Four", page_icon="🎮", layout="centered")
st.title("Connect Four")

# Bootstrap session
if "game" not in st.session_state:
    st.session_state.game = ConnectFour()
if "ai" not in st.session_state:
    st.session_state.ai = ConnectFourAI(st.session_state.game)
    st.session_state.ai.set_player_number(2)  # AI is player 2 (Yellow)

g = st.session_state.game
ai = st.session_state.ai

# Controls
left, right = st.columns(2)
with left:
    ai_starts = st.toggle("AI starts", value=False)
with right:
    if st.button("New game"):
        st.session_state.game = ConnectFour()
        st.session_state.ai = ConnectFourAI(st.session_state.game)
        if ai_starts:
            st.session_state.ai.set_player_number(1)  # AI plays Red
            first_col = st.session_state.ai.get_best_move()
            st.session_state.game.make_move(first_col, 1)
        else:
            st.session_state.ai.set_player_number(2)  # AI plays Yellow
        st.rerun()

def emoji(v):
    return "⚪" if v == 0 else ("🟥" if v == 1 else "🟨")

# Draw board (row 0 is top)
for r in range(g.ROWS):
    cols = st.columns(g.COLS, gap="small")
    for c in range(g.COLS):
        with cols[c]:
            st.button(emoji(g.board[r][c]), key=f"cell-{r}-{c}", disabled=True)

st.divider()
st.write("Drop a piece:")
drop_cols = st.columns(g.COLS, gap="small")

winner = g.check_winner()
if winner is not None:
    st.success("You win! 🎉" if (ai.AI != winner) else "AI wins! 🤖")
elif g.is_board_full():
    st.info("It's a tie.")

# Only allow moves if game is not over
if winner is None and not g.is_board_full():
    for c in range(g.COLS):
        with drop_cols[c]:
            if st.button(f"↓ {c+1}", key=f"drop-{c}", disabled=not g.is_valid_move(c)):
                human = 1 if ai.AI == 2 else 2
                if g.make_move(c, human):
                    if g.check_winner() is None and not g.is_board_full():
                        ai_col = ai.get_best_move()
                        g.make_move(ai_col, ai.AI)
                st.rerun()

st.caption("Red = Human, Yellow = AI. Click the arrows to drop pieces.")
