import streamlit as st
import os
import sys
from dotenv import load_dotenv

# ===============================
# التحقق من البيئة أولاً
# ===============================
def check_imports():
    """التحقق من تثبيت المكتبات"""
    required_packages = ['supabase', 'openai', 'pandas', 'plotly']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

# ===============================
# عرض رسالة توجيهية إذا كانت المكتبات مفقودة
# ===============================
missing_packages = check_imports()
if missing_packages:
    st.error(f"❌ المكتبات التالية غير مثبتة: {', '.join(missing_packages)}")
    st.info("""
    **لحل هذه المشكلة على Streamlit Cloud:**
    1. تأكد من وجود `requirements.txt` في المستودع
    2. تحقق من صيغة `requirements.txt`
    3. انتظر إعادة بناء التطبيق
    """)
    st.stop()

# الآن يمكن استيراد المكتبات بأمان
try:
    from supabase import create_client
    from openai import OpenAI
    import pandas as pd
    import plotly.graph_objects as go
except Exception as e:
    st.error(f"خطأ في استيراد المكتبات: {e}")
    st.stop()

# ===============================
# تهيئة المتغيرات البيئية
# ===============================
load_dotenv()

# الحصول على المفاتيح من Streamlit Secrets أو من .env
def get_secrets():
    """الحصول على الإعدادات من Streamlit Secrets أو المتغيرات البيئية"""
    secrets = {}
    
    # محاولة الحصول من Streamlit Secrets (في السحابة)
    try:
        if hasattr(st, 'secrets'):
            secrets['SUPABASE_URL'] = st.secrets.get('SUPABASE_URL', '')
            secrets['SUPABASE_KEY'] = st.secrets.get('SUPABASE_KEY', '')
            secrets['OPENAI_API_KEY'] = st.secrets.get('OPENAI_API_KEY', '')
    except:
        pass
    
    # إذا لم تكن موجودة في Secrets، جرب .env
    if not secrets.get('SUPABASE_URL'):
        secrets['SUPABASE_URL'] = os.getenv('SUPABASE_URL', '')
    if not secrets.get('SUPABASE_KEY'):
        secrets['SUPABASE_KEY'] = os.getenv('SUPABASE_KEY', '')
    if not secrets.get('OPENAI_API_KEY'):
        secrets['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
    
    return secrets

secrets = get_secrets()

SUPABASE_URL = secrets['SUPABASE_URL']
SUPABASE_KEY = secrets['SUPABASE_KEY']
OPENAI_API_KEY = secrets['OPENAI_API_KEY']

# ===============================
# تهيئة حالة الجلسة
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.user_id = None

# ===============================
# دوال المصادقة (بدون قاعدة بيانات أولاً للاختبار)
# ===============================
def authenticate_simple(username, password):
    """مصادقة مبسطة للاختبار"""
    test_users = {
        'student1': {'password': '123456', 'role': 'طالب'},
        'teacher1': {'password': '123456', 'role': 'أستاذ'},
        'admin1': {'password': '123456', 'role': 'إداري'}
    }
    
    if username in test_users and test_users[username]['password'] == password:
        return {
            'role': test_users[username]['role'],
            'user_id': username,
            'username': username
        }
    return None

# ===============================
# صفحة تسجيل الدخول المبسطة
# ===============================
def login_page():
    st.title("🎓 المنصة التعليمية الذكية")
    st.markdown("### 🔐 تسجيل الدخول")
    
    col1, col2 = st.columns(2)
    
    with col1:
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("🚀 دخول", type="primary", use_container_width=True):
            if not username or not password:
                st.error("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور")
                return
            
            user_data = authenticate_simple(username, password)
            if user_data:
                st.session_state.logged_in = True
                st.session_state.role = user_data["role"]
                st.session_state.username = user_data["username"]
                st.session_state.user_id = user_data["user_id"]
                st.success("✅ تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
    
    with col2:
        st.info("""
        **📋 حسابات تجريبية:**
        
        **👨‍🎓 طالب:**
        - المستخدم: `student1`
        - كلمة المرور: `123456`
        
        **👨‍🏫 أستاذ:**
        - المستخدم: `teacher1`
        - كلمة المرور: `123456`
        
        **👨‍💼 إداري:**
        - المستخدم: `admin1`
        - كلمة المرور: `123456`
        """)
    
    # عرض حالة الاتصالات
    with st.expander("🔧 حالة النظام"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Python", sys.version.split()[0])
        with col2:
            st.metric("Streamlit", st.__version__)
        with col3:
            if SUPABASE_URL:
                st.success("Supabase ✓")
            else:
                st.warning("Supabase ✗")
        
        if OPENAI_API_KEY:
            st.success("OpenAI API ✓")
        else:
            st.warning("OpenAI API ✗")

# ===============================
# القائمة الجانبية
# ===============================
def sidebar_menu():
    with st.sidebar:
        st.title(f"👋 {st.session_state.username}")
        st.markdown(f"**الدور:** {st.session_state.role}")
        st.divider()
        
        # القائمة حسب الدور
        if st.session_state.role == "طالب":
            pages = ["🏠 الرئيسية", "📚 الدروس", "🧠 التمارين", "📊 تقدمي"]
        elif st.session_state.role == "أستاذ":
            pages = ["🏠 الرئيسية", "📤 رفع درس", "✏️ إنشاء تمرين", "👨‍🎓 متابعة"]
        else:
            pages = ["🏠 الرئيسية", "👥 المستخدمين", "📊 إحصائيات", "⚙️ إعدادات"]
        
        selected = st.radio("القائمة", pages, label_visibility="collapsed")
        st.divider()
        
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        return selected

# ===============================
# الصفحات الرئيسية
# ===============================
def student_home():
    st.title("🏠 لوحة الطالب")
    
    st.markdown("### 📚 مرحباً بك في المنصة التعليمية الذكية")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("الدروس المتاحة", "12")
    with col2:
        st.metric("التمارين المحلولة", "47")
    with col3:
        st.metric("مستوى التقدم", "75%")
    
    st.markdown("---")
    
    # دروس موصى بها
    st.subheader("🎯 دروس موصى بها لك")
    lessons = [
        {"title": "مقدمة في الجبر", "subject": "رياضيات", "level": "متوسط"},
        {"title": "قوانين نيوتن", "subject": "فيزياء", "level": "ثانوي"},
        {"title": "اللغة العربية", "subject": "لغة عربية", "level": "ابتدائي"}
    ]
    
    for lesson in lessons:
        with st.expander(f"📖 {lesson['title']}"):
            st.write(f"**المادة:** {lesson['subject']}")
            st.write(f"**المستوى:** {lesson['level']}")
            if st.button("بدء الدرس", key=f"start_{lesson['title']}"):
                st.success(f"بدأت درس {lesson['title']}")

def student_lessons():
    st.title("📚 مكتبة الدروس")
    st.info("هذه الصفحة تعرض الدروس المتاحة. تحتاج اتصالاً بقاعدة البيانات.")

def student_exercises():
    st.title("🧠 التمارين الذكية")
    
    if OPENAI_API_KEY:
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            subject = st.selectbox("المادة", ["رياضيات", "علوم", "لغة عربية"])
            topic = st.text_input("الموضوع (اختياري)")
            
            if st.button("إنشاء تمرين ذكي"):
                with st.spinner("🤖 جاري إنشاء تمرين..."):
                    prompt = f"أنشئ تمريناً في مادة {subject}"
                    if topic:
                        prompt += f" حول موضوع {topic}"
                    
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=300
                    )
                    
                    st.markdown("### 📝 التمرين:")
                    st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"خطأ في خدمة الذكاء الاصطناعي: {e}")
    else:
        st.warning("⚠️ خدمة الذكاء الاصطناعي غير متاحة")
        st.info("يمكنك تجربة التمارين التجريبية:")
        st.write("""
        1. ما نتيجة ٥ × ٧؟
        2. اذكر حالات المادة الثلاث
        3. اكتب جملة صحيحة إعرابياً
        """)

def student_progress():
    st.title("📊 تتبع تقدمي")
    
    # بيانات تجريبية
    import plotly.graph_objects as go
    
    fig = go.Figure(data=[
        go.Bar(
            x=['رياضيات', 'علوم', 'لغة عربية', 'فيزياء'],
            y=[85, 70, 90, 65],
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        )
    ])
    
    fig.update_layout(
        title="تقدمك في المواد",
        yaxis_title="النسبة المئوية",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ===============================
# الدالة الرئيسية
# ===============================
def main():
    # إعدادات الصفحة
    st.set_page_config(
        page_title="المنصة التعليمية الذكية",
        page_icon="🎓",
        layout="wide"
    )
    
    # تنسيق CSS
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # التحقق من تسجيل الدخول
    if not st.session_state.logged_in:
        login_page()
    else:
        selected = sidebar_menu()
        
        if st.session_state.role == "طالب":
            if selected == "🏠 الرئيسية":
                student_home()
            elif selected == "📚 الدروس":
                student_lessons()
            elif selected == "🧠 التمارين":
                student_exercises()
            elif selected == "📊 تقدمي":
                student_progress()
        else:
            st.title(f"👋 مرحباً {st.session_state.role}")
            st.info("لوحة التحكم قيد التطوير")

# ===============================
# تشغيل التطبيق
# ===============================
if __name__ == "__main__":
    main()
