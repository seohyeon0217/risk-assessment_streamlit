import streamlit as st
import matplotlib.pyplot as plt
import time
import pandas as pd # pandas 추가

st.set_page_config(layout="wide", page_title="AI 스마트 배터리 JSA - 공정 특화")
st.title("💡 AI 기반 스마트 배터리 JSA 위험성 평가 (공정 특화 + 선행/후행 통합) 💡")
st.markdown("---")
st.write("안뇽냥뇽냥이! 👋 이 시스템은 **배터리 제조 4대 핵심 공정별로 특화된 위험요인**을 바탕으로 **현재의 안전 관리 노력(선행지표)**을 평가하고, **과거 사고/관리 부실(후행지표)**을 분석하여 위험도를 평가합니다. 후행지표를 통해 드러난 '사고의 교훈'을 선행지표 강화에 적용하는 **'피드백 루프'**를 구현하여, 가장 현실적이고 지능적인 안전 관리 시스템의 가능성을 제시합니다. ✨")
st.markdown("---")

# --- 배터리 제조 4대 핵심 공정 정의 및 정보 ---
battery_processes_details = {
    "전극 공정": {
        "desc": "양극/음극 활물질을 바인더와 섞어 슬러리를 만들고, 코팅, 건조, 프레스, 슬리팅하는 공정.",
        "risk_factors": {
            "화학물질(슬러리, 유기용제) 누출/흡입 위험 관리": {"type": "화학물질", "freq_map": {1:5,2:4,3:3,4:2,5:1}, "sev_map": {1:5,2:4,3:3,4:2,5:1}},
            "분진 발생 및 관리 수준": {"type": "환경", "freq_map": {1:5,2:4,3:3,4:2,5:1}, "sev_map": {1:4,2:3,3:2,4:1,5:1}},
            "고온 건조 설비 이상 및 관리": {"type": "설비", "freq_map": {1:4,2:3,3:2,4:1,5:1}, "sev_map": {1:4,2:3,3:2,4:1,5:1}},
            "프레스/슬리터 등 기계적 끼임/절단 위험 관리": {"type": "기계", "freq_map": {1:5,2:4,3:3,4:2,5:1}, "sev_map": {1:5,2:4,3:3,4:2,5:1}},
            "방폭 및 환기 설비 관리": {"type": "설비/화재", "freq_map": {1:5,2:4,3:3,4:2,5:1}, "sev_map": {1:5,2:4,3:3,4:2,5:1}},
        }
    },
    "조립 공정": {
        "desc": "전극을 감거나 쌓아 젤리롤/스택을 만들고, 케이스에 넣고 전해액 주입 후 밀봉하는 공정.",
        "risk_factors": {
            "전해액 주입 중 유출/흡입 위험 관리": {"type": "화학물질", "freq_map": {1:5,2:4,3:3,4:2,5:1}, "sev_map": {1:5,2:4,3:3,4:2,5:1}},
            "전해액/밀봉 관련 화재/폭발 위험 관리": {"type": "화재/화학", "freq_map": {1:5,2:4,3:3,4:2,5:1}, "sev_map": {1:5,2:4,3:3,4:2,5:1}},
            "권취/스태킹 장비 기계적 끼임 위험 관리": {"type": "기계", "freq_map": {1:4,2:3,3:2,4:1,5:1}, "sev_map": {1:4,2:3,3:2,4:1,5:1}},
            "비활성 가스(아르곤 등) 질식 위험 관리": {"type": "화학물질/환경", "freq_map": {1:4,2:3,3:2,4:1,5:1}, "sev_map": {1:5,2:4,3:3,4:2,5:1}},
            "용접/봉합 스파크 및 열적 위험 관리": {"type": "열", "freq_map": {1:3,2:2,3:1,4:1,5:1}, "sev_map": {1:3,2:2,3:1,4:1,5:1}},
        }
    },
    "활성화 공정": {
        "desc": "조립된 배터리에 초기 충방전을 통해 활물질을 활성화하고 품질 검사.",
        "risk_factors": {
            "불량 셀 열폭주/발화 위험 관리": {"type": "열/화재", "freq_map": {1:5,2:4,3:3,4:2,5:1}, "sev_map": {1:5,2:4,3:3,4:2,5:1}}, # 아리셀 사고와 직결
            "셀 내부 가스 발생 및 폭발 위험 관리": {"type": "폭발", "freq_map": {1:4,2:3,3:2,4:1,5:1}, "sev_map": {1:5,2:4,3:3,4:2,5:1}},
            "초기 전해액 누출 및 흡입 위험 관리": {"type": "화학물질", "freq_map": {1:3,2:2,3:1,4:1,5:1}, "sev_map": {1:4,2:3,3:2,4:1,5:1}},
            "충방전 설비의 전기적 위험 관리": {"type": "전기", "freq_map": {1:3,2:2,3:1,4:1,5:1}, "sev_map": {1:4,2:3,3:2,4:1,5:1}},
            "과열 모니터링 및 자동 진화 시스템 유무": {"type": "안전시스템", "freq_map": {1:5,2:4,3:3,4:2,5:1}, "sev_map": {1:5,2:4,3:3,4:2,5:1}},
        }
    },
    "팩 공정": {
        "desc": "여러 개의 셀을 모듈/팩으로 조립하고 배선, 보호회로 연결, 최종 검사 및 포장.",
        "risk_factors": {
            "고전압 배선 및 조립 중 감전 위험 관리": {"type": "전기", "freq_map": {1:5,2:4,3:3,4:2,5:1}, "sev_map": {1:5,2:4,3:3,4:2,5:1}},
            "셀/모듈 운반/적재 중 낙하/충격 위험 관리": {"type": "물리", "freq_map": {1:4,2:3,3:2,4:1,5:1}, "sev_map": {1:4,2:3,3:2,4:1,5:1}},
            "조립/용접 스파크 및 화재 위험 관리": {"type": "열/화재", "freq_map": {1:3,2:2,3:1,4:1,5:1}, "sev_map": {1:3,2:2,3:1,4:1,5:1}},
            "불량 팩 발화/폭발 위험 관리 (최종 검사)": {"type": "열/폭발", "freq_map": {1:4,2:3,3:2,4:1,5:1}, "sev_map": {1:5,2:4,3:3,4:2,5:1}},
            "포장/운반 자동화 설비 기계적 위험 관리": {"type": "기계", "freq_map": {1:3,2:2,3:1,4:1,5:1}, "sev_map": {1:3,2:2,3:1,4:1,5:1}},
        }
    }
}
process_options = list(battery_processes_details.keys())
selected_process_step = st.selectbox("🔋 배터리 제조 공정 단계 선택", process_options)
st.markdown(f"*{battery_processes_details[selected_process_step]['desc']}*")

