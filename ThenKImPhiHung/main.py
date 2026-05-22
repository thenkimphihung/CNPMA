import streamlit as st
import random
import math

# ==============================================================================
# 1. CẤU HÌNH HỆ THỐNG
# ==============================================================================
st.set_page_config(
    page_title="WOODEN TIC-TAC-TOE",
    page_icon="🪵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. GIAO DIỆN GỖ CLASSIC (WOODEN THEME)
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Grantha+Sandhi:wght@700&family=Plus+Jakarta+Sans:wght@700;800&display=swap');

.stApp {
    background-color: #2b1810;
    background-image:
        linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)),
        url('https://i.pinimg.com/736x/91/4b/22/914b223b4660c092ae98a02e64b50dfe.jpg');
    background-size: cover;
    background-position: center;
    color: #f5e6d3;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.wood-panel {
    background: #4a2c1b;
    padding: 25px;
    border-radius: 15px;
    border: 10px solid #361f12;
    box-shadow:
        inset 0 0 20px rgba(0,0,0,0.8),
        0 15px 30px rgba(0,0,0,0.7);
    margin: 0 auto;
}

div.wood-board-zone div.stButton > button {
    width: 100% !important;
    background: #3d2314 !important;
    border: 2px solid #26150b !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
    box-shadow:
        inset 3px 3px 10px rgba(0,0,0,0.8),
        1px 1px 2px rgba(255,255,255,0.1) !important;
}

div.wood-board-zone div.stButton > button:hover {
    background: #472917 !important;
    border-color: #5c351c !important;
}

div.wood-board-zone div.stButton > button p {
    font-family: 'Grantha Sandhi', serif !important;
    font-weight: 900 !important;
    text-shadow:
        2px 2px 4px rgba(0,0,0,0.9),
        -1px -1px 0px rgba(0,0,0,0.5) !important;
}

div[data-testid="stSidebar"] {
    background-color: rgba(43, 24, 16, 0.95) !important;
    border-right: 3px solid #1f110b;
}

div[data-testid="stSidebar"] .stMarkdown,
div[data-testid="stSidebar"] label {
    color: #f5e6d3 !important;
}

