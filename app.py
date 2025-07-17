import streamlit as st
import pandas as pd
import math
from io import BytesIO
from step1_senarios import generate_step1_scenarios
from step2 import step2_katanomi_zoiroi
from step3 import step3_katanomi_idiaiterotites
from step4 import step4_katanomi_filia
from step5 import step5_omadopoihsh_katigories, step5_katanomi_omadon_se_tmimata
from step6 import step6_ypolipoi_xwris_filies
from step7 import step7_final_check_and_fix

from io import BytesIO

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Κατανομή")
    output.seek(0)
    return output

# ➤ Αποδοχή Όρων Πνευματικών Δικαιωμάτων
st.sidebar.title("🛡️ Όροι Χρήσης & Πνευματικά Δικαιώματα")
with st.sidebar.expander("📃 Προβολή Όρων"):
    st.markdown("""
    **© 2025 Παναγιώτα Γιαννίτσαρου – Όλα τα δικαιώματα διατηρούνται.**

    Η χρήση της παρούσας εφαρμογής προϋποθέτει την αποδοχή των εξής όρων:

    - Απαγορεύεται η αντιγραφή, τροποποίηση ή διανομή του λογισμικού χωρίς έγγραφη άδεια της δημιουργού.
    - Η εφαρμογή προστατεύεται από τη νομοθεσία περί πνευματικής ιδιοκτησίας.
    - Οποιαδήποτε μη εξουσιοδοτημένη χρήση διώκεται νομικά.
    """)

accepted = st.sidebar.checkbox("✅ Αποδέχομαι τους παραπάνω όρους")

if not accepted:
    st.warning("Για να συνεχίσετε, πρέπει να αποδεχτείτε τους όρους χρήσης.")
    st.stop()

# ➤ Κλείδωμα με Κωδικό (εμφανίζεται μόνο αν αποδεχτεί)
password = st.sidebar.text_input("🔐 Εισάγετε τον κωδικό πρόσβασης:", type="password")
if password != "katanomi2025":
    st.warning("Παρακαλώ εισάγετε έγκυρο κωδικό για πρόσβαση στην εφαρμογή.")
    st.stop()

# ➤ Ενεργοποίηση/Απενεργοποίηση Εφαρμογής
enable_app = st.sidebar.checkbox("✅ Ενεργοποίηση Εφαρμογής", value=True)
if not enable_app:
    st.info("🔒 Η εφαρμογή είναι προσωρινά απενεργοποιημένη.")
    st.stop()



st.title("🎯 Ψηφιακή Κατανομή Μαθητών Α΄ Δημοτικού")

# ➤ Αρχικοποίηση μεταβλητών
if "scenario_index" not in st.session_state:
    st.session_state["scenario_index"] = 0
if "scenario_dfs" not in st.session_state:
    st.session_state["scenario_dfs"] = None

