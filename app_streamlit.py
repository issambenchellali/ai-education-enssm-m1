"""
المنصة التعليمية الذكية - الإصدار النهائي
تم التصميم للعمل على Streamlit Cloud بدون مشاكل
"""

import streamlit as st
import os

# ============================================
# إعدادات الصفحة
# ============================================
st.set_page_config(
    page_title="المنصة التعليمية الذكية",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# تنسيق CSS
# ============================================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1E88E5;
        padding: 20px;
        font-size: 2.5rem;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# الصفحة الرئيسية
# ============================================
def main():
    """الصفحة الرئيسية للتطبيق"""
    
    # العنوان الرئيسي
    st.markdown('<h1 class="main-header">🎓 المنصة التعليمية الذكية</h1>', unsafe_allow_html=True)
    
    # رسالة نجاح كبيرة
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown("### ✅ **تم النشر بنجاح على Streamlit Cloud!**")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # تأثير بصري
    st.balloons()
    
    # قسم المميزات
    st.markdown("---")
    st.subheader("✨ مميزات المنصة المتكاملة")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 👨‍🎓 **للطلاب**")
            st.write("• 📖 دروس تفاعلية")
            st.write("• 🧠 تمارين ذكية")
            st.write("• 📊 تتبع التقدم")
    
    with col2:
        with st.container(border=True):
            st.markdown("### 👨‍🏫 **للأساتذة**")
            st.write("• 📤 رفع المحتوى")
            st.write("• ✏️ إنشاء اختبارات")
            st.write("• 👥 متابعة الطلاب")
    
    with col3:
        with st.container(border=True):
            st.markdown("### 👨‍💼 **للإدارة**")
            st.write("• 👤 إدارة المستخدمين")
            st.write("• 📈 تقارير أداء")
            st.write("• ⚙️ إعدادات متقدمة")
    
    # قسم تسجيل الدخول البسيط
    st.markdown("---")
    st.subheader("🔐 نظام تسجيل الدخول")
    
    tab1, tab2 = st.tabs(["تسجيل الدخول", "حسابات تجريبية"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            
            if st.form_submit_button("🚀 دخول إلى المنصة"):
                if username and password:
                    # بيانات تجريبية
                    users = {
                        "طالب": "123456",
                        "أستاذ": "123456", 
                        "مدير": "123456"
                    }
                    
                    if username in users and users[username] == password:
                        st.session_state.logged_in = True
                        st.session_state.user = username
                        st.session_state.role = username
                        st.success(f"✅ مرحباً {username}! تم تسجيل الدخول بنجاح")
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                else:
                    st.warning("⚠️ يرجى تعبئة جميع الحقول")
    
    with tab2:
        st.info("""
        **💡 للحصول على تجربة كاملة، استخدم إحدى الحسابات:**
        
        | الدور | اسم المستخدم | كلمة المرور |
        |-------|--------------|-------------|
        | طالب | `طالب` | `123456` |
        | أستاذ | `أستاذ` | `123456` |
        | مدير | `مدير` | `123456` |
        """)
    
    # قسم معلومات النظام
    st.markdown("---")
    with st.expander("🔧 معلومات النظام التقنية"):
        st.write(f"**إصدار Streamlit:** `{st.__version__}`")
        st.write(f"**بيئة التشغيل:** `Streamlit Cloud`")
        st.write(f"**مسار العمل:** `{os.getcwd()}`")
        
        # عرض الملفات الموجودة
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        st.write(f"**الملفات في المشروع:** `{', '.join(files)}`")
        
        # التحقق من requirements.txt
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                st.code(f.read(), language='txt')

# ============================================
# صفحة الطالب (بعد التسجيل)
# ============================================
def student_dashboard():
    """لوحة تحكم الطالب"""
    
    with st.sidebar:
        st.title(f"👋 {st.session_state.user}")
        st.write(f"**الدور:** {st.session_state.role}")
        st.markdown("---")
        
        menu = st.radio(
            "القائمة",
            ["🏠 الرئيسية", "📚 الدروس", "🧠 تمارين", "📊 تقدمي", "⚙️ إعدادات"]
        )
        
        st.markdown("---")
        if st.button("🚪 تسجيل الخروج"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    if menu == "🏠 الرئيسية":
        st.title("🏠 لوحة الطالب الرئيسية")
        
        # إحصائيات
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("الدروس المكتملة", "12", "+3")
        with col2:
            st.metric("التمارين المحلولة", "47", "+8")
        with col3:
            st.metric("مستوى التقدم", "75%", "+5%")
        
        # دروس موصى بها
        st.subheader("🎯 دروس موصى بها")
        
        lessons = [
            {"name": "الجبر الأساسي", "subject": "رياضيات", "icon": "🔢"},
            {"name": "قوانين نيوتن", "subject": "فيزياء", "icon": "⚛️"},
            {"name": "القواعد النحوية", "subject": "لغة عربية", "icon": "📖"},
        ]
        
        for lesson in lessons:
            with st.container(border=True):
                col_a, col_b = st.columns([1, 4])
                with col_a:
                    st.markdown(f"## {lesson['icon']}")
                with col_b:
                    st.write(f"**{lesson['name']}**")
                    st.write(f"*{lesson['subject']}*")
                    if st.button("بدء الدرس", key=lesson['name']):
                        st.success(f"بدأت درس {lesson['name']}")
    
    elif menu == "📚 الدروس":
        st.title("📚 مكتبة الدروس")
        st.write("هنا ستجد جميع الدروس المتاحة")
        
        # قائمة دروس تجريبية
        for i in range(1, 6):
            with st.expander(f"الدرس {i}: عنوان الدرس التجريبي"):
                st.write("محتوى الدرس سيكون هنا في النسخة الكاملة")
                if st.button(f"بدء الدرس {i}", key=f"start_{i}"):
                    st.success(f"بدأت الدرس {i}")
    
    elif menu == "🧠 تمارين":
        st.title("🧠 التمارين التعليمية")
        
        # تمرين تفاعلي بسيط
        st.subheader("تمرين الرياضيات")
        st.write("**ما هو حاصل ضرب ٧ × ٨؟**")
        
        answer = st.number_input("أدخل إجابتك:", min_value=0, max_value=100)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 تسليم الإجابة"):
                if answer == 56:
                    st.success("✅ إجابة صحيحة! أحسنت")
                    st.balloons()
                else:
                    st.error("❌ إجابة خاطئة، حاول مرة أخرى")
        
        with col2:
            if st.button("💡 عرض الإجابة"):
                st.info("الإجابة الصحيحة هي: ٥٦")
    
    elif menu == "📊 تقدمي":
        st.title("📊 تتبع تقدمي")
        
        # بيانات تقدم بسيطة
        st.subheader("تقدمك في المواد")
        
        import matplotlib.pyplot as plt
        import numpy as np
        
        # إنشاء رسم بياني بسيط
        fig, ax = plt.subplots(figsize=(10, 6))
        subjects = ['رياضيات', 'علوم', 'لغة عربية', 'فيزياء']
        scores = [85, 70, 90, 65]
        
        bars = ax.bar(subjects, scores, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        
        # إضافة التسميات
        ax.set_ylabel('النسبة المئوية')
        ax.set_title('أداؤك في المواد المختلفة')
        ax.set_ylim(0, 100)
        
        # إضافة القيم على الأعمدة
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{score}%', ha='center', va='bottom')
        
        st.pyplot(fig)
        
        # تحليل التقدم
        st.subheader("💡 تحليل أدائك")
        st.write("""
        - **الرياضيات:** أداء ممتاز! يمكنك التقدم للمستوى المتقدم
        - **العلوم:** جيد، ولكن يمكن تحسينه بالممارسة الإضافية
        - **اللغة العربية:** ممتاز! حافظ على هذا المستوى
        - **الفيزياء:** يحتاج تركيز أكثر على الفهم العميق
        """)
    
    elif menu == "⚙️ الإعدادات":
        st.title("⚙️ إعدادات الحساب")
        
        with st.form("settings"):
            name = st.text_input("الاسم الكامل", value="طالب نموذجي")
            email = st.text_input("البريد الإلكتروني", value="student@example.com")
            notifications = st.checkbox("تلقي إشعارات", value=True)
            
            if st.form_submit_button("💾 حفظ التغييرات"):
                st.success("✅ تم حفظ الإعدادات بنجاح")

# ============================================
# الدالة الرئيسية للتشغيل
# ============================================
if __name__ == "__main__":
    # التحقق من حالة تسجيل الدخول
    if not st.session_state.get('logged_in'):
        main()
    else:
        # توجيه حسب الدور
        if st.session_state.role == "طالب":
            student_dashboard()
        else:
            st.title(f"👋 مرحباً {st.session_state.user}")
            st.info("لوحة التحكم لهذا الدور قيد التطوير")
            if st.button("العودة للصفحة الرئيسية"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
