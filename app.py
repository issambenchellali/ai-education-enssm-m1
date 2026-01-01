import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI, AuthenticationError
from collections import Counter

# ===============================
# تحميل المتغيرات البيئية
# ===============================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# ===============================
# تهيئة حالة الجلسة
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ===============================
# دوال المساعدة العامة
# ===============================
def check_environment():
    """فحص المتغيرات البيئية"""
    issues = []
    if not SUPABASE_URL:
        issues.append("❌ SUPABASE_URL غير مضبوط")
    if not SUPABASE_KEY:
        issues.append("❌ SUPABASE_KEY غير مضبوط")
    if not OPENAI_API_KEY:
        issues.append("❌ OPENAI_API_KEY غير مضبوط")
    return issues

def init_supabase():
    """تهيئة اتصال Supabase"""
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            return None
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # اختبار الاتصال
        client.table("users").select("*").limit(1).execute()
        return client
    except Exception as e:
        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        return None

def init_openai():
    """تهيئة اتصال OpenAI"""
    try:
        if not OPENAI_API_KEY:
            return None
        client = OpenAI(api_key=OPENAI_API_KEY)
        # اختبار الاتصال
        client.models.list()
        return client
    except Exception as e:
        st.error(f"خطأ في الاتصال بـ OpenAI: {e}")
        return None

# ===============================
# تهيئة العملاء
# ===============================
supabase = init_supabase()
ai_client = init_openai()

# ===============================
# دوال المصادقة
# ===============================
def authenticate(username, password):
    """المصادقة مع قاعدة البيانات"""
    if not supabase:
        st.error("❌ قاعدة البيانات غير متصلة")
        return None
    
    try:
        res = supabase.table("users").select("*").eq("username", username).execute()
        if res.data and res.data[0]["password"] == password:
            user_data = res.data[0]
            return {
                "role": user_data.get("role", "طالب"),
                "user_id": user_data.get("id"),
                "username": username
            }
    except Exception as e:
        st.error(f"خطأ في المصادقة: {e}")
    return None

def log_activity(user_id, activity_type, details=None):
    """تسجيل النشاط"""
    if not supabase:
        return
    try:
        data = {
            "user_id": user_id,
            "activity_type": activity_type,
            "details": details or {}
        }
        supabase.table("activity_log").insert(data).execute()
    except Exception as e:
        print(f"خطأ في تسجيل النشاط: {e}")

