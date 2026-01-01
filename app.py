import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI, AuthenticationError

# ===============================
# تحميل المتغيرات السرية
# ===============================
load_dotenv()

# الحصول على المفاتيح من المتغيرات البيئية
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# ===============================
# التحقق من المتغيرات مع عرض واضح
# ===============================
def check_environment():
    """فحص المتغيرات البيئية وإعلام المستخدم"""
    issues = []
    
    if not SUPABASE_URL:
        issues.append("❌ SUPABASE_URL غير مضبوط")
    elif "supabase.co" not in SUPABASE_URL:
        issues.append("⚠️ SUPABASE_URL قد يكون غير صحيح")
    
    if not SUPABASE_KEY:
        issues.append("❌ SUPABASE_KEY غير مضبوط")
    
    if not OPENAI_API_KEY:
        issues.append("❌ OPENAI_API_KEY غير مضبوط")
    elif not OPENAI_API_KEY.startswith("sk-"):
        issues.append("⚠️ OpenAI API Key غير صالح (يجب أن يبدأ بـ sk-)")
    
    return issues

# ===============================
# إعدادات آمنة للـ OpenAI
# ===============================
@st.cache_resource
def init_openai():
    """تهيئة عميل OpenAI مع معالجة الأخطاء"""
    if not OPENAI_API_KEY:
        st.error("OpenAI API Key غير موجود")
        return None
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        # اختبار بسيط للتحقق من صحة المفتاح
        test_response = client.models.list()
        st.sidebar.success("✅ OpenAI متصل بنجاح")
        return client
    except AuthenticationError:
        st.error("🔑 مفتاح OpenAI غير صالح أو منتهي الصلاحية")
        return None
    except Exception as e:
        st.error(f"خطأ في الاتصال بـ OpenAI: {str(e)}")
        return None

