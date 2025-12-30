import streamlit as st
import csv
import os
from collections import Counter

# ---------------------------
# إعداد الصفحة
# ---------------------------
st.set_page_config(
    page_title="منصة تعليمية ذكية",
    page_icon="📘",
    layout="wide"
)

# ---------------------------
# دالة تسجيل الدخول
# ---------------------------
def authenticate(username, password):
    with open("users.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (
                username.strip() == row["username"].strip()
                and password.strip() == row["password"].strip()
            ):
                return row["role"].strip()
    return None

# ---------------------------
# تسجيل التفاعل (التعلم الذكي)
# ---------------------------
def log_activity(username, level, subject, lesson, activity_type):
    with open("activity_log.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([username, level, subject, lesson, activity_type])

# ---------------------------
# اقتراح ذكي بناءً على الاستعمال
# ---------------------------
def suggest_activity(username):
    if not os.path.exists("activity_log.csv"):
        return None

    with open("activity_log.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        activities = [
            (row["level"], row["subject"], row["lesson"])
            for row in reader
            if row["username"] == username
        ]

    if not activities:
        return None

    most_common = Counter(activities).most_common(1)[0][0]
    return most_common

# ---------------------------
# تهيئة الجلسة
# ---------------------------
if "role" not in st.session_state:
    st.session_state.role = None
    st.session_state.username = None

# ---------------------------
# صفحة تسجيل الدخول
# ---------------------------
if not st.session_state.role:
    st.title("🔐 تسجيل الدخول")

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        role = authenticate(username, password)
        if role:
            st.session_state.role = role
            st.session_state.username = username
            st.success("✅ تم تسجيل الدخول بنجاح")
            st.rerun()
        else:
            st.error("❌ بيانات غير صحيحة")

# ---------------------------
# بعد تسجيل الدخول
# ---------------------------
else:
    st.sidebar.success(f"👤 {st.session_state.username} ({st.session_state.role})")

    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

    # ---------------------------
    # اختيار النشاط
    # ---------------------------
    st.header("📚 اختيار النشاط")

    level = st.selectbox("الطور", ["ابتدائي", "متوسط", "ثانوي"])
    subject = st.selectbox("المادة", ["رياضيات", "علوم", "فيزياء", "لغة عربية"])
    lesson = st.text_input("اسم الحصة")

    activity_type = st.radio(
        "نوع النشاط",
        ["شرح", "تمارين", "تطبيق"]
    )

    if st.button("▶️ بدء النشاط"):
        st.success(f"📘 {activity_type} - {lesson}")
        log_activity(
            st.session_state.username,
            level,
            subject,
            lesson,
            activity_type
        )

    # ---------------------------
    # الاقتراح الذكي
    # ---------------------------
    st.divider()
    st.subheader("🤖 اقتراح ذكي")

    suggestion = suggest_activity(st.session_state.username)
    if suggestion:
        st.info(
            f"📌 نقترح عليك متابعة:\n\n"
            f"الطور: {suggestion[0]}\n"
            f"المادة: {suggestion[1]}\n"
            f"الحصة: {suggestion[2]}"
        )
    else:
        st.warning("لا توجد بيانات كافية للاقتراح بعد.")

    # ---------------------------
    # لوحة حسب الدور
    # ---------------------------
    st.divider()

    if st.session_state.role == "admin":
        st.header("🧑‍💼 لوحة الإداري")
        st.write("إدارة المستخدمين والمنصة (قابل للتوسيع)")

    elif st.session_state.role == "teacher":
        st.header("👨‍🏫 لوحة الأستاذ")
        st.write("إضافة أنشطة ومتابعة التفاعل")

    elif st.session_state.role == "student":
        st.header("👨‍🎓 لوحة الطالب")
        st.write("التعلم والتفاعل مع المحتوى")