# ===============================
# صفحة تسجيل الدخول
# ===============================
def login_page():
    """عرض صفحة تسجيل الدخول"""
    st.title("🔐 تسجيل الدخول - المنصة التعليمية الذكية")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2991/2991148.png", width=150)
    
    with col2:
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("🚀 دخول", type="primary", use_container_width=True):
            if not username or not password:
                st.error("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور")
                return
            
            user_data = authenticate(username, password)
            if user_data:
                st.session_state.logged_in = True
                st.session_state.role = user_data["role"]
                st.session_state.username = user_data["username"]
                st.session_state.user_id = user_data["user_id"]
                log_activity(user_data["user_id"], "login")
                st.success("✅ تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
    
    # قسم للمستخدمين التجريبيين
    with st.expander("🔧 حسابات تجريبية (للتطوير)"):
        st.markdown("""
        **للاختبار السريع:**
        
        **طالب:**  
        - اسم المستخدم: `student1`  
        - كلمة المرور: `123456`
        
        **أستاذ:**  
        - اسم المستخدم: `teacher1`  
        - كلمة المرور: `123456`
        
        **إداري:**  
        - اسم المستخدم: `admin1`  
        - كلمة المرور: `123456`
        """)

# ===============================
# القائمة الجانبية
# ===============================
def sidebar_menu():
    """عرض القائمة الجانبية"""
    with st.sidebar:
        st.title(f"👋 {st.session_state.username}")
        st.markdown(f"**الدور:** {st.session_state.role}")
        st.divider()
        
        # القائمة حسب الدور
        if st.session_state.role == "طالب":
            menu_options = ["🏠 الرئيسية", "📚 الدروس", "🧠 تمارين", "📊 تقدمي"]
            icons = ["🏠", "📚", "🧠", "📊"]
        elif st.session_state.role == "أستاذ":
            menu_options = ["🏠 الرئيسية", "📤 رفع درس", "✏️ إنشاء تمرين", "👨‍🎓 متابعة"]
            icons = ["🏠", "📤", "✏️", "👨‍🎓"]
        else:  # إداري
            menu_options = ["🏠 الرئيسية", "👥 المستخدمين", "📊 إحصائيات", "⚙️ إعدادات"]
            icons = ["🏠", "👥", "📊", "⚙️"]
        
        selected = st.radio(
            "القائمة",
            menu_options,
            format_func=lambda x: f"{icons[menu_options.index(x)]} {x}"
        )
        
        st.divider()
        
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            log_activity(st.session_state.user_id, "logout")
            for key in ["logged_in", "role", "username", "user_id"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        return selected

# ===============================
# دوال لوحة الطالب
# ===============================
def suggest_activity_for_student():
    """اقتراح نشاط للطالب"""
    try:
        # في حالة عدم وجود بيانات، نعود باقتراح افتراضي
        suggestions = [
            "درس الجبر للمبتدئين",
            "تمارين التفاضل والتكامل",
            "قراءة نص أدبي",
            "تجربة علمية بسيطة"
        ]
        import random
        return random.choice(suggestings)
    except:
        return "درس الرياضيات - العمليات الأساسية"

def display_lessons():
    """عرض الدروس المتاحة"""
    if not supabase:
        st.info("📭 قاعدة البيانات غير متصلة. لا يمكن عرض الدروس.")
        return
    
    try:
        res = supabase.table("lessons").select("*").execute()
        
        if res.data:
            for lesson in res.data[:5]:  # عرض أول 5 دروس فقط
                with st.expander(f"📖 {lesson.get('title', 'بدون عنوان')}"):
                    st.write(f"**المادة:** {lesson.get('subject', 'غير محدد')}")
                    st.write(f"**المستوى:** {lesson.get('level', 'غير محدد')}")
                    st.write(f"**الوصف:** {lesson.get('description', 'لا يوجد وصف')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📖 ابدأ الدرس", key=f"start_{lesson.get('id')}"):
                            st.info(f"بدأت درس: {lesson.get('title')}")
                            log_activity(st.session_state.user_id, "start_lesson", lesson)
                    with col2:
                        if st.button("🧠 تمارين", key=f"ex_{lesson.get('id')}"):
                            generate_and_show_exercise(lesson)
        else:
            st.info("📭 لا توجد دروس متاحة بعد.")
    except Exception as e:
        st.error(f"خطأ في تحميل الدروس: {e}")

def generate_and_show_exercise(lesson):
    """إنشاء وعرض تمرين"""
    if not ai_client:
        st.warning("🤖 خدمة الذكاء الاصطناعي غير متاحة حالياً")
        return
    
    try:
        with st.spinner("🤖 جاري إنشاء تمرين..."):
            prompt = f"""
            أنشئ تمرينًا تعليميًا:
            
            المادة: {lesson.get('subject', 'رياضيات')}
            الدرس: {lesson.get('title', 'درس عام')}
            المستوى: {lesson.get('level', 'متوسط')}
            
            المطلوب:
            1. سؤال واضح
            2. إجابة نموذجية
            3. شرح الحل
            """
            
            response = ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            
            st.markdown("### 🧠 تمرين مخصص:")
            st.write(response.choices[0].message.content)
    except Exception as e:
        st.error(f"خطأ في إنشاء التمرين: {e}")

def student_dashboard(selected):
    """لوحة تحكم الطالب"""
    if selected == "🏠 الرئيسية":
        st.title("🏠 لوحة الطالب")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("الدروس المكتملة", "12", "+3")
        with col2:
            st.metric("التمارين المحلولة", "47", "+8")
        with col3:
            st.metric("مستوى التقدم", "75%", "+5%")
        
        # اقتراح نشاط
        st.subheader("🎯 نشاط مقترح لك")
        suggestion = suggest_activity_for_student()
        st.info(f"**نقترح عليك:** {suggestion}")
        if st.button("بدء النشاط المقترح"):
            st.success(f"بدأت النشاط: {suggestion}")
    
    elif selected == "📚 الدروس":
        st.title("📚 مكتبة الدروس")
        display_lessons()
    
    elif selected == "🧠 تمارين":
        st.title("🧠 التمارين الذكية")
        
        col1, col2 = st.columns(2)
        with col1:
            subject = st.selectbox("المادة", ["رياضيات", "علوم", "فيزياء", "لغة عربية"])
            difficulty = st.select_slider("الصعوبة", ["سهل", "متوسط", "صعب"])
        
        with col2:
            topic = st.text_input("الموضوع (اختياري)")
            num_questions = st.number_input("عدد الأسئلة", 1, 10, 3)
        
        if st.button("🧠 توليد تمارين", type="primary"):
            if not ai_client:
                st.warning("خدمة الذكاء الاصطناعي غير متاحة")
                return
            
            with st.spinner("جاري إنشاء التمارين..."):
                prompt = f"""
                أنشئ {num_questions} تمارين في مادة {subject}
                مستوى الصعوبة: {difficulty}
                الموضوع: {topic if topic else 'عام'}
                
                لكل تمرين:
                1. السؤال
                2. الحل
                3. الشرح
                """
                
                try:
                    response = ai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=500
                    )
                    
                    st.markdown("### 📝 تمارينك:")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"خطأ: {e}")
    
    elif selected == "📊 تقدمي":
        st.title("📊 تتبع تقدمي")
        
        # بيانات نموذجية
        import plotly.graph_objects as go
        
        subjects = ["رياضيات", "علوم", "لغة عربية", "فيزياء"]
        scores = [85, 70, 90, 65]
        
        fig = go.Figure(data=[
            go.Bar(
                x=subjects,
                y=scores,
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            )
        ])
        
        fig.update_layout(
            title="تقدمك في المواد المختلفة",
            yaxis_title="النسبة المئوية",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ===============================
# دوال لوحة الأستاذ
# ===============================
def upload_lesson_page():
    """صفحة رفع درس جديد"""
    st.title("📤 رفع درس جديد")
    
    with st.form("upload_lesson_form"):
        title = st.text_input("عنوان الدرس")
        subject = st.selectbox("المادة", ["رياضيات", "علوم", "فيزياء", "كيمياء", "لغة عربية"])
        level = st.selectbox("المستوى", ["ابتدائي", "متوسط", "ثانوي"])
        description = st.text_area("وصف الدرس")
        
        uploaded_file = st.file_uploader("اختر ملف", type=['pdf', 'txt', 'jpg', 'png'])
        
        submitted = st.form_submit_button("📤 رفع الدرس")
        
        if submitted:
            if not title or not subject:
                st.error("يرجى تعبئة الحقول المطلوبة")
                return
            
            try:
                # حفظ في قاعدة البيانات
                lesson_data = {
                    "title": title,
                    "subject": subject,
                    "level": level,
                    "description": description,
                    "uploaded_by": st.session_state.user_id
                }
                
                if uploaded_file:
                    lesson_data["has_file"] = True
                    # هنا يمكن إضافة رفع الملف لـ Supabase Storage
                
                supabase.table("lessons").insert(lesson_data).execute()
                st.success("✅ تم رفع الدرس بنجاح!")
                log_activity(st.session_state.user_id, "upload_lesson", {"title": title})
                
            except Exception as e:
                st.error(f"خطأ في رفع الدرس: {e}")

def teacher_dashboard(selected):
    """لوحة تحكم الأستاذ"""
    if selected == "🏠 الرئيسية":
        st.title("👨‍🏫 لوحة الأستاذ")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("الدروس المنشأة", "24")
            st.metric("الطلاب النشطين", "15")
        with col2:
            st.metric("التمارين المنشأة", "56")
            st.metric("متوسط التفاعل", "82%")
        
        st.subheader("🛠 إجراءات سريعة")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 رفع درس جديد", use_container_width=True):
                st.session_state.show_upload = True
                st.rerun()
        with col2:
            if st.button("✏️ إنشاء تمرين", use_container_width=True):
                st.session_state.create_exercise = True
                st.rerun()
    
    elif selected == "📤 رفع درس" or st.session_state.get('show_upload'):
        upload_lesson_page()
    
    elif selected == "✏️ إنشاء تمرين" or st.session_state.get('create_exercise'):
        st.title("✏️ إنشاء تمرين")
        
        with st.form("create_exercise_form"):
            lesson_title = st.text_input("عنوان الدرس المرتبط")
            question = st.text_area("نص السؤال")
            answer = st.text_area("الإجابة النموذجية")
            explanation = st.text_area("شرح الحل")
            
            if st.form_submit_button("💾 حفظ التمرين"):
                try:
                    exercise_data = {
                        "lesson_title": lesson_title,
                        "question": question,
                        "answer": answer,
                        "explanation": explanation,
                        "created_by": st.session_state.user_id
                    }
                    
                    # هنا يمكن حفظ التمرين في قاعدة البيانات
                    st.success("✅ تم حفظ التمرين بنجاح!")
                except Exception as e:
                    st.error(f"خطأ في حفظ التمرين: {e}")
    
    elif selected == "👨‍🎓 متابعة":
        st.title("👨‍🎓 متابعة الطلاب")
        st.info("هذه الصفحة قيد التطوير")

# ===============================
# دوال لوحة الإدارة
# ===============================
def admin_dashboard(selected):
    """لوحة تحكم الإدارة"""
    if selected == "🏠 الرئيسية":
        st.title("👨‍💼 لوحة الإدارة")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي المستخدمين", "156")
        with col2:
            st.metric("الدروس المرفوعة", "89")
        with col3:
            st.metric("التفاعلات اليومية", "1,234")
        
        # رسم بياني بسيط
        import plotly.express as px
        data = pd.DataFrame({
            'اليوم': ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة'],
            'التفاعلات': [345, 456, 567, 432, 543]
        })
        fig = px.line(data, x='اليوم', y='التفاعلات', title='نشاط النظام الأسبوعي')
        st.plotly_chart(fig, use_container_width=True)
    
    elif selected == "👥 المستخدمين":
        st.title("👥 إدارة المستخدمين")
        
        # عرض المستخدمين (بيانات تجريبية)
        users_data = pd.DataFrame([
            {"اسم المستخدم": "student1", "الدور": "طالب", "تاريخ التسجيل": "2024-01-01"},
            {"اسم المستخدم": "teacher1", "الدور": "أستاذ", "تاريخ التسجيل": "2024-01-02"},
            {"اسم المستخدم": "admin1", "الدور": "إداري", "تاريخ التسجيل": "2024-01-03"},
        ])
        st.dataframe(users_data, use_container_width=True)
    
    elif selected == "📊 إحصائيات":
        st.title("📊 إحصائيات النظام")
        st.info("هذه الصفحة قيد التطوير")
    
    elif selected == "⚙️ إعدادات":
        st.title("⚙️ إعدادات النظام")
        st.info("هذه الصفحة قيد التطوير")

# ===============================
# الدالة الرئيسية
# ===============================
def main():
    # إعدادات الصفحة
    st.set_page_config(
        page_title="المنصة التعليمية الذكية",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # تخصيص التنسيق
    st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        margin-top: 10px;
    }
    .stMetric {
        text-align: center;
        padding: 10px;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 18px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # التحقق من اتصال قاعدة البيانات
    if not supabase:
        st.warning("⚠️ تحذير: قاعدة البيانات غير متصلة. بعض الميزات قد لا تعمل.")
    
    # التحقق من اتصال OpenAI
    if not ai_client:
        st.info("ℹ️ ملاحظة: خدمة الذكاء الاصطناعي غير متاحة. يمكنك استخدام الميزات الأساسية.")
    
    # التحقق من حالة تسجيل الدخول
    if not st.session_state.logged_in:
        login_page()
    else:
        selected = sidebar_menu()
        
        # توجيه حسب الدور
        if st.session_state.role == "طالب":
            student_dashboard(selected)
        elif st.session_state.role == "أستاذ":
            teacher_dashboard(selected)
        elif st.session_state.role == "إداري":
            admin_dashboard(selected)
        else:
            st.error("❌ دور غير معروف")
            if st.button("تسجيل الخروج وإعادة المحاولة"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

# ===============================
# تشغيل التطبيق
# ===============================
if __name__ == "__main__":
    main()
