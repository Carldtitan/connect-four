# app.py — Streamlit web UI for Connect Four (prettier UI)
import streamlit as st
from game import ConnectFour
from ai import ConnectFourAI

st.set_page_config(page_title="Connect Four", page_icon="🎮", layout="centered")

# ---------- simple CSS to make the board look good ----------
st.markdown("""
<style>
/* Bigger, round buttons for cells */
div.stButton > button[kind="secondary"] {
  font-size: 28px !important;
  line-height: 1 !important;
  width: 64px !important;
  height: 64px !important;
  border-radius: 50% !important;
  border: 2px solid rgba(255,255,255,0.2) !important;
  background: #1f2937 !important; /* slate-800 */
  box-shadow: 0 2px 8px rgba(0,0,0,0.25) !important;
}
/* Drop buttons */
.drop button {
  font-size: 18px !important;
  width: 72px !important;
  height: 42px !important;
  border-radius: 10px !important;
}
/* Header tweaks */
h1 { letter-spacing: .5px; }
.legend { color: #9CA3AF; font-size: 0.9rem; }
.turn-badge {
  display:inline-block; padding:6px 10px; border-radius:12px; font-weight:600;
  background:#374151; color:white; margin-left:.5rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- session/bootstrap ----------
if "game" not in st.session_state:
  st.session_state.game = ConnectFour()
if "ai" not in st.session_state:
  st.session_state.ai = ConnectFourAI(st.session_state.game)
  st.session_state.ai.set_player_number(2)  # AI plays Yellow

g  = st.session_state.game
ai = st.session_state.ai

st.title("Connect Four")

# Controls row
c1, c2, c3 = st.columns([1,1,2])
with c1:
  ai_starts = st.toggle("AI starts", value=False)
with c2:
  if st.button("New game"):
    st.session_state.game = ConnectFour()
    st.session_state.ai   = ConnectFourAI(st.session_state.game)
    if ai_starts:
      st.session_state.ai.set_player_number(1)
      first = st.session_state.ai.get_best_move()
      st.session_state.game.make_move(first, 1)
    else:
      st.session_state.ai.set_player_number(2)
    st.rerun()

# Turn badge
winner = g.check_winner()
if winner is None and not g.is_board_full():
  human = 1 if ai.AI == 2 else 2
  turn = "🔴 Human" if g.current_player == human else "🟡 AI"
  st.markdown(f"**Turn:** <span class='turn-badge'>{turn}</span>", unsafe_allow_html=True)

# ---------- board ----------
def token(v: int) -> str:
  # 0 empty, 1 red, 2 yellow
  return "⚪" if v == 0 else ("🔴" if v == 1 else "🟡")

for r in range(g.ROWS):
  cols = st.columns(g.COLS, gap="small")
  for c in range(g.COLS):
    with cols[c]:
      # secondary style = gray background from CSS; disabled so it's just visual
      st.button(token(g.board[r][c]), key=f"cell-{r}-{c}", disabled=True)

st.divider()
st.write("Drop a piece:")
drop_cols = st.columns(g.COLS, gap="small")

# ---------- gameplay ----------
if winner is not None:
  if ai.AI != winner:
    st.success("You win! 🎉"); st.balloons()
  else:
    st.error("AI wins! 🤖")
elif g.is_board_full():
  st.info("It’s a tie.")
else:
  for c in range(g.COLS):
    with drop_cols[c]:
      disabled = not g.is_valid_move(c)
      # Add a CSS class hook for nicer size
      btn = st.container()
      with btn:
        st.markdown('<div class="drop">', unsafe_allow_html=True)
        if st.button(f"↓ {c+1}", key=f"drop-{c}", disabled=disabled):
          human = 1 if ai.AI == 2 else 2
          if g.make_move(c, human):
            if g.check_winner() is None and not g.is_board_full():
              ai_col = ai.get_best_move()
              g.make_move(ai_col, ai.AI)
          st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<p class='legend'>Red = Human, Yellow = AI. Click the arrows to drop pieces.</p>",
            unsafe_allow_html=True)