# ➤ Εισαγωγή Αρχείου Excel
uploaded_file = st.file_uploader("📥 Εισαγωγή Αρχείου Excel Μαθητών", type=["xlsx"])
if uploaded_file:
    df_initial = pd.read_excel(uploaded_file)
    st.success("✅ Το αρχείο ανέβηκε επιτυχώς!")
    num_classes = math.ceil(len(df_initial) / 25)

    # Δημιουργία σεναρίων Βήματος 1
    scenarios = generate_step1_scenarios(df_initial, num_classes)
    st.session_state["scenario_dfs"] = scenarios
    scenario_index = st.session_state["scenario_index"]
    df = scenarios[scenario_index]

    df["ΚΛΕΙΔΩΜΕΝΟΣ"] = False

    with st.spinner("▶️ Βήμα 2: Ζωηροί Μαθητές..."):
        df = step2_katanomi_zoiroi(df, num_classes)
    with st.spinner("▶️ Βήμα 3: Παιδιά με Ιδιαιτερότητες..."):
        df = step3_katanomi_idiaiterotites(df, num_classes)
    with st.spinner("▶️ Βήμα 4: Αμοιβαίες Φιλίες..."):
        df = step4_katanomi_filia(df)
    with st.spinner("▶️ Βήμα 5: Ομαδοποίηση & Κατηγοριοποίηση..."):
        categories, _ = step5_omadopoihsh_katigories(df)
        df = step5_katanomi_omadon_se_tmimata(df, categories, num_classes)
    with st.spinner("▶️ Βήμα 6: Υπόλοιποι Μαθητές Χωρίς Φιλίες..."):
        df = step6_ypolipoi_xwris_filies(df, num_classes)
    with st.spinner("▶️ Βήμα 7: Έλεγχος & Διορθώσεις..."):
        df, warnings, success = step7_final_check_and_fix(df, num_classes)
        if not success:
            st.error("⛔ Η κατανομή δεν ήταν επιτυχής λόγω πληθυσμιακών περιορισμών.")
            st.stop()

    df["ΤΜΗΜΑ"] = df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
    st.success(f"✅ Ολοκληρώθηκε η κατανομή για το Σενάριο {scenario_index + 1} από {len(scenarios)}.")

    st.subheader("🔍 Προεπισκόπηση Τελικής Κατανομής")
    st.dataframe(df)

    if warnings:
        st.warning("⚠️ Προειδοποιήσεις Κατανομής:")
        for w in warnings:
            st.text(w)

    st.subheader("📊 Πίνακας Στατιστικών Ανά Τμήμα")
    summary = []
    for i in range(num_classes):
        class_id = f'Τμήμα {i+1}'
        class_df = df[df["ΤΜΗΜΑ"] == class_id]
        total = class_df.shape[0]
        stats = {
            "ΤΜΗΜΑ": class_id,
            "ΑΓΟΡΙΑ": (class_df["ΦΥΛΟ"] == "Α").sum(),
            "ΚΟΡΙΤΣΙΑ": (class_df["ΦΥΛΟ"] == "Κ").sum(),
            "ΠΑΙΔΙΑ_ΕΚΠΑΙΔΕΥΤΙΚΩΝ": (class_df["ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν").sum(),
            "ΖΩΗΡΟΙ": (class_df["ΖΩΗΡΟΣ"] == "Ν").sum(),
            "ΙΔΙΑΙΤΕΡΟΤΗΤΕΣ": (class_df["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν").sum(),
            "ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ": (class_df["ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ"] == "Ν").sum(),
            "ΣΥΝΟΛΟ Τμήματος": total
        }
        summary.append(stats)

    stats_df = pd.DataFrame(summary)
    st.dataframe(stats_df)

st.markdown("---")
st.subheader("📥 Λήψη Τελικής Κατανομής")
excel_file = convert_df_to_excel(df)
st.download_button(
    label="💾 Κατέβασε Excel με την Κατανομή",
    data=excel_file,
    file_name="teliki_katanomi.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

    # Κουμπί: Επόμενο Σενάριο

    if len(scenarios) > 1 and scenario_index < len(scenarios) - 1:
        st.markdown("---")
        st.info(f"📌 Υπάρχουν {len(scenarios)} εναλλακτικά σενάρια για την κατανομή παιδιών εκπαιδευτικών.")
        if st.button("🔄 Επόμενο Σενάριο"):
            st.session_state["scenario_index"] += 1
            st.experimental_rerun()


# ============================================================
# 🔄 Εναλλαγή Εναλλακτικών Σεναρίων για Παιδιά Εκπαιδευτικών
# Τοποθετείται ΜΕΤΑ την εμφάνιση στατιστικών και προειδοποιήσεων
# Εκτελεί νέο σενάριο Βήματος 1 και ξανατρέχει όλα τα βήματα
# ============================================================

col1, col2 = st.columns(2)

with col1:
    if scenario_index > 0:
        if st.button("⬅️ Προηγούμενο Σενάριο"):
            st.session_state["scenario_index"] -= 1
            st.experimental_rerun()

with col2:
    if scenario_index < len(scenario_dfs) - 1:
        if st.button("🔄 Επόμενο Σενάριο"):
            st.session_state["scenario_index"] += 1
            st.experimental_rerun()

st.markdown("---")
st.info(f"📌 Βλέπετε το Σενάριο {scenario_index + 1} από {len(scenario_dfs)}")





if not uploaded_file:
    st.markdown(
        """
        <style>
        .custom-footer {
            position: fixed;
            bottom: 38px;
            right: 38px;
            text-align: right;
            animation: fadeIn 2s ease-in;
            z-index: 100;
        }
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        .custom-footer img {
            width: 200px;
        }
        </style>

        <div class='custom-footer'>
            <img src='cab3f5bd-f8cd-4b38-a01b-f9b129797feb.png'>
        </div>
        """,
        unsafe_allow_html=True
    )