st.markdown("---")

# --- 1. 선행지표 입력 (공정별 위험요인 세부 입력) ---
st.subheader("1️⃣ 선행지표 입력 (공정별 위험요인 관리 수준 평가)")
st.markdown("선택하신 공정의 주요 위험요인별 현재 안전 관리 수준을 입력해주세요. (1:불량 ~ 5:우수)")

leading_factors_input = {}
current_process_risk_factors = battery_processes_details[selected_process_step]["risk_factors"]

# 공정별 특화 위험요인 슬라이더로 입력
for i, (factor_name, factor_details) in enumerate(current_process_risk_factors.items()):
    leading_factors_input[factor_name] = st.slider(
        f"{factor_name} ({factor_details['type']})", 1, 5, 3, key=f"risk_{i}"
    )

# --- 2. 후행지표 입력 (과거 사고 및 관리 부실 중심) ---
st.subheader("2️⃣ 후행지표 입력 (과거 사고 결과 및 관리 시스템의 '실질적 부실' 평가)")
st.markdown("과거에 실제로 발생했던 사고/사건, 법규 위반, 관리 시스템의 누적된 부실 등을 통해 **'시스템의 진정한 취약성'**을 평가합니다.")
st.markdown("💡 **만약 '아리셀 공장'의 사고 전 상태를 시뮬레이션한다면, 아래 항목들을 해당 사고가 발생할만한 상태로 설정해보세요! (특히 '예', '있음', '확인됨', '부적절/불법 논란', '미흡' 등을 선택)**")

