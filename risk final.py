import streamlit as st
import matplotlib.pyplot as plt
import time

st.set_page_config(layout="wide", page_title="AI 스마트 배터리 JSA - 진정한 보완")
st.title("💡 AI 기반 스마트 배터리 JSA 위험성 평가 (선행 vs 후행 - 보완의 원리) 💡")
st.markdown("---")
st.write("안뇽냥뇽냥이! 👋 이 시스템은 **'현재의 안전 관리 노력'을 평가하는 선행지표**와 **'과거의 실제 사고 결과 및 관리 부실'을 분석하는 후행지표**를 각각 독립적으로 평가합니다. 두 지표의 본질적인 차이를 이해하고, **아리셀 배터리 공장 사고의 '교훈'을 후행지표에 반영하여 선행지표를 어떻게 보완하고 강화해야 하는지** 그 '피드백 루프'의 원리를 명확하게 제시합니다. ✨")
st.markdown("---")

# --- 배터리 제조 공정 단계 정의 ---
process_steps_info = {
    "양극 혼합 및 코팅": "배터리 재료(화학물질)를 혼합하고 전극에 코팅하는 단계. 화학물질 취급, 분진, 슬러리, 화재/폭발 위험이 있습니다.",
    "프레스 및 슬리팅": "코팅된 전극을 압착하여 밀도를 높이고(프레스) 폭에 맞춰 자르는(슬리팅) 단계. 기계적 끼임, 절단, 그리고 불량 제품(배터리)으로 인한 발열, 화재/폭발 위험이 내재되어 있습니다. 특히 이 공정은 **아리셀 배터리 공장 화재·폭발 사고가 발생한 핵심 '사고 발생 위치'**입니다.",
    "셀 조립 및 전해액 주입": "양극, 음극, 분리막을 조립하고(권취, 스태킹) 배터리 핵심 물질인 전해액을 주입하는 단계. 화학물질 유출, 중독, 질식, 화재 위험이 높습니다.",
    "밀봉 및 활성화": "전해액이 주입된 셀을 외부와 완벽히 차단하고(밀봉) 초기 충방전을 통해 셀의 성능을 깨우는(활성화) 단계. 밀봉 불량, 폭발(불량 셀), 화재, 과열 위험이 내재되어 있습니다.",
    "충방전 테스트": "완성된 셀, 모듈, 팩의 성능을 검사하기 위해 반복적인 충방전을 수행하는 단계. 과열, 발화, 폭발, 전기적 위험이 높습니다.",
    "모듈/팩 조립 및 최종 검사": "개별 셀들을 모듈 또는 팩 형태로 연결하고(배선, 용접) 최종 성능을 검사 후 포장하는 단계. 기계적 손상, 감전, 단락, 화재 위험이 내재되어 있습니다."
}
process_options = list(process_steps_info.keys())
selected_process_step = st.selectbox("🔋 배터리 제조 공정 단계 선택", process_options)

st.markdown("---")

# --- 1. 선행지표 입력 ---
st.subheader("1️⃣ 선행지표 입력 (현재 작업환경 및 관리 시스템 건전성 평가 - 예방 노력)")
st.markdown("현재 시점에서 작업장 환경, 설비 관리 상태, 작업자의 안전 행동, 그리고 전반적인 안전 관리 시스템의 **잠재적 위험 요인과 예방 노력**을 평가합니다.")

col1, col2 = st.columns(2)

