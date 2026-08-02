import streamlit as st
import re
import os

# --- 1. 페이지 기본 설정 ---
st.set_page_config(page_title="로또 종합 스캐너", page_icon="🔍", layout="centered")

st.title("🔍 로또 종합 스캐너")
st.markdown("상단의 **탭(Tab)**을 눌러 원하는 기능을 선택하세요. (기본 세트/패턴은 자동 저장됩니다!)")

# --- 공통: 파일 저장/보관 함수 ---
def load_saved_data(filename, default_text):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    return default_text

def save_data(filename, text):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

# 자동 저장 콜백 함수
def save_tab1_sets_callback():
    save_data("saved_tab1_sets.txt", st.session_state.tab1_sets_key)

def save_tab2_box1_callback():
    save_data("saved_tab2_box1.txt", st.session_state.tab2_box1_key)

# ---  지능형 스마트 토큰 카빙 (어떤 형태든 숫자 쏙쏙 추출) ---
def extract_lotto_numbers(text):
    clean_text = text.replace("/", " ").replace(".", " ").replace("-", " ").replace(",", " ")
    tokens = clean_text.strip().split()
    all_nums = []
    for token in tokens:
        # 4글자 이상 연속된 숫자는 2자리씩 자동 슬라이싱 (예: '010203' -> 1, 2, 3)
        if len(token) >= 4 and token.isdigit():
            chunks = [int(token[i:i+2]) for i in range(0, len(token), 2) if i+1 < len(token)]
            all_nums.extend(chunks)
        elif token.isdigit():
            all_nums.append(int(token))
    # 1~45 사이 로또 번호만 남기고 중복 제거 후 정렬
    return sorted(list({n for n in all_nums if 1 <= n <= 45}))

# --- 상단 탭(Tab) 나누기 ---
tab1, tab2 = st.tabs(["🎰 1. 당첨 조합 대량 스캐너 (기존)", "📊 2. 패턴 겹침 분석기 (신규)"])