col_lag1, col_lag2 = st.columns(2)

with col_lag1:
    st.write("### 💥 과거 사고 결과 (인명/재산/운영 손실)")
    has_major_incident = st.radio("과거 대형/중대 재해(사망, 다수 부상 등)가 있었습니까?", ["없음", "있음"], key="l_pmao") 
    past_fatalities_count = 0
    past_injuries_count = 0
    if has_major_incident == "있음":
        past_fatalities_count = st.number_input("과거 대형 재해로 인한 사망자 수 (명)", min_value=0, value=0, key="l_f_c")
        past_injuries_count = st.number_input("과거 대형 재해로 인한 부상자 수 (명)", min_value=0, value=0, key="l_i_c")

    st.write("### 💸 과거 법규 위반 및 행정 처분")
    past_fine_history_level = st.selectbox("과거 안전 관련 벌금 부과 이력 (정성적 수준)", ["없음", "있음 (1회성)", "상습적/중요 위반 (2회 이상)"], key="l_pf_h")
    past_hazard_over_storage = st.selectbox("과거 위험물질 기준 초과 보관 적발 이력", ["없음", "있음"], key="l_ph_os") # 아리셀 리튬 초과 보관 반영

with col_lag2:
    st.write("### 📝 과거 안전 관리 시스템의 허점")
    past_hidden_accident_reports = st.selectbox("과거 경미 사고 보고 누락/은폐 정황이 있었습니까?", ["없음", "의혹 있음", "확인됨"], key="l_ph_ar")
    past_safety_training_adequacy = st.selectbox("과거 안전 교육 및 인력 관리 적절성 (특히 파견직)", ["매우 적절", "보통", "부적절/불법 논란"], key="l_pst_a")
    past_safety_audit_compliance = st.selectbox("과거 안전 감사 지적사항 개선 실적", ["모두 개선 완료", "일부 개선", "개선 미흡/형식적"], key="l_psa_c")
    past_government_intervention = st.selectbox("과거 정부/기관으로부터의 작업중지 또는 강력 권고 이행 여부", ["모두 이행", "일부 이행", "이행 미흡"], key="l_pg_i")

st.markdown("---")

# --- 위험도 수준 정의 ---
# 공정별 총 위험도 점수 범위
# 빈도(1-5) * 강도(1-5) = 최대 25점/요인. 요인별 갯수에 따라 총점 다름.
# 여기서는 5개 요인 * 25점 = 최대 125점으로 가정하고 등급을 나눔.
def get_risk_level(total_risk_score):
    if total_risk_score <= 20: return "매우 낮음" # Very Low
    elif total_risk_score <= 40: return "낮음"    # Low
    elif total_risk_score <= 60: return "보통"    # Medium
    elif total_risk_score <= 80: return "높음"    # High
    else: return "매우 높음" # Very High

# --- 3. 선행지표 평가 함수 (Current Potential Risk) ---
def evaluate_leading_risk_score():
    total_score = 0
    # 각 위험요인별 빈도, 강도 점수를 현재 관리 수준(1~5)에 따라 매핑하여 합산
    # 관리 수준이 낮을수록 (1점) 위험 빈도/강도가 높아짐
    current_process_risk_factors = battery_processes_details[selected_process_step]["risk_factors"]
    
    # 선행지표 요소 (점수 높을수록 위험)
    for factor_name, factor_details in current_process_risk_factors.items():
        input_value = leading_factors_input[factor_name] # 사용자가 슬라이더로 입력한 관리 수준
        
        freq = factor_details["freq_map"].get(input_value, 1) # 관리 수준에 따른 빈도
        sev = factor_details["sev_map"].get(input_value, 1)   # 관리 수준에 따른 강도
        
        total_score += (freq * sev)
    
    return total_score

