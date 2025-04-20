
import streamlit as st
import math

interventions = [
    {"name": "Smoking cessation", "arr_lifetime": 17, "arr_5yr": 5},
    {"name": "Antiplatelet (ASA or clopidogrel)", "arr_lifetime": 6, "arr_5yr": 2},
    {"name": "BP control (ACEi/ARB ± CCB)", "arr_lifetime": 12, "arr_5yr": 4},
    {"name": "Semaglutide 2.4 mg", "arr_lifetime": 4, "arr_5yr": 1},
    {"name": "Weight loss to ideal BMI", "arr_lifetime": 10, "arr_5yr": 3},
    {"name": "Empagliflozin", "arr_lifetime": 6, "arr_5yr": 2},
    {"name": "Icosapent ethyl (TG ≥1.5)", "arr_lifetime": 5, "arr_5yr": 2},
    {"name": "Mediterranean diet", "arr_lifetime": 9, "arr_5yr": 3},
    {"name": "Physical activity", "arr_lifetime": 9, "arr_5yr": 3},
    {"name": "Alcohol moderation", "arr_lifetime": 5, "arr_5yr": 2},
    {"name": "Stress reduction", "arr_lifetime": 3, "arr_5yr": 1}
]

ldl_therapies = {
    "None": 0,
    "Atorvastatin 20 mg": 40,
    "Atorvastatin 80 mg": 50,
    "Rosuvastatin 10 mg": 40,
    "Rosuvastatin 20–40 mg": 55,
    "Simvastatin 40 mg": 35,
    "Ezetimibe alone": 20,
    "PCSK9 inhibitor": 60
}

def estimate_smart_risk(age, sex, sbp, total_chol, hdl, smoker, diabetes, egfr, crp, vasc_count):
    sex_val = 1 if sex == "Male" else 0
    smoking_val = 1 if smoker else 0
    diabetes_val = 1 if diabetes else 0
    crp_log = math.log(crp + 1) if crp else 0

    lp = (0.064*age + 0.34*sex_val + 0.02*sbp + 0.25*total_chol -
          0.25*hdl + 0.44*smoking_val + 0.51*diabetes_val -
          0.2*(egfr/10) + 0.25*crp_log + 0.4*vasc_count)

    risk = 1 - 0.900**math.exp(lp - 5.8)
    return round(risk * 100, 1)

st.title("Comprehensive SMART CVD Risk Reduction Calculator")

age = st.slider("Age", 30, 90, 60)
sex = st.radio("Sex", ["Male", "Female"])
smoker = st.checkbox("Currently smoking")
diabetes = st.checkbox("Diabetes")
egfr = st.slider("eGFR", 15, 120, 80)
total_chol = st.number_input("Total Cholesterol (mmol/L)", 2.0, 10.0, 5.0, 0.1)
hdl = st.number_input("HDL-C (mmol/L)", 0.5, 3.0, 1.0, 0.1)
crp = st.number_input("hs-CRP (mg/L) [Not acute]", 0.1, 20.0, 2.0, 0.1)
if crp > 10:
    st.warning("hs-CRP >10 mg/L suggests acute inflammation. Avoid using acute-phase values.")

st.markdown("### Vascular Disease")
vasc_count = sum([st.checkbox(label) for label in ["Coronary artery disease", "Cerebrovascular disease", "Peripheral artery disease"]])

sbp_current = st.number_input("Current SBP (mmHg)", 80, 220, 145)
sbp_target = st.number_input("Target SBP (mmHg)", 80, 220, 120)

baseline_ldl = st.number_input("Baseline LDL-C (mmol/L)", 0.5, 6.0, 3.5, 0.1)
on_therapy = st.selectbox("Already on lipid-lowering therapy?", ["None"] + list(ldl_therapies.keys())[1:])
therapy_ldl_reduction = ldl_therapies[on_therapy]
adjusted_ldl = baseline_ldl * (1 - therapy_ldl_reduction / 100)

additional_therapy = st.multiselect("Add or intensify therapy", [t for t in ldl_therapies if t != "None" and t != on_therapy])
additional_ldl_reduction = sum([ldl_therapies[t]/2 for t in additional_therapy])
final_ldl = adjusted_ldl * (1 - additional_ldl_reduction / 100)

baseline_risk = estimate_smart_risk(age, sex, sbp_current, total_chol, hdl, smoker, diabetes, egfr, crp, vasc_count)

selected_interventions = [st.checkbox(i["name"]) for i in interventions]
total_rrr = sum([i["arr_lifetime"] for idx, i in enumerate(interventions) if selected_interventions[idx]])
total_rrr += min((baseline_ldl - final_ldl)*22, 35)
total_rrr += min(20 * (sbp_current - sbp_target)/10, 30)
total_rrr = min(total_rrr, 70)

final_risk = round(baseline_risk * (1 - total_rrr / 100), 1)

if st.button("Calculate"):
    st.success(f"Baseline SMART 10-year risk: {baseline_risk}%")
    st.info(f"LDL-C after adjustments: {final_ldl:.2f} mmol/L (initial: {baseline_ldl:.2f})")
    st.success(f"Estimated Cumulative RRR: {total_rrr}%")
    st.success(f"Final CVD Risk: {final_risk}%")
