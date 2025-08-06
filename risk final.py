import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

st.set_page_config(layout="wide", page_title="AI 스마트 배터리 JSA - F/S 직접 입력")
st.title("💡 AI 기반 스마트 배터리 JSA 위험성 평가 (F/S 직접 입력 + 선행/후행 통합) 💡")
st.markdown("---")
st.write("안뇽냥뇽냥이! 👋 이 시스템은 **배터리 제조 4대 핵심 공정별로 특화된 위험요인**에 대해 **빈도(F)와 강도(S)를 직접 입력**하여 위험도를 평가하고, **현재의 안전 관리 노력(선행지표)**과 **과거 사고/관리 부실(후행지표)**을 분석합니다. 후행지표를 통해 드러난 '사고의 교훈'을 선행지표 강화에 적용하는 **'피드백 루프'**를 구현하여, 가장 현실적이고 지능적인 안전 관리 시스템의 가능성을 제시합니다. ✨")
st.markdown("---")

# --- 배터리 제조 4대 핵심 공정 정의 및 정보 ---
# 각 공정별 주요 위험요인 리스트를 정의
# (여기서는 직접 빈도/강도를 입력받으므로 freq_map/sev_map은 더 이상 사용하지 않음)
battery_processes_details = {
    "전극 공정": {
        "desc": "양극/음극 활물질을 바인더와 섞어 슬러리를 만들고, 코팅, 건조, 프레스, 슬리팅하는 공정. (화학물질 취급, 분진, 화재/폭발, 기계적 위험)",
        "risk_factors": [
            {"name": "화학물질(슬러리, 유기용제) 누출/흡입", "type": "화학물질"},
            {"name": "분진 발생 및 관리", "type": "환경/호흡기"},
            {"name": "고온 건조 설비 이상 및 발열", "type": "설비/열상"},
            {"name": "프레스/슬리터 등 기계적 끼임/절단", "type": "기계"},
            {"name": "방폭 및 환기 설비 미흡", "type": "설비/화재"},
        ]
    },
    "조립 공정": {
        "desc": "전극을 감거나 쌓아 젤리롤/스택을 만들고, 케이스에 넣고 전해액 주입 후 밀봉하는 공정. (화학물질, 질식, 기계적, 열적 위험)",
        "risk_factors": [
            {"name": "전해액 주입 중 유출/흡입", "type": "화학물질"},
            {"name": "전해액/밀봉 관련 화재/폭발", "type": "화재/화학"},
            {"name": "권취/스태킹 장비 기계적 끼임", "type": "기계"},
            {"name": "비활성 가스(아르곤 등) 질식", "type": "화학물질/환경"},
            {"name": "용접/봉합 스파크 및 열적 위험", "type": "열"},
        ]
    },
    "활성화 공정": {
        "desc": "조립된 배터리에 초기 충방전을 통해 활물질을 활성화하고 품질 검사. (열폭주, 가스 발생, 전기적 위험)",
        "risk_factors": [
            {"name": "불량 셀 열폭주/발화", "type": "열/화재"}, # 아리셀 사고와 직결
            {"name": "셀 내부 가스 발생 및 폭발", "type": "폭발"},
            {"name": "초기 전해액 누출 및 흡입", "type": "화학물질"},
            {"name": "충방전 설비의 전기적 위험", "type": "전기"},
            {"name": "과열 모니터링 및 진화 시스템 미흡", "type": "안전시스템"},
        ]
    },
    "팩 공정": {
        "desc": "여러 개의 셀을 모듈/팩으로 조립하고 배선, 보호회로 연결, 최종 검사 및 포장. (전기적, 물리적, 열적 위험)",
        "risk_factors": [
            {"name": "고전압 배선 및 조립 중 감전", "type": "전기"},
            {"name": "셀/모듈 운반/적재 중 낙하/충격", "type": "물리"},
            {"name": "조립/용접 스파크 및 화재", "type": "열/화재"},
            {"name": "불량 팩 발화/폭발 (최종 검사)", "type": "열/폭발"},
            {"name": "포장/운반 자동화 설비 기계적 위험", "type": "기계"},
        ]
    }
}
process_options = list(battery_processes_details.keys())
selected_process_step = st.selectbox("🔋 배터리 제조 공정 단계 선택", process_options)
st.markdown(f"*{battery_processes_details[selected_process_step]['desc']}*")

st.markdown("---")