# --- 후행지표 '위험 상태' 판별 및 내부 점수 계산 함수 ---
def get_lagging_status_and_score(fatalities, injuries, has_major_incident_bool, fine_history_level, over_storage, hidden_reports, training_adequacy, audit_compliance, govt_intervention):
    score = 0
    # 1. 인명 피해 (가장 강력한 요소)
    if has_major_incident_bool == "있음":
        if fatalities >= 10: # 아리셀 (23명 사망)급 대형 사고
            score += 250 # 최상위 점수 (치명적)
        elif fatalities > 0:
            score += 150 # 사망자 발생 시 매우 높은 점수
        elif injuries >= 5:
            score += 100 # 다수 부상자 발생 시 높은 점수
        elif injuries > 0:
            score += 50 # 부상자 발생 시 점수
    
    # 2. 법규 위반 및 행정 처분
    if fine_history_level == "있음 (1회성)": score += 30
    elif fine_history_level == "상습적/중요 위반 (2회 이상)": score += 60 
    if over_storage == "있음": score += 70 # 위험물질 초과 보관

    # 3. 과거 안전 관리 시스템의 허점
    if hidden_reports == "의혹 있음": score += 40
    elif hidden_reports == "확인됨": score += 80 # 확정된 은폐 시 더 심각
    
    if training_adequacy == "부적절/불법 논란": score += 70
    
    if audit_compliance == "50% 미만 (개선 미흡)": score += 60
    elif audit_compliance == "50%~99%": score += 30 # '일부 개선'에 해당하는 구간
    
    if govt_intervention == "이행 미흡": score += 50

    # 최종 상태 판별
    if score >= 250: # 인명피해 대규모 + 기타 부실
        status = "심각한 결함 이력 (Critical Failure History)"
    elif score >= 150: # 인명피해 또는 다수 심각 부실
        status = "주요 시스템 부실 (Major System Failure)"
    elif score >= 80: # 중등도 부실 (벌금, 은폐 의혹 등)
        status = "경고 필요 (Warning Required)"
    else: # 문제점 적거나 없음
        status = "주목할 문제 없음 (No Significant Issues)" # 이제 '클린 레코드'는 더 엄격한 기준에서 사용

    return status, score

# --- 5. 평가 수행 ---
with st.spinner('위험성 평가를 분석 중입니다... 🧐'):
    time.sleep(1.5)
    leading_score_raw = evaluate_leading_risk_score() # 선행지표 총 점수
    lagging_status, lagging_score_raw = get_lagging_status_and_score( # 후행지표 상태 및 점수
        past_fatalities_count, past_injuries_count, has_major_incident,
        past_fine_history_level, past_hazard_over_storage, past_hidden_accident_reports,
        past_safety_training_adequacy, past_safety_audit_compliance, past_government_intervention
    )

    leading_grade = get_risk_level(leading_score_raw) # 선행지표 등급
    
# --- 6. 결과 출력 ---
st.subheader("✅ 위험성 평가 결과")
st.markdown("---")

col_res1, col_res2 = st.columns(2)
with col_res1:
    st.success("### 🚀 선행지표 위험도 등급 (현재 관리 상태의 위험 수준)")
    st.write(f"**{selected_process_step} 공정의 현재 위험도:** **{leading_grade}** (총점: {leading_score_raw}점)")
    st.markdown("""
    - **의미**: 현재 시점의 안전 관리 노력과 시스템의 건전성을 반영한 위험도. 잠재적인 사고 가능성을 예측합니다.
    - **활용**: 예방 활동 계획 수립 및 현재 관리 시스템 개선 방향 설정에 활용됩니다.
    """)
with col_res2:
    st.warning("### 🕰️ 후행지표 위험 상태 (과거 사고 이력 및 관리 부실 수준)")
    st.write(f"**시스템의 과거 위험 상태:** **{lagging_status}** (내부 점수: {lagging_score_raw}점)")
    st.markdown("""
    - **의미**: 과거의 실제 사고 결과, 법규 위반, 관리 시스템의 구조적 부실을 반영한 위험도. '숨겨진 위험'을 드러냅니다.
    - **활용**: 근본적인 문제점 파악 및 시스템적 개선, 과거의 교훈 학습에 활용됩니다.
    """)
