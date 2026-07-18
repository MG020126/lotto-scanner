import streamlit as st
import re

# --- 1. 페이지 기본 설정 ---
st.set_page_config(page_title="로또 스캐너", page_icon="🔍", layout="centered")

st.title("🔍 로또 스캐너 (지능형 대량 스캔)")
st.markdown("매주 새로운 세트 번호를 갱신하고, 번호들을 형식 제한 없이 한 번에 쫙 스캔해 보세요!")

# --- 2. 1단계: 이번 주 세트 입력 칸 ---
st.header(" 1단계: 이번 주 24수 세트 입력")
st.markdown("유튜브나 예상수 이미지에서 본 A~J 세트 번호를 아래에 넣어주세요. (형식: A 1 2 3...)")

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

sets_input = st.text_area("▼ 10개 세트(A~J) 번호 목록", value=default_sets, height=200)

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

# --- 3. 2단계: 내 번호 대량 스캔 칸 ---
st.markdown("---")
st.header(" 2단계: 내 번호 대량 스캔하기")
st.markdown("""
아빠가 뽑으신 번호들을 자유롭게 붙여넣어 주세요! 
* **띄어쓰기, 쉼표(,), 슬래시(/), 마침표(.), 대시(-)** 모두 알아서 구분합니다.
* **`010203040506...`** 처럼 숫자를 공백 없이 다닥다닥 붙여 쓰셔도 자동으로 6개씩 쪼개어 스캔합니다.
""")

bulk_input = st.text_area(
    "✏️ 번호 묶음 입력칸 (예시 데이터를 지우고 번호를 넣으세요)",
    "010204060709111520212325\n7 10 15 25 38 44 / 030407101113\n1,5,7,11,25,36",
    height=250
)

# --- 4. 스캔 및 파싱 핵심 로직 가동 ---
if st.button(" 조합 일괄 스캔 시작!", use_container_width=True):
    if not parsed_sets:
        st.error("⚠️ 위쪽 칸에 세트 데이터가 비어있습니다. 이번 주 세트 번호를 확인해 주세요.")
    elif not bulk_input.strip():
        st.warning("⚠️ 스캔할 번호를 입력해 주세요!")
    else:
        # 특수 기호들을 모두 공백으로 치환하여 1차 정리
        clean_input = bulk_input.replace("/", " ").replace(".", " ").replace("-", " ").replace(",", " ")
        raw_tokens = clean_input.strip().split()
        
        all_numbers = []
        for token in raw_tokens:
            # 💡 [핵심 기능] 붙어있는 긴 숫자 데이터 분해 (예: '010203' -> 1, 2, 3)
            if len(token) >= 4 and token.isdigit():
                # 2자리씩 순차적으로 쪼개서 리스트에 추가
                chunks = [int(token[i:i+2]) for i in range(0, len(token), 2) if i+1 < len(token)]
                all_numbers.extend(chunks)
            # 💡 1자리 숫자나 공백/쉼표로 분리된 정상적인 숫자는 그대로 추가 (예: '7' -> 7 / '1' -> 1)
            elif token.isdigit():
                all_numbers.append(int(token))
                
        # 순수한 숫자 배열에서 앞에서부터 정확히 6개씩 칼같이 잘라내기 (카빙)
        valid_games = []
        for i in range(0, len(all_numbers), 6):
            chunk = all_numbers[i:i+6]
            if len(chunk) == 6:
                game_set = set(chunk)
                # 로또 유효 범위(1~45) 및 한 게임 내 중복 번호 검증을 통과한 것만 인정
                if len(game_set) == 6 and all(1 <= x <= 45 for x in game_set):
                    valid_games.append((len(valid_games) + 1, game_set))
        
        # --- 5. 결과 출력 ---
        if not valid_games:
            st.error("⚠️ 유효한 로또 조합을 추출하지 못했습니다. (1~45 사이 숫자군이 맞는지 확인해 주세요)")
        else:
            st.success(f"✅ 총 {len(valid_games)}게임의 조합을 완벽히 식별했습니다. 전수 대조 시스템 가동!")
            
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
                
                # 10개 세트 중 가장 많이 맞춘 '최고 기록' 세트 1개만 정렬하여 추출
                best_matches = sorted(best_matches, key=lambda x: x["count"], reverse=True)
                top_match = best_matches[0]
                results_to_show.append((game_num, my_numbers, top_match))
            
            # 아빠가 입력한 순서 그대로 결과를 일괄 출력
            for game_num, my_numbers, top_match in results_to_show:
                my_nums_str = ", ".join(f"{n:02d}" for n in sorted(list(my_numbers)))
                count = top_match["count"]
                set_name = top_match["set"]
                matched_str = ", ".join(f"{n:02d}" for n in top_match["matched"])
                
                if count == 6:
                    st.error(f" **[게임 {game_num}]** {my_nums_str} 👉 **{set_name}세트 6개 올적중!!!**")
                elif count == 5:
                    st.success(f" **[게임 {game_num}]** {my_nums_str} 👉 **{set_name}세트 5개 일치!** (일치 번호: {matched_str})")
                elif count == 4:
                    st.info(f" **[게임 {game_num}]** {my_nums_str} 👉 {set_name}세트 4개 일치 (일치 번호: {matched_str})")
                elif count == 3:
                    st.warning(f" **[게임 {game_num}]** {my_nums_str} 👉 {set_name}세트 3개 일치")
                else:
                    st.write(f"⚪ [게임 {game_num}] {my_nums_str} 👉 최고 {count}개 일치 ({set_name}세트)")

st.markdown("---")
st.caption("만든이: 전민규 (어떤 정렬 방식이든 6수씩 자동 분류하는 지능형 스마트 토큰 카빙 엔진 탑재)")
