# app.py
# -*- coding: utf-8 -*-

import random
import time
import streamlit as st


# ---------- 유틸 함수들 ----------

def generate_number(digits: int) -> int:
    """지정한 자릿수의 랜덤 정수 생성."""
    if digits == 1:
        return random.randint(1, 9)  # 0은 너무 쉬우니까 제외
    start = 10 ** (digits - 1)
    end = (10 ** digits) - 1
    return random.randint(start, end)


def generate_problems(first_digits: int, second_digits: int, count: int = 10):
    """퀴즈에 쓸 (a, b) 쌍을 미리 만들어 둔다."""
    problems = []
    for _ in range(count):
        a = generate_number(first_digits)
        b = generate_number(second_digits)
        problems.append({"a": a, "b": b})
    return problems


def init_state():
    """Streamlit session_state 초기값 세팅."""
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "finished" not in st.session_state:
        st.session_state.finished = False
    if "first_digits" not in st.session_state:
        st.session_state.first_digits = 1
    if "second_digits" not in st.session_state:
        st.session_state.second_digits = 1
    if "num_questions" not in st.session_state:
        st.session_state.num_questions = 10  # 조건: 한 번에 10문제
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "problems" not in st.session_state:
        st.session_state.problems = []
    if "correct_count" not in st.session_state:
        st.session_state.correct_count = 0
    if "times" not in st.session_state:
        st.session_state.times = []
    if "total_start_time" not in st.session_state:
        st.session_state.total_start_time = None
    if "total_time" not in st.session_state:
        st.session_state.total_time = None
    if "question_start_time" not in st.session_state:
        st.session_state.question_start_time = None
    if "feedback" not in st.session_state:
        st.session_state.feedback = ""


def start_quiz():
    """퀴즈 시작/재시작할 때 상태 초기화."""
    st.session_state.quiz_started = True
    st.session_state.finished = False
    st.session_state.current_index = 0
    st.session_state.correct_count = 0
    st.session_state.times = []
    st.session_state.feedback = ""
    st.session_state.num_questions = 10  # 조건 고정

    # 문제 미리 생성
    st.session_state.problems = generate_problems(
        st.session_state.first_digits,
        st.session_state.second_digits,
        st.session_state.num_questions,
    )

    # 타이머 시작
    now = time.time()
    st.session_state.total_start_time = now
    st.session_state.total_time = None
    st.session_state.question_start_time = now


def finish_quiz():
    """퀴즈 종료 처리."""
    st.session_state.quiz_started = False
    st.session_state.finished = True
    if st.session_state.total_start_time is not None:
        st.session_state.total_time = time.time() - st.session_state.total_start_time
    else:
        st.session_state.total_time = sum(st.session_state.times)


# ---------- Streamlit UI ----------

def main():
    init_state()

    st.title("🧮 곱셈 연습 퀴즈")
    st.write("곱셈 문제 10개를 푸는 웹 퀴즈입니다.")

    # ---- 사이드바: 설정 ----
    with st.sidebar:
        st.header("⚙️ 설정")

        st.session_state.first_digits = st.number_input(
            "첫 번째 숫자의 자릿수",
            min_value=1,
            max_value=6,
            value=st.session_state.first_digits,
            step=1,
        )
        st.session_state.second_digits = st.number_input(
            "두 번째 숫자의 자릿수",
            min_value=1,
            max_value=6,
            value=st.session_state.second_digits,
            step=1,
        )

        st.caption("예: 1 → 1자리수(1~9), 2 → 2자리수(10~99)")

        if not st.session_state.quiz_started:
            if st.button("🚀 퀴즈 시작하기 / 다시 시작하기"):
                start_quiz()

    # ---- 메인 영역 ----

    # 1) 아직 시작 전 & 결과도 없음 → 안내 화면
    if not st.session_state.quiz_started and not st.session_state.finished:
        st.subheader("시작 방법")
        st.markdown(
            """
1. 왼쪽 사이드바에서 **자릿수 설정**  
   (예: 2자리 × 2자리 등)  
2. **“퀴즈 시작하기” 버튼**을 누르면 문제 10개가 시작됩니다.  
3. 한 문제 맞출 때마다 자동으로 다음 문제로 넘어갑니다.  
4. 마지막 문제까지 풀면 **총 시간 + 통계**가 나옵니다.
            """
        )
        return

    # 2) 퀴즈 진행 중
    if st.session_state.quiz_started:
        idx = st.session_state.current_index
        num_q = st.session_state.num_questions

        # 진행 상황
        st.subheader(f"문제 {idx + 1} / {num_q}")
        st.progress(idx / num_q)

        # 현재까지 총 경과 시간 표시 (대략적인 느낌용)
        if st.session_state.total_start_time is not None:
            elapsed_now = time.time() - st.session_state.total_start_time
            st.caption(f"현재까지 총 경과 시간: {elapsed_now:.1f}초")

        # 직전 문제 피드백
        if st.session_state.feedback:
            st.info(st.session_state.feedback)

        # 현재 문제 가져오기
        problem = st.session_state.problems[idx]
        a, b = problem["a"], problem["b"]
        st.markdown(f"### ❓ {a} × {b} = ?")

        # 답 입력 폼
        with st.form(key=f"answer_form_{idx}"):
            answer = st.number_input(
                "정답을 입력하세요.",
                step=1,
                format="%d",
            )
            submitted = st.form_submit_button("제출")

        # 제출 처리
        if submitted:
            # 이 문제 풀이 시간
            if st.session_state.question_start_time is None:
                st.session_state.question_start_time = time.time()
            elapsed = time.time() - st.session_state.question_start_time
            st.session_state.times.append(elapsed)

            correct_value = a * b
            if int(answer) == correct_value:
                st.session_state.correct_count += 1
                st.session_state.feedback = f"✅ 정답! (풀이 시간: {elapsed:.2f}초)"
            else:
                st.session_state.feedback = (
                    f"❌ 오답! 정답은 {correct_value} 입니다. "
                    f"(풀이 시간: {elapsed:.2f}초)"
                )

            # 다음 문제로
            st.session_state.current_index += 1

            # 마지막 문제였는지 확인
            if st.session_state.current_index >= num_q:
                finish_quiz()
            else:
                st.session_state.question_start_time = time.time()

            st.rerun()

        return

    # 3) 퀴즈 끝난 후 결과 화면
    if st.session_state.finished:
        st.subheader("🎉 퀴즈 결과")

        num_q = st.session_state.num_questions
        correct = st.session_state.correct_count
        wrong = num_q - correct
        total_time = st.session_state.total_time or 0.0
        times = st.session_state.times

        avg_time = total_time / num_q if num_q > 0 else 0.0
        fastest = min(times) if times else 0.0
        slowest = max(times) if times else 0.0

        col1, col2 = st.columns(2)
        with col1:
            st.metric("맞힌 개수", f"{correct} / {num_q}")
            st.metric("틀린 개수", f"{wrong} 문제")
        with col2:
            st.metric("총 소요 시간", f"{total_time:.2f}초")
            st.metric("문제당 평균 시간", f"{avg_time:.2f}초")

        st.write("---")
        st.markdown(
            f"""
- 가장 빨리 푼 문제: **{fastest:.2f}초**  
- 가장 오래 걸린 문제: **{slowest:.2f}초**
"""
        )

        if times:
            st.write("### ⏱️ 문제별 풀이 시간(초)")
            # 간단한 시각화
            st.bar_chart(times)

        st.write("---")
        st.write("다시 풀고 싶으면 왼쪽 사이드바에서 자릿수 확인 후, 버튼을 눌러 재시작하세요.")


if __name__ == "__main__":
    main()