# --- 1. 선행지표 입력 (공정별 빈도/강도 직접 입력) ---
st.subheader("1️⃣ 선행지표 입력 (공정별 위험요인 빈도/강도 직접 평가)")
st.markdown("선택하신 공정의 주요 위험요인별 **빈도(F)와 강도(S)**를 직접 입력해주세요. (F: 1=거의 없음 ~ 5=매우 자주, S: 1=경미 ~ 5=사망/치명적)")

leading_factors_f_s_input = {}
current_process_risk_factors_list = battery_processes_details[selected_process_step]["risk_factors"]

# 공정별 특화 위험요인별 빈도/강도 슬라이더로 입력
for i, factor in enumerate(current_process_risk_factors_list):
    col_f, col_s, col_risk = st.columns(3)
    with col_f:
        freq = st.slider(f"{factor['name']} (F)", 1, 5, 3, key=f"freq_{selected_process_step}_{i}")
    with col_s:
        sev = st.slider(f"{factor['name']} (S)", 1, 5, 3, key=f"sev_{selected_process_step}_{i}")
    with col_risk:
        risk_fs = freq * sev
        st.write(f"**위험도 (F*S): {risk_fs}**")
        leading_factors_f_s_input[factor['name']] = {'freq': freq, 'sev': sev, 'risk': risk_fs}

st.markdown("---")

# --- 추가 선행지표 입력 (전사적 안전 관리 시스템) ---
st.subheader("1-2️⃣ 추가 선행지표 입력 (전사적 안전 관리 시스템 건전성 평가)")
st.markdown("회사 전체의 안전 관리 시스템과 관련된 잠재적 위험 요인과 예방 노력을 평가합니다.")

col1, col2 = st.columns(2)
with col1:
    st.write("### 👷 전사적 작업 환경 관리")
    env_cleanliness = st.slider("전사적 작업장 청결도 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_env_c_total")
    env_ventilation = st.slider("전사적 작업장 환기 상태 (1:불량 ~ 5:5)", 1, 5, 3, key="s_env_v_total")
    env_orderliness = st.slider("전사적 작업장 정리정돈 상태 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_env_o_total")
    env_chemical_exposure = st.slider("전사적 환경 화학물질 노출 관리 수준 (1:높음 ~ 5:낮음)", 1, 5, 4, key="s_env_ce_total") # 관리 수준이므로 5점이 좋음
    env_dust_level = st.slider("전사적 환경 분진 관리 수준 (1:높음 ~ 5:낮음)", 1, 5, 4, key="s_env_d_total")

    st.write("### 👨‍🏭 전사적 작업자 관리")
    worker_skill = st.selectbox("전체 작업자 평균 숙련도", ["미숙련", "보통", "숙련"], key="s_w_s_total")
    worker_safety_compliance = st.slider("전체 작업자 안전수칙 준수도 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_w_sc_total")
    worker_ppe_compliance = st.slider("전체 작업자 PPE 착용 준수도 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_w_ppe_total")
    worker_fatigue_mgmt = st.slider("작업자 피로 관리 시스템 (1:미흡 ~ 5:우수)", 1, 5, 3, key="s_w_f_total")

with col2:
    st.write("### 🛠️ 전사적 설비 관리")
    equip_condition = st.slider("전체 설비 평균 건전성 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_e_c_total")
    equip_inspection_cycle = st.slider("전사적 설비 점검 주기 준수율 (1:미흡 ~ 5:우수)", 1, 5, 4, key="s_e_ic_total")
    equip_breakdown_history = st.select_slider("전사적 설비 고장 이력 (6개월)", options=["없음", "1~2회", "3회 이상"], key="s_e_bh_total")
    equip_maintenance_quality = st.slider("전사적 설비 유지보수 품질 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_e_mq_total")

    st.write("### 🛡️ 전사적 안전 관리 시스템 (총괄)")
    safety_inspection_status = st.selectbox("전사적 안전점검 체계", ["정기점검 완벽", "샘플점검 위주", "점검 미흡/미실시"], key="s_sm_is_total")
    fire_facility_adequacy = st.selectbox("전사적 소방시설 법적 기준 준수", ["기준 초과 설치", "법적 기준 준수", "설치 미흡/대상 아님"], key="s_sm_ffa_total")
    special_extinguisher_presence = st.radio("전사적 특수 소화기(배터리 전용) 보유 여부", ["보유", "미보유"], key="s_sm_sep_total")
    chemical_mgmt_msds = st.slider("전사적 화학물질 MSDS 관리 및 교육 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_c_msds_total")
    chemical_mgmt_storage = st.slider("전사적 화학물질 저장/취급 관리 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_c_st_total")
    jsa_performance = st.slider("JSA(작업안전분석) 수행 완성도 (1:낮음 ~ 5:높음)", 1, 5, 3, key="s_j_p_total")
    sops_compliance = st.slider("작업표준서(SOP) 준수도 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_s_c_total")
    worker_safety_education_freq = st.slider("정기 안전 교육 빈도 (월)", 0, 4, 1, key="s_w_sef_total")
    ptw_compliance = st.slider("작업허가제(PTW) 준수도 (1:불량 ~ 5:우수)", 1, 5, 3, key="s_p_c_total")