# ==============================================================================
# [탭 1] 기존 기능: 이번 주 24수 세트 vs 내 로또 조합(6수) 당첨 채점
# ==============================================================================
with tab1:
    st.header("📝 1단계: 이번 주 24수 세트 입력 (자동 기억)")
    default_tab1_sets = """A 1 2 4 6 7 9 10 11 15 20 21 23 25 31 32 33 34 36 37 38 39 40 44 45
B 1 3 4 5 6 7 10 11 13 14 16 17 19 20 21 25 27 30 31 32 35 42 44 45
C 1 3 4 6 7 8 10 12 14 18 20 21 22 24 25 26 28 29 31 32 41 43 44 45
D 2 3 4 8 9 11 12 14 15 18 19 25 26 29 31 32 33 34 35 36 40 41 43 45
E 2 3 5 6 7 8 10 12 13 15 18 19 24 25 27 28 30 31 32 33 37 38 39 44
F 2 3 5 8 13 15 17 19 21 23 27 31 32 34 35 36 37 39 40 41 42 43 44 45
G 2 3 6 7 10 14 15 16 17 22 25 26 29 31 32 33 35 37 38 39 41 42 43 44
H 3 4 7 10 11 13 15 17 20 21 22 24 26 27 29 30 32 34 35 37 38 39 43 45
I 3 5 7 9 10 11 12 14 15 18 20 22 23 24 25 30 33 34 35 38 42 43 44 45
J 5 6 7 9 10 11 13 14 19 22 23 25 26 27 29 30 31 32 34 36 40 41 43 44"""
    
    saved_tab1_sets = load_saved_data("saved_tab1_sets.txt", default_tab1_sets)
    sets_input = st.text_area("▼ 10개 세트(A~J) 목록 (수정 후 칸 밖을 누르면 자동 저장)", value=saved_tab1_sets, height=180, key="tab1_sets_key", on_change=save_tab1_sets_callback)
    
    parsed_sets = {}
    if sets_input:
        for line in sets_input.strip().split('\n'):
            parts = line.replace(",", " ").split()
            if not parts: continue
            set_name = parts[0].upper()
            nums = {int(p) for p in parts[1:] if p.isdigit()}
            if nums: parsed_sets[set_name] = nums

    st.markdown("---")
    st.header("🔍 2단계: 내 로또 조합(6수) 대량 스캔하기")
    st.caption("뽑으신 6수짜리 조합들을 붙여넣으세요. (띄어쓰기/쉼표/슬래시/연속숫자 010203 전부 자동 인식)")
    
    uploaded_file_tab1 = st.file_uploader("📂 로또 조합 메모장 파일(.txt)이 있다면 올려주세요", type=["txt"], key="upload_tab1")
    default_bulk_text = "010204060709\n7 10 15 25 38 44 / 030407101113"
    if uploaded_file_tab1 is not None:
        default_bulk_text = uploaded_file_tab1.read().decode("utf-8")
        st.info("✅ 메모장 파일에서 조합을 성공적으로 읽어왔습니다!")
        
    bulk_input = st.text_area("▼ 6수 조합 묶음 입력칸", value=default_bulk_text, height=160, key="bulk_tab1")

    if st.button("🚀 6수 조합 당첨 스캔 시작!", use_container_width=True, key="btn_tab1"):
        if not parsed_sets:
            st.error("⚠️ 1단계에 세트 데이터가 비어있습니다.")
        elif not bulk_input.strip():
            st.warning("⚠️ 스캔할 로또 조합을 입력해 주세요!")
        else:
            clean_input = bulk_input.replace("/", " ").replace(".", " ").replace("-", " ").replace(",", " ")
            raw_tokens = clean_input.strip().split()
            all_numbers = []
            for token in raw_tokens:
                if len(token) >= 4 and token.isdigit():
                    all_numbers.extend([int(token[i:i+2]) for i in range(0, len(token), 2) if i+1 < len(token)])
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
                st.error("⚠️ 유효한 로또 조합(1~45 사이 6개 숫자)을 찾지 못했습니다.")
            else:
                st.success(f"✅ 총 {len(valid_games)}게임의 조합을 식별했습니다. 채점 결과:")
                for game_num, my_numbers in valid_games:
                    best_matches = sorted([{"set": k, "count": len(my_numbers.intersection(v)), "matched": sorted(list(my_numbers.intersection(v)))} for k, v in parsed_sets.items()], key=lambda x: x["count"], reverse=True)
                    top = best_matches[0]
                    my_nums_str = ", ".join(f"{n:02d}" for n in sorted(list(my_numbers)))
                    matched_str = ", ".join(f"{n:02d}" for n in top["matched"])
                    
                    if top["count"] == 6: st.error(f"🏆 [게임 {game_num}] {my_nums_str} 👉 {top['set']}세트 6개 올적중!!!")
                    elif top["count"] == 5: st.success(f"🔥 [게임 {game_num}] {my_nums_str} 👉 {top['set']}세트 5개 일치! ({matched_str})")
                    elif top["count"] == 4: st.info(f"✨ [게임 {game_num}] {my_nums_str} 👉 {top['set']}세트 4개 일치 ({matched_str})")
                    elif top["count"] == 3: st.warning(f"🔹 [게임 {game_num}] {my_nums_str} 👉 {top['set']}세트 3개 일치")
                    else: st.write(f"⚪ [게임 {game_num}] {my_nums_str} 👉 최고 {top['count']}개 일치 ({top['set']}세트)")

