import streamlit as st
import json
import webbrowser
from utils import ask_student_agent

# 페이지 설정
st.set_page_config(page_title="학생용 Agent", page_icon="🎓")
st.markdown("<h1 style='text-align: center;'>🎓 학생용 Agent</h1>", unsafe_allow_html=True)

# 세션 상태 초기화
if "log" not in st.session_state:
    st.session_state.log = []
if "phase" not in st.session_state:
    st.session_state.phase = "input"

# ✅ 채팅창 스타일링 (생략 가능)
st.markdown("""
<style>
.chat-container {
    height: 400px;
    overflow-y: auto;
    padding: 1em;
    border: 1px solid #ccc;
    border-radius: 10px;
    margin-bottom: 1em;
    background-color: #ffffff;
    display: flex;
    flex-direction: column;
}
.chat-bubble {
    padding: 0.8em 1em;
    margin: 0.5em 0;
    border-radius: 12px;
    max-width: 80%;
    display: inline-block;
    font-size: 1rem;
    word-wrap: break-word;
}
.user {
    background-color: #dcf8c6;
    align-self: flex-end;
    text-align: right;
}
.assistant {
    background-color: #f1f0f0;
    align-self: flex-start;
    text-align: left;
}
</style>
""", unsafe_allow_html=True)

# ✅ 채팅 출력
chat_html = '<div class="chat-container" id="chatbox">'
for turn in st.session_state.log:
    cls = "user" if turn["role"] == "student" else "assistant"
    chat_html += f'<div class="chat-bubble {cls}">{turn["msg"]}</div>'
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# 자동 스크롤
st.markdown("""
<script>
const chatbox = document.getElementById("chatbox");
if (chatbox) {
    const observer = new MutationObserver(() => {
        chatbox.scrollTop = chatbox.scrollHeight;
    });
    observer.observe(chatbox, { childList: true });
}
</script>
""", unsafe_allow_html=True)

# ✅ 입력 폼
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("메시지를 입력하세요:", key="user_input_input")
    submitted = st.form_submit_button("보내기")
    if submitted and user_input:
        st.session_state.log.append({"role": "student", "msg": user_input})
        st.session_state.phase = "response"
        st.rerun()

# ✅ GPT 응답 처리
if st.session_state.phase == "response":
    with st.spinner("응답 중입니다..."):
        chat_log = st.session_state.log.copy()
        reply = ask_student_agent(chat_log)
    st.session_state.log.append({"role": "assistant", "msg": reply})
    st.session_state.phase = "input"
    st.rerun()

# ✅ 대화 종료 → 저장 + 교사 페이지 자동 이동
if st.button("✅ 교사용 Agent로 넘어가기"):
    # 1. 기존 상담 기록 복사
    st.session_state["student_log_for_teacher"] = st.session_state.log.copy()

    # 2. 현재 채팅창 초기화
    st.session_state.log = []
    st.session_state.phase = "input"

    # 3. 알림 출력 (원한다면)
    st.success("✅ 상담 기록이 저장되었고, 새 상담을 시작할 준비가 되었습니다.")
    st.rerun()  # 화면 재렌더링으로 반영

