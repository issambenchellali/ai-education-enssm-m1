import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from collections import Counter
from openai import OpenAI

# ===============================
# تحميل المتغيرات السرية
# ===============================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("❌ مفتاح OpenAI غير مضبوط")
    st.stop()
st.write("OPENAI_API_KEY loaded:", bool(OPENAI_API_KEY))
# ===============================
# إنشاء العملاء
# ===============================
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
ai_client = OpenAI(api_key=OPENAI_API_KEY)

# ===============================
# إعداد الصفحة
# ===============================
st.set_page_config(
    page_title="منصة تعليمية ذكية",
    page_icon="📘",
    layout="wide"
)

# ===============================
# دوال أساسية
# ===============================
def authenticate(username, password):
    res = supabase.table("users").select("*").eq("username", username).execute()
    if res.data and res.data[0]["password"] == password:
        return res.data[0]["role"]
    return None


def log_activity(username, level, subject, lesson, activity_type):
    supabase.table("activity_log").insert({
        "username": username,
        "level": level,
        "subject": subject,
        "lesson": lesson,
        "activity_type": activity_type
    }).execute()


def suggest_activity(username):
    res = supabase.table("activity_log").select("*").eq("username", username).execute()
    if not res.data:
        return None
    activities = [(r["level"], r["subject"], r["lesson"]) for r in res.data]
    return Counter(activities).most_common(1)[0][0]


def generate_exercise(subject, lesson, level):
    prompt = f"""
أنت أستاذ محترف.
أنشئ تمرينًا تعليميًا حقيقيًا.

الطور: {level}
المادة: {subject}
الدرس: {lesson}

المطلوب:
1️⃣ سؤال مباشر
2️⃣ تمرين تطبيقي
3️⃣ حل نموذجي واضح
"""

    response = ai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )

    return response.choices[0].message.content


def explain_lesson(subject, lesson):
    prompt = f"""
اشرح درس "{lesson}" في مادة "{subject}"
بأسلوب بسيط، تدريجي، ومفهوم للطالب.
"""

    response = ai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    return response.choices[0].message.content


# ===============================
# تهيئة الجلسة
# ===============================
if "role" not in st.session_state:
    st.session_state.role = None
    st.session_state.username = None

# ===============================
# تسجيل الدخول
# ===============================
if not st.session_state.role:
    st.title("🔐 تسجيل الدخول")

    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        role = authenticate(u, p)
        if role:
            st.session_state.role = role
            st.session_state.username = u
            st.success("تم الدخول بنجاح")
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")

# ===============================
# بعد تسجيل الدخول
# ===============================
else:
    st.sidebar.success(f"{st.session_state.username} ({st.session_state.role})")

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.clear()
        st.rerun()

    page = st.sidebar.radio(
        "📂 الصفحات",
        ["📚 النشاط", "🤖 الذكاء الاصطناعي", "📊 الإدارة", "👨‍🏫 الأستاذ"]
    )

    # ===============================
    # صفحة النشاط
    # ===============================
    if page == "📚 النشاط":
        st.header("📚 النشاط التعليمي")

        level = st.selectbox("الطور", ["ابتدائي", "متوسط", "ثانوي"])
        subject = st.selectbox("المادة", ["رياضيات", "علوم", "فيزياء", "لغة عربية"])
        lesson = st.text_input("اسم الدرس")
        activity = st.radio("نوع النشاط", ["شرح", "تمارين", "تطبيق"])

        if st.button("بدء"):
            log_activity(st.session_state.username, level, subject, lesson, activity)

            if activity == "شرح":
                st.markdown(explain_lesson(subject, lesson))
            else:
                st.markdown(generate_exercise(subject, lesson, level))

    # ===============================
    # صفحة الذكاء الاصطناعي
    # ===============================
    elif page == "🤖 الذكاء الاصطناعي":
        st.header("🤖 قدرات الذكاء الاصطناعي")

        subject = st.selectbox("المادة", ["رياضيات", "علوم", "فيزياء", "لغة عربية"])
        lesson = st.text_input("الدرس")