st.markdown("---")

# --- 7. 선행 vs. 후행 지표 비교 분석 ---
st.subheader("🔍 선행 vs. 후행 지표 비교 분석: 아리셀 사고의 심층 교훈")
st.markdown("선행지표와 후행지표는 **본질적으로 다른 지표**이지만, 서로를 보완하며 **진정한 위험을 드러내고 미래의 안전을 설계하는 데 필수적**입니다. 후행지표(과거 데이터 및 관리 부실)를 통해 드러난 위험이 선행지표(현재의 관리 노력)를 어떻게 보완해야 하는지 비교합니다.")

col_comp_chart, col_comp_text = st.columns([0.6, 0.4])

with col_comp_chart:
    fig, ax = plt.subplots(figsize=(7, 4))
    # 등급별/상태별 색상 조정
    bar_colors_leading = {'매우 낮음': 'lightgreen', '낮음': 'skyblue', '보통': 'lightyellow', '높음': 'salmon', '매우 높음': 'red'}
    bar_colors_lagging = {'주목할 문제 없음': 'forestgreen', '경고 필요 (Warning Required)': 'orange', '주요 시스템 부실 (Major System Failure)': 'darkorange', '심각한 결함 이력 (Critical Failure History)': 'darkred', '주요 인명 피해': 'darkred'}
    
    bars = ax.bar(["선행지표 위험도", "후행지표 위험 상태"], [leading_score_raw, lagging_score_raw], 
                   color=[bar_colors_leading.get(leading_grade, 'gray'), bar_colors_lagging.get(lagging_status, 'gray')])
    
    ax.set_ylim(0, max(leading_score_raw, lagging_score_raw) + 40) # y축 여유 공간 확보
    ax.set_ylabel("위험도 점수 (내부 계산)")
    ax.set_title(f"'{selected_process_step}' 공정 위험도 비교")

    # 그래프 위에 등급/상태 텍스트 표시
    for bar, text_display in zip(bars, [leading_grade, lagging_status]):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{text_display}\n({yval:.0f}점)", ha='center', va='bottom', fontsize=10, weight='bold')
    
    # 아리셀 사고 부실 사례를 그래프 옆에 주석으로 표시 (후행지표 상태가 심각할 경우)
    if lagging_status in ["주요 인명 피해", "주요 시스템 부실 (Major System Failure)", "심각한 결함 이력 (Critical Failure History)"]:
        ax.text(1.05, 0.95, "⚠️ **아리셀 사고와 같은 과거 문제점**", transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='lightcoral', ec='firebrick', lw=1, alpha=0.5))
        ax.text(1.05, 0.88, "- 사고 전 화재 은폐 의혹", transform=ax.transAxes, fontsize=8, verticalalignment='top')
        ax.text(1.05, 0.81, "- 안전점검 체계의 허점", transform=ax.transAxes, fontsize=8, verticalalignment='top')
        ax.text(1.05, 0.74, "- 특수 소화기 부재", transform=ax.transAxes, fontsize=8, verticalalignment='top')
        ax.text(1.05, 0.67, "- 위험물질 초과 보관", transform=ax.transAxes, fontsize=8, verticalalignment='top')
        ax.text(1.05, 0.60, "- 안전교육/인력관리 부실", transform=ax.transAxes, fontsize=8, verticalalignment='top')
        ax.text(1.05, 0.53, "➡ **후행지표가 이를 강력히 경고!**", transform=ax.transAxes, fontsize=9, verticalalignment='top', color='red')
        fig.tight_layout() # 그래프와 주석 겹치지 않게 레이아웃 조정
    
    st.pyplot(fig)


