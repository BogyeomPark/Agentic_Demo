import streamlit as st
import json
from utils import ask_teacher_agent

st.set_page_config(page_title="교사용 Agent", page_icon="🧑‍🏫")
st.markdown("<h1 style='text-align: center;'>🧑‍🏫 교사용 Agent</h1>", unsafe_allow_html=True)

# ✅ 학생 로그 불러오기
try:
    with open("student_log.json", "r", encoding="utf-8") as f:
        student_log = json.load(f)
except FileNotFoundError:
    st.error("학생 로그 파일이 없습니다.")
    st.stop()

# ✅ 전공/과목 정보 불러오기
try:
    with open("data.json", "r", encoding="utf-8") as f:
        curriculum_data = json.load(f)
except FileNotFoundError:
    st.warning("전공/과목 정보 파일(data.json)이 없습니다.")
    curriculum_data = {}

# ✅ 세션 상태 초기화
if "log" not in st.session_state:
    st.session_state.log = []
if "phase" not in st.session_state:
    st.session_state.phase = "input"
if "teacher_log" not in st.session_state:  # ✅ 추가됨
    st.session_state.teacher_log = []

# ✅ 채팅창 스타일링
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
with st.form(key="teacher_form", clear_on_submit=True):
    teacher_input = st.text_input("메시지를 입력하세요:", key="teacher_input_input")
    submitted = st.form_submit_button("보내기")
    if submitted and teacher_input:
        st.session_state.log.append({"role": "student", "msg": teacher_input})
        st.session_state.teacher_log.append({"role": "교사", "msg": teacher_input})  # ✅ 교사 입력 저장
        st.session_state.phase = "response"
        st.rerun()

# ✅ 응답 처리
if st.session_state.phase == "response":
    with st.spinner("응답 중입니다..."):
        chat_log = st.session_state.log.copy()
        reply = ask_teacher_agent(chat_log[-1]["msg"], student_log, curriculum_data)
    st.session_state.log.append({"role": "assistant", "msg": reply})
    st.session_state.teacher_log.append({"role": "AI 에이전트", "msg": reply})  # ✅ AI 응답 저장
    st.session_state.phase = "input"
    st.rerun()

# ✅ 상담 종료 버튼 추가 및 로그 저장
if st.button("✅ 상담 종료하기"):
    try:
        with open("teacher_log.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.teacher_log, f, ensure_ascii=False, indent=2)
        st.success("상담 로그가 저장되었습니다.")
    except Exception as e:
        st.error(f"저장 중 오류 발생: {e}")