st.markdown("---")

# --- 2. 후행지표 입력 (과거 사고 및 관리 부실 중심) ---
st.subheader("2️⃣ 후행지표 입력 (과거 사고 결과 및 관리 부실 심층 분석)")
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
    # 1. 공정별 위험요인 JSA 점수 합산
    total_jsa_risk = 0
    detailed_jsa_risks = [] # JSA 상세 정보를 저장할 리스트

    current_process_risk_factors = battery_processes_details[selected_process_step]["risk_factors"]
    for factor in current_process_risk_factors:
        freq = leading_factors_f_s_input[factor['name']]['freq']
        sev = leading_factors_f_s_input[factor['name']]['sev']
        risk_score = freq * sev
        total_jsa_risk += risk_score
        detailed_jsa_risks.append({
            "위험요인": factor['name'],
            "유형": factor['type'],
            "빈도(F)": freq,
            "강도(S)": sev,
            "위험도(F*S)": risk_score
        })
    
    # 2. 전사적 선행지표 점수 계산 (각 지표의 관리 수준이 낮을수록(1점) 점수가 높아지도록)
    score = 0
    # 전사적 작업 환경 관리
    score += (6 - env_cleanliness) * 2
    score += (6 - env_ventilation) * 2
    score += (6 - env_orderliness) * 2
    score += (6 - env_chemical_exposure) * 3 # 5점이 좋으므로 6-점으로
    score += (6 - env_dust_level) * 3

    # 전사적 작업자 관리
    if worker_skill == "미숙련": score += 5
    elif worker_skill == "보통": score += 2
    score += (6 - worker_safety_compliance) * 4
    score += (6 - worker_ppe_compliance) * 4
    score += (6 - worker_fatigue_mgmt) * 2 # 피로도 '관리 수준'이므로 6-점으로
    
    # 정기 안전 교육 빈도 (월) - 0~4회. 0회는 위험 최고, 4회는 위험 최저. 5-Freq 사용
    score += (5 - worker_safety_education_freq) * 2 

    # 전사적 설비 관리
    score += (6 - equip_condition) * 4
    score += (6 - equip_inspection_cycle) * 3
    if equip_breakdown_history == "3회 이상": score += 5
    elif equip_breakdown_history == "1~2회": score += 2
    score += (6 - equip_maintenance_quality) * 3

    # 전사적 안전 관리 시스템 (총괄)
    if safety_inspection_status == "점검 미흡/미실시": score += 5
    elif safety_inspection_status == "샘플점검 위주": score += 3 # 아리셀 사례
    if fire_facility_adequacy == "설치 미흡/대상 아님": score += 4 # 아리셀 스프링클러 사례
    elif fire_facility_adequacy == "법적 기준 준수": score += 1
    if special_extinguisher_presence == "미보유": score += 5 # 아리셀 특수소화기 사례
    score += (6 - chemical_mgmt_msds) * 3
    score += (6 - chemical_mgmt_storage) * 4
    score += (6 - jsa_performance) * 3 # JSA 미흡시 위험
    score += (6 - sops_compliance) * 2 # SOP 준수 미흡시 위험
    score += (6 - ptw_compliance) * 3 # PTW 미준수시 위험

    # JSA 위험도와 전사적 선행지표 점수를 합산
    # JSA 위험도는 공정별 상세 위험이므로, 전사적 관리 점수에 더해줌
    final_leading_score = total_jsa_risk + score
    
    return final_leading_score, pd.DataFrame(detailed_jsa_risks)

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
    leading_score_raw, jsa_details_df = evaluate_leading_risk_score() # 선행지표 총 점수와 JSA 상세 정보 반환
    
    lagging_status, lagging_score_raw = get_lagging_status_and_score(
        past_fatalities_count, past_injuries_count, accident_occurred, # 'accident_occurred' radio button value used here
        past_fine_history_level, past_hazard_over_storage, past_hidden_accident_reports,
        past_safety_training_adequacy, past_safety_audit_compliance, past_government_intervention
    )

    leading_grade = get_risk_level(leading_score_raw) # 선행지표 등급
    