with col1:
    st.write("### 👷 작업 환경")
    env_cleanliness = st.slider("작업장 청결도 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_env_c")
    env_ventilation = st.slider("작업장 환기 상태 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_env_v")
    env_orderliness = st.slider("작업장 정리정돈 상태 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_env_o")
    env_chemical_exposure = st.slider("환경 화학물질 노출 농도 (1:낮음 ~ 5:높음)", 1, 5, 2, key="s_env_ce")
    env_dust_level = st.slider("환경 분진 농도 (1:낮음 ~ 5:높음)", 1, 5, 2, key="s_env_d")

    st.write("### 👨‍🏭 작업자 안전 행동")
    worker_skill = st.selectbox("작업자 숙련도", ["미숙련", "보통", "숙련"], key="s_w_s")
    worker_safety_compliance = st.slider("작업자 안전수칙 준수도 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_w_sc")
    worker_ppe_compliance = st.slider("작업자 PPE 착용 준수도 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_w_ppe")
    worker_fatigue = st.slider("작업자 피로도 (1:낮음 ~ 5:높음)", 1, 5, 2, key="s_w_f")

with col2:
    st.write("### 🛠️ 설비 건전성 및 관리")
    equip_condition = st.slider("설비 종합 상태 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_e_c")
    equip_inspection_cycle = st.slider("설비 점검 주기 준수도 (1:미흡 ~ 5:우수)", 1, 5, 4, key="s_e_ic")
    equip_breakdown_history = st.select_slider("설비 최근 6개월 고장 이력", options=["없음", "1~2회", "3회 이상"], key="s_e_bh")
    equip_maintenance_quality = st.slider("설비 유지보수 품질 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_e_mq")

    st.write("### 🛡️ 안전 관리 시스템 (선행적 요소)")
    safety_inspection_status = st.selectbox("안전점검 체계 (현재 운영)", ["정기점검 완벽", "샘플점검 위주", "점검 미흡/미실시"], key="s_sm_is")
    fire_facility_adequacy = st.selectbox("소방시설 법적 기준 준수", ["기준 초과 설치", "법적 기준 준수", "설치 미흡/대상 아님"], key="s_sm_ffa")
    special_extinguisher_presence = st.radio("특수 소화기(배터리 전용) 보유 여부", ["보유", "미보유"], key="s_sm_sep")
    chemical_mgmt_msds = st.slider("화학물질 MSDS 관리 및 교육 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_c_msds")
    chemical_mgmt_storage = st.slider("화학물질 저장/취급 관리 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_c_st")
    jsa_performance = st.slider("JSA(작업안전분석) 수행 완성도 (1:낮음 ~ 5:높음)", 1, 5, 3, key="s_j_p")
    sops_compliance = st.slider("작업표준서(SOP) 준수도 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_s_c")
    worker_safety_education_freq = st.slider("정기 안전 교육 빈도 (월)", 0, 4, 1, key="s_w_sef")
    ptw_compliance = st.slider("작업허가제(PTW) 준수도 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_p_c")

st.markdown("---")

# --- 2. 후행지표 입력 ---
st.subheader("2️⃣ 후행지표 입력 (과거 사고 결과 및 관리 시스템의 '실질적 부실' 평가)")
st.markdown("과거에 실제로 발생했던 사고/사건, 법규 위반, 관리 시스템의 누적된 부실 등을 통해 **'시스템의 진정한 취약성'**을 평가합니다.")
st.markdown("💡 **만약 '아리셀 공장'의 사고 전 상태를 시뮬레이션한다면, 아래 항목들을 해당 사고가 발생할만한 상태로 설정해보세요! (특히 '예', '있음', '확인됨', '부적절/불법 논란', '미흡' 등을 선택)**")

col_lag1, col_lag2 = st.columns(2)

with col_lag1:
    st.write("### 💥 과거 사고 결과 (인명/재산/운영 손실)")
    # 사고 존재 유무 및 인명 피해
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

# --- 선행지표 '위험도 등급'에 따른 설명 ---
def get_leading_grade_description(grade):
    if grade == "매우 낮음": return "최소 위험 / 모니터링 유지"
    elif grade == "낮음": return "낮은 위험 / 점진적 개선 권고"
    elif grade == "보통": return "주의 필요 / 계획된 개선 조치 필요"
    elif grade == "높음": return "즉시 조치 필요 / 작업 통제 검토"
    else: return "위험 수용 불가 / 즉시 작업 중단"

