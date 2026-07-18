import streamlit as st

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="로또 스캐너", page_icon="🔍", layout="centered")

st.title("🔍 로또 스캐너")
st.markdown("매주 새로운 세트 번호를 갱신하고, 고른 번호가 어디에 숨어있는지 스캔해 보세요!")

# --- 1단계: 이번 주 세트 입력 칸 ---
st.header(" 1단계: 이번 주 24수 세트 입력")
st.markdown("유튜브나 예상수 이미지에서 본 A~J 세트 번호를 아래에 넣어주세요. (알파벳과 숫자만 띄어쓰기로 구분)")

# 기본값으로 예시 데이터(1233회)를 넣어두어 사용법을 알기 쉽게 함
default_sets = """A 1 2 4 6 7 9 10 11 15 20 21 23 25 31 32 33 34 36 37 38 39 40 44 45
B 1 3 4 5 6 7 10 11 13 14 16 17 19 20 21 25 27 30 31 32 35 42 44 45
C 1 3 4 6 7 8 10 12 14 18 20 21 22 24 25 26 28 29 31 32 41 43 44 45
D 2 3 4 8 9 11 12 14 15 18 19 25 26 29 31 32 33 34 35 36 40 41 43 45
E 2 3 5 6 7 8 10 12 13 15 18 19 24 25 27 28 30 31 32 33 37 38 39 44
F 2 3 5 8 13 15 17 19 21 23 27 31 32 34 35 36 37 39 40 41 42 43 44 45
G 2 3 6 7 10 14 15 16 17 22 25 26 29 31 32 33 35 37 38 39 41 42 43 44
H 3 4 7 10 11 13 15 17 20 21 22 24 26 27 29 30 32 34 35 37 38 39 43 45
I 3 5 7 9 10 11 12 14 15 18 20 22 23 24 25 30 33 34 35 38 42 43 44 45
J 5 6 7 9 10 11 13 14 19 22 23 25 26 27 29 30 31 32 34 36 40 41 43 44"""

sets_input = st.text_area("▼ 10개 세트(A~J) 번호 목록", value=default_sets, height=250)

# 입력된 텍스트를 파이썬 딕셔너리로 변환(파싱)하는 로직
parsed_sets = {}
if sets_input:
    lines = sets_input.strip().split('\n')
    for line in lines:
        parts = line.replace(",", " ").split()
        if not parts:
            continue
        set_name = parts[0].upper() # 줄의 첫 글자(A, B, C...)를 세트 이름으로 지정
        numbers = [int(p) for p in parts[1:] if p.isdigit()]
        
        if numbers:
            parsed_sets[set_name] = set(numbers)

# --- 2단계: 내 번호 스캔 칸 ---
st.markdown("---")
st.header("🔍 2단계: 내 번호 스캔하기")
user_input = st.text_input("고른 번호 6개를 띄어쓰기로 쳐주세요 (예: 7 10 15 25 38 44)", "")

if st.button(" 스캔 시작하기", use_container_width=True):
    if not parsed_sets:
        st.error("⚠️ 위쪽 칸에 세트 데이터가 비어있습니다. 이번 주 세트 번호를 넣어주세요.")
    elif not user_input:
        st.warning("⚠️ 스캔할 번호 6개를 입력해 주세요!")
    else:
        try:
            # 입력받은 번호 검증
            raw_numbers = user_input.replace(",", " ").split()
            my_numbers = set(map(int, raw_numbers))
            
            if len(my_numbers) != 6:
                st.error("⚠️ 서로 다른 번호 딱 6개를 입력하셔야 해요!")
            elif any(n < 1 or n > 45 for n in my_numbers):
                st.error("⚠️ 번호는 1부터 45 사이여야 해요!")
            else:
                st.success(f" 분석 타겟 번호: {sorted(list(my_numbers))}")
                
                # 교집합 매칭 로직
                results = []
                for set_name, set_numbers in parsed_sets.items():
                    intersection = my_numbers.intersection(set_numbers)
                    results.append({
                        "set": set_name,
                        "count": len(intersection),
                        "matched": sorted(list(intersection))
                    })
                
                # 많이 겹친 순서대로 자동 정렬
                results = sorted(results, key=lambda x: x["count"], reverse=True)
                
                # 스캔 결과 출력
                st.subheader("📊 스캔 결과")
                for res in results:
                    count = res["count"]
                    set_name = res["set"]
                    matched_str = ", ".join(f"{n:02d}" for n in res["matched"])
                    
                    if count == 6:
                        st.info(f"🏆 **[{set_name}세트] 6개 올적중!!!** 👉 [{matched_str}]")
                    elif count >= 4:
                        st.success(f" **[{set_name}세트] {count}개 일치** 👉 [{matched_str}]")
                    elif count >= 2:
                        st.warning(f" **[{set_name}세트] {count}개 일치** 👉 [{matched_str}]")
                    else:
                        st.write(f" [{set_name}세트] {count}개 일치 👉 [{'없음' if count == 0 else matched_str}]")
                        
        except ValueError:
            st.error("⚠️ 숫자가 아닌 값이 포함되어 있습니다. 다시 확인해 주세요!")

st.markdown("---")
st.caption("만든이: 전민규 (데이터 팩터 스코어링)")