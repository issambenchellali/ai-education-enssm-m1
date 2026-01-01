import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import openai
from collections import Counter
from openai import OpenAI
# ---------------------------
# تحميل المتغيرات السرية
# ---------------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# ---------------------------
# إنشاء عميل Supabase
# ---------------------------
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------
# إعداد الصفحة
# ---------------------------
st.set_page_config(
    page_title="منصة تعليمية ذكية",
    page_icon="📘",
    layout="wide"
)

# ---------------------------
# تسجيل الدخول
# ---------------------------
def authenticate(username, password):
    data = supabase.table("users").select("*").eq("username", username).execute()
    if data.data:
        user = data.data[0]
        if password == user["password"]:
            return user["role"]
    return None

# ---------------------------
# تسجيل النشاط
# ---------------------------
def log_activity(username, level, subject, lesson, activity_type):
    supabase.table("activity_log").insert({
        "username": username,
        "level": level,
        "subject": subject,
        "lesson": lesson,
        "activity_type": activity_type
    }).execute()

# ---------------------------
# اقتراح ذكي باستخدام Supabase
# ---------------------------
def suggest_activity(username):
    res = supabase.table("activity_log").select("*").eq("username", username).execute()
    activities = [(row["level"], row["subject"], row["lesson"]) for row in res.data]
    if not activities:
        return None
    most_common = Counter(activities).most_common(1)[0][0]
    return most_common

# ---------------------------
# اقتراح تمارين بواسطة AI
# 
#def generate_exercise(subject, lesson):
#    prompt = f"اصنع لي تمرين قصير للدرس '{lesson}' في مادة '{subject}' باللغة العربية."
#    response = openai.ChatCompletion.create(
#        model="gpt-4",
#        messages=[{"role": "user", "content": prompt}],
#       max_tokens=300
#    )
#    return response.choices[0].message.content
# ---------------------------

def generate_exercise(subject, lesson):
    prompt = f"""
أنشئ تمرينًا تعليميًا للطالب حول المادة التالية:

المادة: {subject}
الدرس: {lesson}

اجعل التمرين مناسبًا للتعليم الثانوي مع حل مختصر.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )

    return response.choices[0].message.content


client = OpenAI(api_key=os.getenv(OPENAI_API_KEY))

# =========================
# توليد تمرين بالذكاء الاصطناعي
# =========================
def generate_exercise(subject, lesson):

    prompt = f"""
أنشئ تمرينًا تعليميًا مناسبًا للتعليم الثانوي.

المادة: {subject}
الدرس: {lesson}

المطلوب:
- سؤال واحد على الأقل
- تمرين تطبيقي
- حل مختصر وواضح
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )

    return response.choices[0].message.content


exercise = exercise_response.choices[0].message.content

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
    activity_type = st.radio("نوع النشاط", ["شرح", "تمارين", "تطبيق"])

    if st.button("▶️ بدء النشاط"):
        st.success(f"📘 {activity_type} - {lesson}")
        log_activity(st.session_state.username, level, subject, lesson, activity_type)

        # اقتراح تمارين فعلية بواسطة AI
        if activity_type != "شرح":
            exercise = generate_exercise(subject, lesson)
            st.markdown(f"### 🤖 التمرين المقترح:\n{exercise}")

    # ---------------------------
    # الاقتراح الذكي
    # ---------------------------
    st.divider()
    st.subheader("🤖 اقتراح ذكي")
    suggestion = suggest_activity(st.session_state.username)
    if suggestion:
        st.info(f"📌 نقترح متابعة:\nالطور: {suggestion[0]}\nالمادة: {suggestion[1]}\nالحصة: {suggestion[2]}")
    else:
        st.warning("لا توجد بيانات كافية للاقتراح بعد.")

    # ---------------------------
    # لوحة حسب الدور
    # ---------------------------
    st.divider()
    if st.session_state.role == "admin":
        st.header("🧑‍💼 لوحة الإداري")
        st.write("📊 إحصائيات المستخدمين والأنشطة")
        data = supabase.table("activity_log").select("*").execute()
        df = pd.DataFrame(data.data)
        st.dataframe(df)
        st.bar_chart(df.groupby("subject").size())

    elif st.session_state.role == "teacher":
        st.header("👨‍🏫 لوحة الأستاذ")
        st.write("إضافة تمارين جديدة")
        new_lesson = st.text_input("درس جديد")
        file = st.file_uploader("رفع ملف الدرس (PDF/صورة/نص)", type=["pdf", "png", "jpg", "txt"])
        if st.button("💾 إضافة درس"):
            if new_lesson and file:
                file_content = file.read()
                supabase.storage.from_("lessons").upload(f"{new_lesson}_{file.name}", file_content)
                st.success("✅ تم إضافة الدرس بنجاح")

    elif st.session_state.role == "student":
        st.header("👨‍🎓 لوحة الطالب")
        st.write("التعلم والتفاعل مع المحتوى")