# --- 후행지표 '위험 상태'에 따른 설명 ---
def get_lagging_status_description(status):
    if status == "클린 레코드": return "사고 이력 없음 / 시스템 양호"
    elif status == "주목할 문제 없음": return "사소한 문제 존재 / 지속적 관찰"
    elif status == "경고 필요 (Warning Required)": return "잠재적 사고 유발 요인 / 시스템 취약"
    elif status == "주요 시스템 부실 (Major System Failure)": return "심각 사고 발생 가능성 높음 / 시스템 결함"
    elif status == "심각한 결함 이력 (Critical Failure History)": return "대규모 인명피해 및 시스템 붕괴 / 총체적 부실"
    return "알 수 없음"

# --- 3. 선행지표 평가 함수 (Current Potential Risk) ---
def evaluate_leading_risk_score():
    score = 0
    # 작업 환경 (값이 낮을수록 위험)
    score += (6 - env_cleanliness) * 2
    score += (6 - env_ventilation) * 2
    score += (6 - env_orderliness) * 2
    score += env_chemical_exposure * 3 # 높을수록 위험
    score += env_dust_level * 3 # 높을수록 위험

    # 작업자 안전 행동
    if worker_skill == "미숙련": score += 5
    elif worker_skill == "보통": score += 2
    score += (6 - worker_safety_compliance) * 4 # 낮을수록 위험
    score += (6 - worker_ppe_compliance) * 4 # 낮을수록 위험
    score += (6 - worker_fatigue) * 2 # 피로도 높을수록 위험
    score += (5 - worker_safety_education_freq) * 2 # 교육 빈도 낮을수록 위험
    
    # 설비 건전성 및 관리
    score += (6 - equip_condition) * 4 # 낮을수록 위험
    score += (6 - equip_inspection_cycle) * 3 # 낮을수록 위험
    if equip_breakdown_history == "3회 이상": score += 5
    elif equip_breakdown_history == "1~2회": score += 2
    score += (6 - equip_maintenance_quality) * 3 # 낮을수록 위험

    # 안전 관리 시스템 (선행적 요소)
    if safety_inspection_status == "점검 미흡/미실시": score += 5
    elif safety_inspection_status == "샘플점검 위주": score += 3 # 아리셀 사례
    if fire_facility_adequacy == "설치 미흡/대상 아님": score += 4 # 아리셀 스프링클러 사례
    elif fire_facility_adequacy == "법적 기준 준수": score += 1
    if special_extinguisher_presence == "미보유": score += 5 # 아리셀 특수소화기 사례
    score += (6 - chemical_mgmt_msds) * 3 # 낮을수록 위험
    score += (6 - chemical_mgmt_storage) * 4 # 낮을수록 위험
    score += (6 - jsa_performance) * 3 # JSA 미흡시 위험
    score += (6 - sops_compliance) * 2 # SOP 준수 미흡시 위험
    score += (6 - ptw_compliance) * 3 # PTW 미준수시 위험

    return round(score, 2)

# --- 4. 후행지표 '위험 상태' 판별 및 내부 점수 계산 함수 ---
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
    if score >= 250: # 대규모 인명피해 또는 복합적이고 치명적인 부실
        status = "심각한 결함 이력 (Critical Failure History)"
    elif score >= 150: # 인명피해 또는 다수 심각 부실
        status = "주요 시스템 부실 (Major System Failure)"
    elif score >= 80: # 중등도 부실 (벌금, 은폐 의혹 등)
        status = "경고 필요 (Warning Required)"
    else: # 문제점 적거나 없음
        status = "주목할 문제 없음 (No Significant Issues)" # 이제 '클린 레코드'는 더 엄격한 기준에서 사용

    return status, score