with col_comp_text:
    # 선행 vs 후행 등급 비교 해석
    if lagging_status == "심각한 결함 이력 (Critical Failure History)":
        st.error(f"**❗ 경고: 후행지표 상태 '{lagging_status}'는 선행지표 '{leading_grade}' 등급의 현재 노력을 무색하게 합니다.**")
        st.markdown(f"""
        ### 아리셀 사고의 총체적 부실, 단계별 심층 분석
        **과거의 치명적인 문제들이 실제 사고로 이어졌거나, 사고를 일으킬 만한 시스템적 부실이 누적되어 있었다는 것을 의미합니다. 선행지표로 가려졌던 허점이 후행지표를 통해 드러났습니다.**
        """)
        # 인터랙티브 UI 요소 (Expander 사용)
        with st.expander("단계 1: 겉으로만 보이는 안전과 숨겨진 위험"):
            st.markdown("""
            **문제점**: 아리셀 사고 이전, 공장은 '우수사업장'으로 선정되기도 했습니다. 이는 **선행지표(형식적 점검, 서류상 기준)만으로는 실제 위험을 포착하기 어려움**을 보여줍니다. **현재의 청결도, 설비 점검 주기가 양호해 보여도, 시스템적/문화적 부실은 가려질 수 있습니다.**
            """)
        with st.expander("단계 2: 과거 관리 부실의 치명적인 누적"):
            st.markdown("""
            **원인**: 사고 전 **사고 전 화재 은폐 의혹, 위험물질 초과 보관 벌금 이력, '샘플 점검'에 그친 안전점검, 그리고 감사 지적 개선 미흡** 등 과거의 '숨겨진 부실'이 존재했습니다. 이는 후행지표가 '심각한 결함 이력'을 보인 핵심적인 이유입니다. **명목상의 안전 관리가 아닌, 실제 위험을 통제하지 못했던 결과가 이 상태로 직결됩니다.**
            """)
        with st.expander("단계 3: 고위험 공정의 특성과 부실의 폭발적인 시너지"):
            st.markdown(f"""
            **상황**: 특히 '{selected_process_step}'과 같은 고에너지 배터리 공정에서는 불량 제품 처리 과정의 사소한 문제(과도한 발열, 열폭주)가 **대형 폭발로 이어질 수 있는 치명적 위험**을 내포합니다. 이러한 고위험 상황에서 **특수 소화기 부재, 부실한 비상 대응 훈련** 등이 관리 시스템의 허점을 더욱 부각시켜 후행지표 등급을 폭발적으로 상승시키는 요인이 됩니다.
            """)
        with st.expander("단계 4: 인적 요소 및 법규 사각지대의 위험 증폭"):
            st.markdown("""
            **결과**: 불법 파견 논란 속 **파견직에 대한 안전 교육 부실**은 미숙련 작업자의 안전 행동 위험을 가중시켰습니다. 또한 **소방법상 리튬 화재의 특수성 미반영, 특수 소화기 규정 미비** 등 법규와 현실의 괴리가 사고를 키운 원인이 됩니다. **과거 불법 파견 적발, 교육 이수율 저조와 같은 후행지표는 이러한 인적/시스템적 취약점을 명백히 보여줍니다.**
            """)
        st.markdown(f"""
        **총평**: 후행지표 상태가 심각하다는 것은 이처럼 **단순히 과거 사고 빈도가 높아서가 아니라, 그 이면에 깔린 총체적 관리 부실과 시스템적 결함이 축적된 결과**입니다. 이는 형식적인 선행지표 관리만으로는 대형 사고를 막을 수 없으며, **과거의 실질적 문제를 직시하고 개선해야만 진정한 안전이 확보됨을 강력히 경고**합니다.
        """)
        st.markdown("---")
    
    elif lagging_status == "주요 시스템 부실 (Major System Failure)":
        st.error(f"**❗ 경고: 후행지표 상태 '{lagging_status}'는 선행지표 '{leading_grade}'에도 불구하고 시스템의 주요 결함을 나타냅니다.**")
        st.markdown("""
        과거 인명 피해가 발생했거나, 다수의 법규 위반 및 관리 허점들이 누적되었음을 의미합니다. 선행지표가 현재의 노력을 보여주더라도, 이러한 과거의 '큰 문제들'은 현재 시스템에 근본적인 취약점이 있음을 시사합니다. 즉각적이고 전반적인 개선 노력이 시급합니다.
        """)
        st.markdown("---")

    elif lagging_status == "경고 필요 (Warning Required)":
        st.warning(f"**⚠ 후행지표 상태 '{lagging_status}': 현재는 안전해 보여도 과거의 경고 신호에 주목해야 합니다.**")
        st.markdown("""
        과거 안전 관련 벌금, 보고 누락 의혹, 감사 지적 개선 미흡 등 **경고 신호들이 존재했음을 의미합니다.** 현재 선행지표 등급이 양호하더라도, 이러한 과거의 작은 문제들이 누적되면 언제든 대형 사고로 이어질 수 있습니다. 즉각적인 원인 분석과 개선 노력이 필요합니다.
        """)
        st.markdown("---")

    else: # 클린 레코드 또는 주목할 문제 없음
        st.info(f"**✅ 후행지표 상태 '{lagging_status}': 현재 관리 노력이 과거 데이터와 일치합니다.**")
        st.markdown("""
        과거에 큰 사고나 심각한 관리 부실 이력이 없음을 나타냅니다. 이는 현재의 선행지표 기반 예방 노력이 잘 작동하고 있다는 긍정적인 신호입니다. 하지만, '클린 레코드'가 영원한 안전을 보장하지 않으므로, 지속적인 위험성 평가와 개선 노력을 통해 현재의 높은 안전 수준을 유지해야 합니다.
        """)
        st.markdown("---")