@st.cache_resource
def init_supabase():
    """تهيئة عميل Supabase مع معالجة الأخطاء"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("إعدادات Supabase غير مكتملة")
        return None
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # اختبار الاتصال
        client.table("users").select("*").limit(1).execute()
        st.sidebar.success("✅ Supabase متصل بنجاح")
        return client
    except Exception as e:
        st.error(f"خطأ في الاتصال بـ Supabase: {str(e)}")
        return None

# ===============================
# تهيئة العملاء
# ===============================
def initialize_clients():
    """تهيئة كافة العملاء مع التعامل مع الأخطاء"""
    # التحقق من البيئة أولاً
    issues = check_environment()
    
    if issues:
        with st.sidebar:
            st.error("مشكلات في الإعدادات:")
            for issue in issues:
                st.write(issue)
        
        # عرض إرشادات للمستخدم
        if st.session_state.get("logged_in"):
            st.warning("""
            **تحذير:** هناك مشكلة في إعدادات النظام
            
            يرجى:
            1. التحقق من ملف `.env`
            2. التأكد من صحة المفاتيح
            3. إعادة تشغيل التطبيق
            """)
        return None, None
    
    # تهيئة العملاء
    supabase_client = init_supabase()
    openai_client = init_openai()
    
    return supabase_client, openai_client

# ===============================
# تحديث الدوال التي تستخدم الذكاء الاصطناعي
# ===============================
def safe_ai_call(func):
    """مُغلف للتعامل الآمن مع استدعاءات OpenAI"""
    def wrapper(*args, **kwargs):
        if not ai_client:
            st.warning("⏸️ خدمة الذكاء الاصطناعي غير متاحة حالياً")
            return "الخدمة غير متوفرة. يرجى التحقق من إعدادات OpenAI API Key."
        
        try:
            return func(*args, **kwargs)
        except AuthenticationError:
            st.error("🔑 خطأ في مصادقة OpenAI. يرجى التحقق من API Key.")
            return "حدث خطأ في الخدمة."
        except Exception as e:
            st.error(f"خطأ في خدمة الذكاء الاصطناعي: {str(e)}")
            return f"حدث خطأ: {str(e)}"
    
    return wrapper

@safe_ai_call
def generate_exercise_safe(subject, lesson, level):
    """نسخة آمنة من توليد التمارين"""
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
        model="gpt-3.5-turbo",  # استخدام نموذج أقل تكلفة للاختبار
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7
    )

    return response.choices[0].message.content

@safe_ai_call
def chat_with_ai_safe(messages):
    """نسخة آمنة من الدردشة مع AI"""
    response = ai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )
    return response.choices[0].message.content

# ===============================
# تحديث صفحة المساعد التعليمي
# ===============================
def chatbot_page():
    """صفحة المساعد التعليمي مع معالجة الأخطاء"""
    st.markdown("### 🤖 مساعدك التعليمي الذكاء الاصطناعي")
    
    # تحذير إذا لم يكن AI متاحاً
    if not ai_client:
        st.warning("""
        ⚠️ **خدمة الذكاء الاصطناعي غير متاحة حالياً**
        
        **لحل هذه المشكلة:**
        1. تأكد من صحة `OPENAI_API_KEY` في ملف `.env`
        2. تحقق من رصيد حساب OpenAI
        3. تأكد من تفعيل API Key
        
        **للاختبار بدون OpenAI:**
        - يمكنك استخدام الميزات الأخرى
        - التواصل مع الأستاذ مباشرة
        - استعراض الدروس المتاحة
        """)
        
        # عرض بدائل
        st.info("💡 **بدائل مؤقتة:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📚 استعراض الدروس المتاحة"):
                st.switch_page("pages/1_👨‍🎓_الطالب.py")
        with col2:
            if st.button("🧠 تمارين تجريبية"):
                st.session_state.show_sample_exercises = True
        
        return
    
    # تهيئة محادثة
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # عرض تاريخ المحادثة
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # إدخال المستخدم
    if prompt := st.chat_input("اطرح سؤالك التعليمي هنا..."):
        # إضافة سؤال المستخدم
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # الحصول على الإجابة
        with st.chat_message("assistant"):
            with st.spinner("🤖 جاري التفكير..."):
                try:
                    messages = [
                        {"role": "system", "content": "أنت مساعد تعليمي ذكي."},
                        *[{"role": msg["role"], "content": msg["content"]} 
                          for msg in st.session_state.chat_history[-6:]]
                    ]
                    
                    answer = chat_with_ai_safe(messages)
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    st.error(f"حدث خطأ: {str(e)}")
                    # إضافة إجابة بديلة
                    st.markdown("""
                    **عذراً، واجهت صعوبة في الاتصال بالخدمة.**
                    
                    يمكنك:
                    - إعادة المحاولة لاحقاً
                    - تصفح الدروس المتاحة
                    - الاطلاع على الأسئلة الشائعة
                    """)

# ===============================
# تحديث الدالة الرئيسية
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
    }
    .stMetric {
        text-align: center;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # تهيئة العملاء بشكل عالمي
    global supabase, ai_client
    supabase, ai_client = initialize_clients()
    
    # التحقق من تسجيل الدخول
    if not st.session_state.get("logged_in"):
        login_page()
    else:
        # عرض حالة الاتصال في الشريط الجانبي
        with st.sidebar:
            if not ai_client:
                st.warning("🤖 AI غير متصل")
            if not supabase:
                st.warning("🗄️ قاعدة البيانات غير متصلة")
        
        selected = sidebar_menu()
        
        # توجيه حسب الدور
        if st.session_state.role == "طالب":
            student_dashboard(selected)
        elif st.session_state.role == "أستاذ":
            teacher_dashboard(selected)
        elif st.session_state.role == "إداري":
            admin_dashboard(selected)

# ===============================
# تشغيل التطبيق
# ===============================
if __name__ == "__main__":
    main()