.wood-sign {
    background: #5c351c;
    border: 2px solid #3d2314;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
    font-weight: bold;
    color: #f5e6d3;
    box-shadow: 0 4px 8px rgba(0,0,0,0.4);
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. SESSION STATE
# ==============================================================================
if 'grid_size' not in st.session_state:
    st.session_state.grid_size = 3

if 'board' not in st.session_state:
    st.session_state.board = [' ' for _ in range(9)]

if 'winner' not in st.session_state:
    st.session_state.winner = None

if 'turn' not in st.session_state:
    st.session_state.turn = 'X'

if 'scores' not in st.session_state:
    st.session_state.scores = {
        'Player': 0,
        'AI': 0,
        'Ties': 0
    }

# ==============================================================================
# 4. RESET GAME
# ==============================================================================
def reset_board(size):
    st.session_state.grid_size = size
    st.session_state.board = [' ' for _ in range(size * size)]
    st.session_state.winner = None
    st.session_state.turn = 'X'

# ==============================================================================
# 5. KẾT THÚC GAME
# ==============================================================================
def finish_game(winner):
    st.session_state.winner = winner

    if winner == 'X':
        st.session_state.scores['Player'] += 1

    elif winner == 'O':
        st.session_state.scores['AI'] += 1

    elif winner == 'Tie':
        st.session_state.scores['Ties'] += 1

# ==============================================================================
# 6. KIỂM TRA THẮNG
# ==============================================================================
def check_winner(board, size):

    win_condition = 3 if size == 3 else (4 if size == 5 else 5)

    matrix = [
        board[i * size:(i + 1) * size]
        for i in range(size)
    ]

    for r in range(size):
        for c in range(size):

            # Ngang
            if c <= size - win_condition:
                if (
                    matrix[r][c] != ' '
                    and all(
                        matrix[r][c + i] == matrix[r][c]
                        for i in range(win_condition)
                    )
                ):
                    return matrix[r][c]

            # Dọc
            if r <= size - win_condition:
                if (
                    matrix[r][c] != ' '
                    and all(
                        matrix[r + i][c] == matrix[r][c]
                        for i in range(win_condition)
                    )
                ):
                    return matrix[r][c]

            # Chéo xuôi
            if r <= size - win_condition and c <= size - win_condition:
                if (
                    matrix[r][c] != ' '
                    and all(
                        matrix[r + i][c + i] == matrix[r][c]
                        for i in range(win_condition)
                    )
                ):
                    return matrix[r][c]

            # Chéo ngược
            if r >= win_condition - 1 and c <= size - win_condition:
                if (
                    matrix[r][c] != ' '
                    and all(
                        matrix[r - i][c + i] == matrix[r][c]
                        for i in range(win_condition)
                    )
                ):
                    return matrix[r][c]

    if ' ' not in board:
        return 'Tie'

    return None

# ==============================================================================
# 7. MINIMAX CHO 3x3
# ==============================================================================
def minimax(board, depth, is_max):

    status = check_winner(board, 3)

    if status == 'X':
        return 10 - depth

    if status == 'O':
        return depth - 10

    if status == 'Tie':
        return 0

    if is_max:

        best = -math.inf

        for i in range(9):
            if board[i] == ' ':
                board[i] = 'X'
                best = max(best, minimax(board, depth + 1, False))
                board[i] = ' '

        return best

    else:

        best = math.inf

        for i in range(9):
            if board[i] == ' ':
                board[i] = 'O'
                best = min(best, minimax(board, depth + 1, True))
                board[i] = ' '

        return best

# ==============================================================================
# 8. AI MOVE
# ==============================================================================
def get_ai_move(board, size):

    # 3x3 => Minimax
    if size == 3:

        best_val = math.inf
        best_move = None

        for i in range(9):

            if board[i] == ' ':

                board[i] = 'O'

                move_val = minimax(board, 0, True)

                board[i] = ' '

                if move_val < best_val:
                    best_val = move_val
                    best_move = i

        return best_move

    # 5x5 và 10x10
    empty_cells = [i for i, c in enumerate(board) if c == ' ']

    # AI thắng luôn
    for move in empty_cells:

        board[move] = 'O'

        if check_winner(board, size) == 'O':
            board[move] = ' '
            return move

        board[move] = ' '

    # Chặn người chơi
    for move in empty_cells:

        board[move] = 'X'

        if check_winner(board, size) == 'X':
            board[move] = ' '
            return move

        board[move] = ' '

    # Random
    return random.choice(empty_cells) if empty_cells else None

# ==============================================================================
# 9. CLICK Ô CỜ
# ==============================================================================
def cell_clicked(idx, mode):

    # Nếu ô đã đánh hoặc game kết thúc
    if (
        st.session_state.board[idx] != ' '
        or st.session_state.winner is not None
    ):
        return

    # ==========================================================
    # CHẾ ĐỘ ĐẤU VỚI MÁY
    # ==========================================================
    if mode == "🤖 Đấu với Máy":

        # Người chơi luôn là X
        st.session_state.board[idx] = 'X'

        winner = check_winner(
            st.session_state.board,
            st.session_state.grid_size
        )

        if winner:
            finish_game(winner)
            return

        # AI đánh O
        ai_move = get_ai_move(
            st.session_state.board,
            st.session_state.grid_size
        )

        if ai_move is not None:

            st.session_state.board[ai_move] = 'O'

            winner = check_winner(
                st.session_state.board,
                st.session_state.grid_size
            )

            if winner:
                finish_game(winner)
                return

    # ==========================================================
    # CHẾ ĐỘ 2 NGƯỜI
    # ==========================================================
    else:

        st.session_state.board[idx] = st.session_state.turn

        winner = check_winner(
            st.session_state.board,
            st.session_state.grid_size
        )

        if winner:
            finish_game(winner)
            return

        # Đổi lượt
        st.session_state.turn = (
            'O'
            if st.session_state.turn == 'X'
            else 'X'
        )

# ==============================================================================
# 10. SIDEBAR
# ==============================================================================
with st.sidebar:

    st.markdown("""
    <h2 style='text-align:center;
               font-family:"Grantha Sandhi";
               color:#eec590;'>
        THÀNH TRÌ CÀI ĐẶT
    </h2>
    """, unsafe_allow_html=True)

    current_size = st.radio(
        "📐 KÍCH THƯỚC BÀN CỜ:",
        [3, 5, 10],
        format_func=lambda x: f"Bàn cờ {x} x {x}",
        index=[3, 5, 10].index(st.session_state.grid_size)
    )

    if current_size != st.session_state.grid_size:
        reset_board(current_size)
        st.rerun()

    game_mode = st.selectbox(
        "👥 CHẾ ĐỘ CHƠI",
        ["🤖 Đấu với Máy", "👥 Chơi 2 người"]
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("🔄 Thiết lập lại trận mới", use_container_width=True):
        reset_board(st.session_state.grid_size)
        st.rerun()

# ==============================================================================
# 11. TITLE
# ==============================================================================
st.markdown("""
<h1 style='text-align:center;
           font-family:"Grantha Sandhi";
           color:#eec590;
           margin-bottom:0;'>
WOODEN TIC-TAC-TOE
</h1>
""", unsafe_allow_html=True)

if st.session_state.grid_size == 3:
    st.markdown("""
    <p style='text-align:center;
              color:#b09475;
              font-size:14px;'>
        Luật: Đạt liên tiếp 3 ô ngang/dọc/chéo để thắng
    </p>
    """, unsafe_allow_html=True)

elif st.session_state.grid_size == 5:
    st.markdown("""
    <p style='text-align:center;
              color:#b09475;
              font-size:14px;'>
        Luật: Đạt liên tiếp 4 ô ngang/dọc/chéo để thắng
    </p>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <p style='text-align:center;
              color:#b09475;
              font-size:14px;'>
        Luật: Đạt liên tiếp 5 ô ngang/dọc/chéo để thắng
    </p>
    """, unsafe_allow_html=True)

# ==============================================================================
# 12. TRẠNG THÁI GAME
# ==============================================================================
if st.session_state.winner is None:

    if game_mode == "🤖 Đấu với Máy":
        txt = "Lượt đi: Người chơi X"

    else:
        txt = f"Lượt đi: {st.session_state.turn}"

    st.markdown(
        f"<div class='wood-sign'>🪵 {txt}</div>",
        unsafe_allow_html=True
    )

else:

    if st.session_state.winner == 'Tie':

        st.markdown("""
        <div class='wood-sign'
             style='background:#b0814a;'>
             🤝 TRẬN ĐẤU HÒA CỜ!
        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown(
            f"""
            <div class='wood-sign'
                 style='background:#8a4d29;
                        color:#fceade;'>
                 🏆 QUÂN {st.session_state.winner} CHIẾN THẮNG!
            </div>
            """,
            unsafe_allow_html=True
        )

# ==============================================================================
# 13. KÍCH THƯỚC Ô
# ==============================================================================
cell_height = (
    "110px"
    if st.session_state.grid_size == 3
    else ("70px" if st.session_state.grid_size == 5 else "40px")
)

font_size = (
    "45px"
    if st.session_state.grid_size == 3
    else ("30px" if st.session_state.grid_size == 5 else "18px")
)

# ==============================================================================
# 14. BOARD
# ==============================================================================
st.markdown(
    "<div class='wood-board-zone'><div class='wood-panel'>",
    unsafe_allow_html=True
)

st.markdown(f"""
<style>
div.wood-board-zone div.stButton > button {{
    height: {cell_height} !important;
}}

div.wood-board-zone div.stButton > button p {{
    font-size: {font_size} !important;
}}
</style>
""", unsafe_allow_html=True)

size = st.session_state.grid_size

for r in range(size):

    cols = st.columns(size)

    for c in range(size):

        idx = r * size + c

        val = st.session_state.board[idx]

        display_text = val if val != ' ' else " "

        with cols[c]:

            st.button(
                display_text,
                key=f"w_cell_{idx}",
                on_click=cell_clicked,
                args=(idx, game_mode),
                use_container_width=True
            )

st.markdown("</div></div>", unsafe_allow_html=True)

# ==============================================================================
# 15. SCORE
# ==============================================================================
st.markdown("<br>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

c1.metric("THẮNG (X)", st.session_state.scores['Player'])
c2.metric("HÒA", st.session_state.scores['Ties'])
c3.metric("THUA (O)", st.session_state.scores['AI'])