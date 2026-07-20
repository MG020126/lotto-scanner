import streamlit as st
import re
import os

# --- 페이지 기본 설정 ---
st.set_page_config(page_title=" 로또 스캐너", page_icon="🔍", layout="centered")

st.title("🔍 로또 스캐너 (지능형 대량 스캔 + 저장)")
st.markdown("번호를 한 번 저장해 두면 다음번에 열어도 그대로 남아있어요!")

# --- 💡 파일 저장/보관을 위한 핵심 함수 ---
def load_saved_data(filename, default_text):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    return default_text

def save_data(filename, text):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

# --- 1단계: 이번 주 세트 입력 칸 ---
st.header("📝 1단계: 이번 주 24수 세트 입력")

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

# 저장된 세트 불러오기
saved_sets = load_saved_data("saved_sets.txt", default_sets)
sets_input = st.text_area("▼ 10개 세트(A~J) 번호 목록", value=saved_sets, height=180)

# 세트 저장 버튼
if st.button("💾 이번 주 세트 번호 기억하기"):
    save_data("saved_sets.txt", sets_input)
    st.success("✅ 세트 번호가 서버에 저장되었습니다! 다음번에도 이 번호로 시작합니다.")

parsed_sets = {}
if sets_input:
    for line in sets_input.strip().split('\n'):
        parts = line.replace(",", " ").split()
        if not parts:
            continue
        set_name = parts[0].upper()
        numbers = {int(p) for p in parts[1:] if p.isdigit()}
        if numbers:
            parsed_sets[set_name] = numbers

# --- 2단계: 내 번호 대량 스캔 칸 ---
st.markdown("---")
st.header("🔍 2단계: 내 번호 대량 스캔하기")

# 저장된 내 번호 데이터 불러오기
default_bulk = "010204060709111520212325\n7 10 15 25 38 44 / 030407101113"
saved_bulk = load_saved_data("saved_bulk.txt", default_bulk)

#  파일 업로드 기능 추가 (폰에 txt 파일이 있을 경우)
uploaded_file = st.file_uploader("📂 로또 번호 메모장 파일(.txt)이 있다면 여기에 올려주세요", type=["txt"])
if uploaded_file is not None:
    saved_bulk = uploaded_file.read().decode("utf-8")
    st.info("✅ 메모장 파일에서 번호를 성공적으로 읽어왔습니다!")

bulk_input = st.text_area("✏️ 번호 묶음 입력칸", value=saved_bulk, height=220)

# 내 번호 저장 버튼
if st.button("💾 이 번호 묶음 기억하기"):
    save_data("saved_bulk.txt", bulk_input)
    st.success("✅ 번호 묶음이 서버에 저장되었습니다! 이제 주중에는 안 지워져요.")

# --- 3단계: 스캔 가동 ---
st.markdown("---")
if st.button("🚀 조합 일괄 스캔 시작!", use_container_width=True):
    if not parsed_sets:
        st.error("⚠️ 위쪽 칸에 세트 데이터가 비어있습니다.")
    elif not bulk_input.strip():
        st.warning("⚠️ 스캔할 번호를 입력해 주세요!")
    else:
        # 기호 정제 로직
        clean_input = bulk_input.replace("/", " ").replace(".", " ").replace("-", " ").replace(",", " ")
        raw_tokens = clean_input.strip().split()
        
        all_numbers = []
        for token in raw_tokens:
            if len(token) >= 4 and token.isdigit():
                chunks = [int(token[i:i+2]) for i in range(0, len(token), 2) if i+1 < len(token)]
                all_numbers.extend(chunks)
            elif token.isdigit():
                all_numbers.append(int(token))
                
        valid_games = []
        for i in range(0, len(all_numbers), 6):
            chunk = all_numbers[i:i+6]
            if len(chunk) == 6:
                game_set = set(chunk)
                if len(game_set) == 6 and all(1 <= x <= 45 for x in game_set):
                    valid_games.append((len(valid_games) + 1, game_set))
        
        if not valid_games:
            st.error("⚠️ 유효한 로또 조합을 추출하지 못했습니다. 형식을 확인해 주세요!")
        else:
            st.success(f"✅ 총 {len(valid_games)}게임의 조합을 완벽히 식별했습니다. 대조 시작!")
            
            st.subheader("📊 스캔 결과 분석 리포트")
            
            results_to_show = []
            for game_num, my_numbers in valid_games:
                best_matches = []
                for set_name, set_numbers in parsed_sets.items():
                    intersection = my_numbers.intersection(set_numbers)
                    best_matches.append({
                        "set": set_name,
                        "count": len(intersection),
                        "matched": sorted(list(intersection))
                    })
                
                best_matches = sorted(best_matches, key=lambda x: x["count"], reverse=True)
                top_match = best_matches[0]
                results_to_show.append((game_num, my_numbers, top_match))
            
            for game_num, my_numbers, top_match in results_to_show:
                my_nums_str = ", ".join(f"{n:02d}" for n in sorted(list(my_numbers)))
                count = top_match["count"]
                set_name = top_match["set"]
                matched_str = ", ".join(f"{n:02d}" for n in top_match["matched"])
                
                if count == 6:
                    st.error(f"🏆 **[게임 {game_num}]** {my_nums_str} 👉 **{set_name}세트 6개 올적중!!!**")
                elif count == 5:
                    st.success(f" **[게임 {game_num}]** {my_nums_str} 👉 **{set_name}세트 5개 일치!** (일치 번호: {matched_str})")
                elif count == 4:
                    st.info(f" **[게임 {game_num}]** {my_nums_str} 👉 {set_name}세트 4개 일치 (일치 번호: {matched_str})")
                elif count == 3:
                    st.warning(f" **[게임 {game_num}]** {my_nums_str} 👉 {set_name}세트 3개 일치")
                else:
                    st.write(f" [게임 {game_num}] {my_nums_str} 👉 최고 {count}개 일치 ({set_name}세트)")

st.markdown("---")
st.caption("만든이: 전민규 (자동 데이터 저장 및 로드 기능 추가 완료)")
