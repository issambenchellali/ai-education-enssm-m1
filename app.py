import streamlit as st
import pandas as pd
import time

# ---------------------------------
# إعداد الصفحة
# ---------------------------------
st.set_page_config(
    page_title="منصة تعليمية ذكية",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------
# تحميل البيانات
# ---------------------------------
@st.cache_data
def load_activities():
    return pd.read_csv("activities.csv")

@st.cache_data
def load_users():
    return pd.read_csv("users.csv")

activities = load_activities()
users = load_users()

# ---------------------------------
# Session State
# ---------------------------------
if "logged" not in st.session_state:
    st.session_state.logged = False
    st.session_state.role = ""
    st.session_state.start_time = 0

# ---------------------------------
# تسجيل الدخول
# ---------------------------------
def login():
    st.title("🔐 تسجيل الدخول")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        user = users[(users.username == u) & (users.password == p)]
        if user.empty:
            st.error("بيانات غير صحيحة")
        else:
            st.session_state.logged = True
            st.session_state.role = user.iloc[0]["role"]
            st.rerun()

# ---------------------------------
# الذكاء الاصطناعي (حساب النقاط)
# ---------------------------------
def calculate_ai_score(row):
    return (
        row["avg_rating"] * 0.5
        + row["success_count"] * 0.3
        - row["usage_count"] * 0.2
    )

# ---------------------------------
# واجهة الطالب
# ---------------------------------
def student_view():
    st.header("👨‍🎓 الطالب")

    col1, col2, col3 = st.columns(3)

    with col1:
        level = st.selectbox("الطور", activities.level_stage.unique())
    with col2:
        subject = st.selectbox(
            "المادة",
            activities[activities.level_stage == level].subject.unique()
        )
    with col3:
        lesson = st.selectbox(
            "الحصة",
            activities[
                (activities.level_stage == level) &
                (activities.subject == subject)
            ].lesson.unique()
        )

    if st.button("🤖 اقترح نشاطًا ذكيًا"):
        subset = activities[
            (activities.level_stage == level) &
            (activities.subject == subject) &
            (activities.lesson == lesson)
        ].copy()

        subset["ai_score"] = subset.apply(calculate_ai_score, axis=1)
        activity = subset.sort_values("ai_score", ascending=False).iloc[0]

        st.session_state.start_time = time.time()

        st.markdown("## 📘 الشرح")
        st.write(activity.description)

        st.markdown("## ✏️ التمارين")
        st.write(activity.exercises)

        st.markdown("## 🧪 التطبيق")
        st.write(activity.application)

        rating = st.slider("⭐ قيّم النشاط", 1, 5, 3)

        if st.button("✅ أنهيت النشاط"):
            duration = int(time.time() - st.session_state.start_time)

            idx = activities.id == activity.id
            activities.loc[idx, "usage_count"] += 1
            activities.loc[idx, "success_count"] += 1
            activities.loc[idx, "total_rating"] += rating
            activities.loc[idx, "avg_rating"] = (
                activities.loc[idx, "total_rating"]
                / activities.loc[idx, "usage_count"]
            )

            activities.to_csv("activities.csv", index=False)
            st.success("تم حفظ تفاعلك – النظام يتعلم منك 🤖")

# ---------------------------------
# واجهة الأستاذ
# ---------------------------------
def teacher_view():
    st.header("👨‍🏫 الأستاذ")
    st.dataframe(activities)

# ---------------------------------
# واجهة الإداري
# ---------------------------------
def admin_view():
    st.header("🧑‍💼 الإداري")
    st.metric("عدد الأنشطة", len(activities))
    st.metric("عدد المستخدمين", len(users))

# ---------------------------------
# التطبيق الرئيسي
# ---------------------------------
if not st.session_state.logged:
    login()
else:
    with st.sidebar:
        st.write(f"الدور: **{st.session_state.role}**")
        if st.button("تسجيل الخروج"):
            st.session_state.logged = False
            st.rerun()

    if st.session_state.role == "student":
        student_view()
    elif st.session_state.role == "teacher":
        teacher_view()
    else:
        admin_view()