# ==============================================================================
# [탭 2] 신규 기능: 1번 박스(30패턴 저장) vs 2번 박스(20~30수 입력) 겹침 대조
# ==============================================================================
with tab2:
    st.header("📝 [1번 박스] 30개 패턴 저장 (자동 기억)")
    st.caption("각 줄에 패턴 이름과 번호를 써주세요. (한 번 써두면 평생 자동 기억합니다)")

    default_patterns = """P01 1 2 4 6 7 9 10 11 15 20 21 23 25 31 32 33 34 36 37 38 39 40 44 45
P02 1 3 4 5 6 7 10 11 13 14 16 17 19 20 21 25 27 30 31 32 35 42 44 45
P03 1 3 4 6 7 8 10 12 14 18 20 21 22 24 25 26 28 29 31 32 41 43 44 45
P04 2 3 4 8 9 11 12 14 15 18 19 25 26 29 31 32 33 34 35 36 40 41 43 45
P05 2 3 5 6 7 8 10 12 13 15 18 19 24 25 27 28 30 31 32 33 37 38 39 44
P06 2 3 5 8 13 15 17 19 21 23 27 31 32 34 35 36 37 39 40 41 42 43 44 45
P07 2 3 6 7 10 14 15 16 17 22 25 26 29 31 32 33 35 37 38 39 41 42 43 44
P08 3 4 7 10 11 13 15 17 20 21 22 24 26 27 29 30 32 34 35 37 38 39 43 45
P09 3 5 7 9 10 11 12 14 15 18 20 22 23 24 25 30 33 34 35 38 42 43 44 45
P10 5 6 7 9 10 11 13 14 19 22 23 25 26 27 29 30 31 32 34 36 40 41 43 44"""

    saved_box1 = load_saved_data("saved_tab2_box1.txt", default_patterns)
    box1_input = st.text_area("▼ 30개 패턴 목록 (수정 후 칸 밖을 누르면 자동 저장)", value=saved_box1, height=200, key="tab2_box1_key", on_change=save_tab2_box1_callback)

    parsed_patterns = []
    if box1_input:
        for idx, line in enumerate(box1_input.strip().split('\n')):
            if not line.strip(): continue
            parts = line.strip().split()
            nums = extract_lotto_numbers(line)
            if nums:
                label = parts[0] if (not parts[0].isdigit() or len(parts[0]) <= 3) else f"패턴{idx+1}"
                parsed_patterns.append({"label": label, "numbers": set(nums)})

    st.caption(f"✅ 1번 박스에서 총 **{len(parsed_patterns)}개**의 패턴을 읽어왔습니다.")

    st.markdown("---")
    st.header("🔍 [2번 박스] 대조할 20~30수 번호 입력")
    st.caption("이번 주 분석할 20~30개 번호를 넣으세요. (띄어쓰기/쉼표/연속숫자 010203... 자유롭게 입력)")

    uploaded_file_tab2 = st.file_uploader("📂 번호 메모장 파일(.txt)이 있다면 올려주세요", type=["txt"], key="upload_tab2")
    default_box2_text = "01 03 05 07 10 11 13 15 17 20 22 25 27 29 30 32 34 35 37 38 40 42 44 45"
    if uploaded_file_tab2 is not None:
        default_box2_text = uploaded_file_tab2.read().decode("utf-8")
        st.info("✅ 메모장 파일에서 번호를 성공적으로 불러왔습니다!")

    box2_input = st.text_area("▼ 대조할 20~30수 목록 입력칸", value=default_box2_text, height=100, key="box2_tab2")

    st.markdown("---")
    if st.button("🚀 30패턴 vs 20~30수 겹침 분석 시작!", use_container_width=True, key="btn_tab2"):
        if not parsed_patterns:
            st.error("⚠️ 1번 박스에 저장된 패턴이 없습니다.")
        elif not box2_input.strip():
            st.warning("⚠️ 2번 박스에 대조할 번호를 입력해 주세요!")
        else:
            box2_numbers = set(extract_lotto_numbers(box2_input))
            if not box2_numbers:
                st.error("⚠️ 2번 박스에서 유효한 로또 번호(1~45)를 찾지 못했습니다.")
            else:
                box2_str = ", ".join(f"{n:02d}" for n in sorted(list(box2_numbers)))
                st.success(f"✅ **2번 박스 인식 완료 (총 {len(box2_numbers)}수):** {box2_str}")
                
                analysis_results = []
                for item in parsed_patterns:
                    label = item["label"]
                    pattern_nums = item["numbers"]
                    intersection = pattern_nums.intersection(box2_numbers)
                    analysis_results.append({
                        "label": label,
                        "total_pattern_count": len(pattern_nums),
                        "overlap_count": len(intersection),
                        "overlap_nums": sorted(list(intersection))
                    })
                
                analysis_results = sorted(analysis_results, key=lambda x: x["overlap_count"], reverse=True)
                
                st.subheader("🏆 [결론] 패턴별 겹친 숫자 순위 리포트")
                st.write("2번 박스 번호와 **가장 많이 겹친 패턴부터 순서대로** 보여드립니다.")
                
                for rank, res in enumerate(analysis_results, 1):
                    label = res["label"]
                    overlap_count = res["overlap_count"]
                    total_p_count = res["total_pattern_count"]
                    overlap_str = ", ".join(f"{n:02d}" for n in res["overlap_nums"]) if res["overlap_nums"] else "겹친 수 없음"
                    
                    if overlap_count >= 15:
                        st.error(f"**{rank}위. [{label}]** 👉 **총 {overlap_count}수 겹침!** (패턴 총 {total_p_count}수 중)\n\n"
                                 f"🔹 **겹친 번호:** {overlap_str}")
                    elif overlap_count >= 10:
                        st.success(f"**{rank}위. [{label}]** 👉 **총 {overlap_count}수 겹침!** (패턴 총 {total_p_count}수 중)\n\n"
                                   f"🔹 **겹친 번호:** {overlap_str}")
                    elif overlap_count >= 5:
                        st.info(f"**{rank}위. [{label}]** 👉 **총 {overlap_count}수 겹침!** (패턴 총 {total_p_count}수 중)\n\n"
                                f"🔹 **겹친 번호:** {overlap_str}")
                    else:
                        st.write(f"**{rank}위. [{label}]** 👉 **총 {overlap_count}수 겹침** (패턴 총 {total_p_count}수 중) | 겹친 수: {overlap_str}")

st.markdown("---")
st.caption("만든이: 전민규 (기존 6수 당첨 스캐너 + 신규 30패턴 겹침 분석기 상단 탭 통합 완성)")