# --- 평가 수행 ---
with st.spinner('위험성 평가를 분석 중입니다... 🧐'):
    time.sleep(1.5)
    leading_score_raw = evaluate_leading_risk_score()
    lagging_status, lagging_score_raw = get_lagging_status_and_score(
        past_fatalities_count, past_injuries_count, has_major_incident,
        past_fine_history_level, past_hazard_over_storage, past_hidden_accident_reports,
        past_safety_training_adequacy, past_safety_audit_compliance, past_government_intervention
    )

    leading_grade = leading_score_to_grade(leading_score_raw)
    leading_grade_desc = get_leading_grade_description(leading_grade) # 선행지표 등급별 설명 추가

# --- 5. 결과 출력 ---
st.subheader("✅ 위험성 평가 결과")
st.markdown("---")

col_res1, col_res2 = st.columns(2)
with col_res1:
    st.success("### 🚀 선행지표 위험도 등급 (예방 노력의 현황)")
    st.write(f"현재 관리 상태 기반 위험도 등급: **{leading_grade}**")
    st.markdown(f"_(조치 필요성: {leading_grade_desc})_")
    st.markdown(f"_(내부 점수: {leading_score_raw}점)_")
    st.markdown("""
    - **개념**: 현재 시점의 안전 관리 노력과 시스템의 건전성을 반영한 위험도. 잠재적인 사고 가능성을 예측합니다.
    - **활용**: 예방 활동 계획 수립 및 현재 관리 시스템 개선 방향 설정에 활용됩니다.
    """)
with col_res2:
    st.warning("### 🕰️ 후행지표 위험 상태 (과거 시스템의 실질적 부실)")
    st.write(f"과거 사고/부실 반영 위험 상태: **{lagging_status}**")
    st.markdown(f"_(내부 점수: {lagging_score_raw}점)_")
    st.markdown("""
    - **의미**: 과거의 실제 사고 이력, 법규 위반, 관리 시스템의 구조적 부실을 반영한 위험도. '숨겨진 위험'을 드러냅니다.
    - **활용**: 근본적인 문제점 파악 및 시스템적 개선, 과거의 교훈 학습에 활용됩니다.
    """)
st.markdown("---")

# --- 6. 선행 vs. 후행 지표 비교 분석 ---
st.subheader("🔍 선행 vs. 후행 지표 비교 분석: 아리셀 사고의 심층 교훈")
st.markdown("선행지표와 후행지표는 **본질적으로 다른 지표**이지만, 서로를 보완하며 **진정한 위험을 드러내고 미래의 안전을 설계하는 데 필수적**입니다. 후행지표(과거 데이터 및 관리 부실)를 통해 드러난 위험이 선행지표(현재의 관리 노력)를 어떻게 보완해야 하는지 비교합니다.")

col_comp_chart, col_comp_text = st.columns([0.6, 0.4])

with col_comp_chart:
    fig, ax = plt.subplots(figsize=(7, 4))
    # 등급별로 색상 조정 (선행지표 등급에 따라)
    bar_colors_leading = {'매우 낮음': 'lightgreen', '낮음': 'skyblue', '보통': 'lightyellow', '높음': 'salmon', '매우 높음': 'red'}
    bar_colors_lagging = {'클린 레코드': 'darkgreen', '주목할 문제 없음': 'forestgreen', '경고 필요 (Warning Required)': 'orange', '주요 시스템 부실 (Major System Failure)': 'darkorange', '심각한 결함 이력 (Critical Failure History)': 'darkred', '주요 인명 피해': 'darkred'}
    
    # 선행지표 등급의 색상과 후행지표 상태의 색상을 각각 적용
    bars = ax.bar(["선행지표", "후행지표"], [leading_score_raw, lagging_score_raw], 
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
        st.error(f"**❗ 경고: 후행지표 상태 '{lagging_status}'는 '{leading_grade}' 등급의 선행지표를 무색하게 합니다.**")
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

# --- 7. 후행지표 기반 선행지표 보완 루틴 ---
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