# --- 8. 후행지표 기반 선행지표 보완 루틴 ---
st.subheader("🔁 후행지표 기반 선행지표 보완 루틴: 사고의 교훈을 미래 안전으로")
st.markdown("아리셀 사고와 같은 중대 재해의 **'과거 데이터(후행지표)'를 분석**하여, **미래의 사고를 막을 수 있는 '선행지표'를 어떻게 강화**할 수 있는지 보여주는 루틴입니다.")

# Streamlit Session State 초기화
if 'show_rca' not in st.session_state:
    st.session_state.show_rca = False
if 'rca_applied' not in st.session_state:
    st.session_state.rca_applied = False

# 사고 발생 버튼
if st.button("🚨 사고 발생! (후행지표 인지 & 보완 루틴 시작)"):
    st.session_state.show_rca = True
    st.session_state.rca_applied = False # 새로운 사고 발생 시 루틴 초기화

if st.session_state.show_rca:
    st.markdown("---")
    st.success("### ✅ 사고 데이터 수집 및 원인 분석 (RCA)")
    st.markdown("""
    **사고 시나리오**: 2024년 6월, 화성 아리셀 공장 '프레스 및 슬리팅' 공정에서 불량 리튬이온 배터리 처리 중 폭발, 대규모 인명 피해 발생 (사망 23명). 
    """)
    st.markdown("""
    **RCA (Root Cause Analysis) 결과**:
    - **직접 원인**: 불량 배터리 열폭주, 초기 화재 진압 실패 (일반 소화기 사용, 특수 소화기 부재)
    - **간접 원인**: 과밀 적재, 통풍 불량, 정전기 등 발화 조건, 불량품 관리 미흡, **사고 전 경미 화재 은폐, 안전점검 부실, 위험물질 초과 보관**
    - **근본 원인**: **안전 관리 시스템 총체적 부실** (명목상 '우수사업장'이었으나 실제로는 JSA, SOP, PTW 등 형식적 관리, 교육 미흡, 인력관리 문제, 비상 대응 훈련 미흡)
    """)
    st.markdown("---")
    st.warning("### 🛠️ 미흡했던 선행지표 도출 및 강화된 선행지표 제안")
    st.markdown("""
    위 RCA 결과에 따라, 사고 이전에 '작동했어야 할' 선행지표들이 무엇이었고, 앞으로 어떻게 강화되어야 할지 도출합니다.
    """)

    st.markdown("#### 🔍 미흡했던 과거 선행지표 (아리셀 사례):")
    st.markdown("- **[관리 부실]** **안전점검 체계**: '샘플 점검'으로 실제 위험 간과.")
    st.markdown("- **[안전 설비 부재]** **소방시설**: 스프링클러 설치 의무 대상 아님, **특수 소화기 부재**.")
    st.markdown("- **[위험물 관리]** **화학물질 저장 관리**: 리튬 등 위험물질 규정 초과 보관 (벌금 이력).")
    st.markdown("- **[행동 안전/교육]** **작업자 안전 교육**: 파견직 등 안전 교육 및 관리 부실 (불법 파견 논란).")
    st.markdown("- **[절차/모니터링]** **JSA, SOP, PTW**: 수행 완성도 낮거나 형식적, 온도/습도 모니터링 부재.")
    st.markdown("- **[비상 대응]** **대피 경로/훈련**: 피난유도등 미흡, 비상 훈련 부실 (작업자 전원 사망).")

    st.markdown("#### ✅ 강화된 선행지표 제안 (선택하여 반영):")
    
    enhance_options = {
        "JSA(작업안전분석) 수행 완성도 높임": False,
        "작업표준서(SOP) 준수도 강화": False,
        "작업허가제(PTW) 엄격 적용": False,
        "배터리 보관 온도/습도 자동 센서 및 경고 시스템 도입": False,
        "정전기 발생 가능성 평가 및 방지 대책 강화": False,
        "방폭 환기 시스템 점검 및 보강": False,
        "리튬 특성 및 비상 대응 훈련 강화 (월 1회 이상)": False,
        "피난 유도등 및 비상 대피 경로 확보/훈련 강화": False,
        "전사적 정기 안전점검 의무화 및 실질 점검 강화": False,
        "배터리 전용 특수 소화기 비치 및 소방 시설 보강": False,
        "위험물질 저장/취급 규정 준수 및 실시간 모니터링": False,
        "파견직 포함 전 직원에 대한 철저한 안전 교육 실시": False
    }

    for option, _ in enhance_options.items():
        enhance_options[option] = st.checkbox(option, value=False, key=f"enhance_{option.replace(' ', '_')}")

    if st.button("✔ 선택된 선행지표 강화 제안 반영 (시뮬레이션)"):
        st.session_state.rca_applied = True # 반영 트리거
        st.success("**JSA 평가서 갱신 및 선행지표 강화 방안이 성공적으로 반영되었습니다!**")
        st.markdown("""
        - **JSA 자동 업데이트**: 관련 작업 JSA 항목에 선택된 강화된 선행지표가 추가/업데이트됩니다.
        - **관리자 알림**: 안전 관리자에게 변경된 JSA 및 강화 방안이 자동 통보됩니다.
        - **작업자 교육**: 변경된 내용에 대한 작업자 교육 일정이 자동 등록되고, 교육 이수 후 적용됩니다.
        - **주기적 모니터링**: 강화된 선행지표의 실제 적용 및 효과에 대한 모니터링이 시작됩니다.
        """)
    
    if st.session_state.rca_applied:
        st.info("💡 이제 선행지표 입력 부분으로 돌아가, **선택된 강화 방안에 맞춰 입력 값을 변경하여 재평가**하면, 위험도가 어떻게 낮아지는지 확인할 수 있습니다.")

st.markdown("---")
st.info("⭐ **중요**: 본 시스템은 한국산업안전보건공단 및 고용노동부 자료, 그리고 아리셀 사고와 같은 실제 사례를 참고하여 개발된 AI 기반의 예측/추천 자료입니다. 실제 현장 상황과 위험도는 다를 수 있으므로, 반드시 **전문가의 정밀 진단 및 현장 특성을 고려한 위험성 평가**를 수행해야 합니다. 모든 기업과 근로자는 **산업안전보건법 및 중대재해처벌법을 준수**하여 안전한 작업 환경을 조성할 의무가 있습니다. 안전은 언제나 최우선입니다! ⭐")