# --- 6. 결과 출력 ---
st.subheader("✅ 위험성 평가 결과")
st.markdown("---")

col_res1, col_res2 = st.columns(2)
with col_res1:
    st.success("### 🚀 선행지표 위험도 등급 (예방 노력의 현황)")
    st.write(f"현재 관리 상태 기반 위험도 등급: **{leading_grade}**")
    st.markdown(f"_(총점: {leading_score_raw}점, 조치 필요성: {get_leading_grade_description(leading_grade)})_")
    st.markdown("""
    - **의미**: 현재 시점의 안전 관리 노력과 시스템의 건전성을 반영한 위험도. 잠재적인 사고 가능성을 예측합니다.
    - **활용**: 예방 활동 계획 수립 및 현재 관리 시스템 개선 방향 설정에 활용됩니다.
    """)
    st.write("#### 공정별 위험요인 상세 (빈도 x 강도)")
    st.table(jsa_details_df) # JSA 위험요인 상세 표로 출력

with col_res2:
    st.warning("### 🕰️ 후행지표 위험 상태 (과거 시스템의 실질적 부실)")
    st.write(f"과거 사고/부실 반영 위험 상태: **{lagging_status}** (내부 점수: {lagging_score_raw}점)")
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
    bar_colors_lagging = {'주목할 문제 없음': 'forestgreen', '경고 필요 (Warning Required)': 'orange', '주요 시스템 부실 (Major System Failure)': 'darkorange', '심각한 결함 이력 (Critical Failure History)': 'darkred', '주요 인명 피해': 'darkred', '클린 레코드': 'darkgreen'}
    
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

# --- 8. 위험성 감소 대책 및 실행 후 위험도 시뮬레이션 ---
st.subheader("8. 위험성 감소 대책 및 실행 후 위험도 시뮬레이션")
st.markdown("선택된 공정에서 식별된 위험요인에 대해 감소 대책을 수립하고, 실행 후 위험도 감소 효과를 시뮬레이션합니다.")

# 위험요인 목록을 가져와서 감소량 입력 필드 생성
if selected_process_step: # 공정이 선택되어야 함
    current_process_risk_factors_list = battery_processes_details[selected_process_step]["risk_factors"]
    
    # 이 공정의 총 JSA 위험도를 가져옴
    initial_jsa_total_risk = sum(item['risk'] for item in leading_factors_f_s_input.values())

    st.write(f"#### {selected_process_step} 공정 (위험도 감소 대책)")
    reduced_risk_amounts = {}
    
    # 각 위험요인별 위험도(F*S) 값과 해당 위험요인 이름 저장
    jsa_risk_values_dict = {item['name']: item['risk'] for item in leading_factors_f_s_input.values()}
    
    for factor in current_process_risk_factors_list:
        factor_name = factor['name']
        current_risk_fs = jsa_risk_values_dict.get(factor_name, 0)
        
        # 위험도 감소 예상량 입력
        reduced_risk_amounts[factor_name] = st.number_input(
            f"'{factor_name}' 위험도 감소 예상량 (0~{current_risk_fs})", 
            min_value=0, 
            max_value=int(current_risk_fs),
            value=0,
            key=f"reduce_{selected_process_step}_{factor_name}"
        )

    if st.button("감소 대책 적용 및 위험도 재평가 시뮬레이션"):
        st.markdown("---")
        st.subheader("📉 감소 대책 적용 후 예상 위험도")
        
        simulated_jsa_details = []
        simulated_total_jsa_risk = 0
        
        for factor in current_process_risk_factors_list:
            factor_name = factor['name']
            current_risk_fs = jsa_risk_values_dict.get(factor_name, 0)
            reduction_amount = reduced_risk_amounts.get(factor_name, 0)
            
            simulated_risk_fs = max(0, current_risk_fs - reduction_amount) # 0 미만 방지
            simulated_total_jsa_risk += simulated_risk_fs
            
            simulated_jsa_details.append({
                "위험요인": factor_name,
                "유형": factor['type'],
                "빈도(F)": leading_factors_f_s_input[factor_name]['freq'], # 감소 전 빈도
                "강도(S)": leading_factors_f_s_input[factor_name]['sev'],   # 감소 전 강도
                "기존 위험도(F*S)": current_risk_fs,
                "감소 예상량": reduction_amount,
                "감소 후 위험도(F*S)": simulated_risk_fs
            })
        
        # 전사적 선행지표 점수 재계산 (JSA 위험도는 simulated_total_jsa_risk로 대체)
        # 이 부분은 evaluate_leading_risk_score 함수 내부 로직을 재사용해야 함
        # 현재 evaluate_leading_risk_score가 인자없이 글로벌 변수 참조하는 형태라 조금 수정 필요
        
        # 임시 방편으로, JSA 위험도만 시뮬레이션하여 선행지표 점수 계산에 반영
        # 실제 모든 선행지표 입력값들은 그대로 두고 JSA 부분만 변화시켜야 정확함.
        # 기존 evaluate_leading_risk_score 함수의 로직을 복사하여 JSA_total_risk만 대체
        
        # JSA 부분 제외한 선행지표 점수를 먼저 계산
        non_jsa_leading_score_raw = 0
        non_jsa_leading_score_raw += (6 - env_cleanliness) * 2 + (6 - env_ventilation) * 2 + (6 - env_orderliness) * 2
        non_jsa_leading_score_raw += env_chemical_exposure * 3 + env_dust_level * 3
        non_jsa_leading_score_raw += (5 - worker_skill_options.index(worker_skill)) * 5 # worker_skill 반영
        non_jsa_leading_score_raw += (6 - worker_safety_compliance) * 4 + (6 - worker_ppe_compliance) * 4
        non_jsa_leading_score_raw += (6 - worker_fatigue_mgmt) * 2
        non_jsa_leading_score_raw += (5 - worker_safety_education_freq) * 2
        non_jsa_leading_score_raw += (6 - equip_condition) * 4 + (6 - equip_inspection_cycle) * 3
        if equip_breakdown_history == "3회 이상": non_jsa_leading_score_raw += 5
        elif equip_breakdown_history == "1~2회": non_jsa_leading_score_raw += 2
        non_jsa_leading_score_raw += (6 - equip_maintenance_quality) * 3
        if safety_inspection_status == "점검 미흡/미실시": non_jsa_leading_score_raw += 5
        elif safety_inspection_status == "샘플점검 위주": non_jsa_leading_score_raw += 3
        if fire_facility_adequacy == "설치 미흡/대상 아님": non_jsa_leading_score_raw += 4
        elif fire_facility_adequacy == "법적 기준 준수": non_jsa_leading_score_raw += 1
        if special_extinguisher_presence == "미보유": non_jsa_leading_score_raw += 5
        non_jsa_leading_score_raw += (6 - chemical_mgmt_msds) * 3 + (6 - chemical_mgmt_storage) * 4
        non_jsa_leading_score_raw += (6 - jsa_performance) * 3 + (6 - sops_compliance) * 2 + (6 - ptw_compliance) * 3

        simulated_leading_score_raw = simulated_total_jsa_risk + non_jsa_leading_score_raw # JSA 대체 후 합산

        simulated_leading_grade = get_risk_level(simulated_leading_score_raw)

        st.table(pd.DataFrame(simulated_jsa_details))
        st.write(f"감소 대책 적용 후 공정 내 예상 총 위험도: **{simulated_total_jsa_risk:.2f}점**")
        st.write(f"감소 대책 적용 후 **전사적 선행지표 예상 총점: {simulated_leading_score_raw:.2f}점**")
        st.write(f"감소 대책 적용 후 **전사적 선행지표 예상 등급: {simulated_leading_grade}**")

        fig_sim, ax_sim = plt.subplots()
        ax_sim.bar(["현재 총 선행 위험도", "감소 후 예상 선행 위험도"], [leading_score_raw, simulated_leading_score_raw], color=["salmon", "lightgreen"])
        ax_sim.set_ylim(0, max(leading_score_raw, simulated_leading_score_raw) + 20)
        ax_sim.set_ylabel("총 위험도 점수")
        ax_sim.set_title(f"'{selected_process_step}' 공정 포함 전체 선행지표 위험도 변화 시뮬레이션")
        for bar in ax_sim.patches:
            yval = bar.get_height()
            ax_sim.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.2f}", ha='center', va='bottom')
        st.pyplot(fig_sim)


# --- 9. 후행지표 기반 선행지표 보완 루틴 ---
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