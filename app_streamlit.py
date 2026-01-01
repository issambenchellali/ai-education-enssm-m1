import streamlit as st
import time

# إعدادات الصفحة
st.set_page_config(
    page_title="المنصة التعليمية",
    page_icon="📚",
    layout="wide"
)

# تنسيق بسيط
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1E88E5;
        font-size: 3rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# العنوان الرئيسي
st.markdown('<h1 class="main-title">📚 المنصة التعليمية الذكية</h1>', unsafe_allow_html=True)
st.markdown("### ✅ نجحت! التطبيق يعمل على Streamlit Cloud")

# رسالة نجاح
st.balloons()
st.success("🎉 تم بناء التطبيق وتشغيله بنجاح!")

# محاكاة للتأكد من عمل مكتبات Python
st.markdown("---")
st.subheader("🔍 اختبار النظام")

# اختبار مكتبات Python الأساسية
try:
    import sys
    st.write(f"✅ **Python Version:** {sys.version.split()[0]}")
except:
    st.write("❌ Python غير متاح")

try:
    st.write(f"✅ **Streamlit Version:** {st.__version__}")
except:
    st.write("❌ Streamlit غير متاح")

# قسم المميزات
st.markdown("---")
st.subheader("✨ مميزات المنصة")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **👨‍🎓 للطلاب:**
    - دروس تفاعلية
    - تمارين ذكية
    - تتبع التقدم
    """)

with col2:
    st.info("""
    **👨‍🏫 للأساتذة:**
    - رفع المحتوى
    - إنشاء اختبارات
    - متابعة الطلاب
    """)

with col3:
    st.info("""
    **👨‍💼 للإدارة:**
    - إدارة المستخدمين
    - تقارير وإحصائيات
    - إعدادات النظام
    """)

# زر تفاعلي بسيط
st.markdown("---")
if st.button("🎯 جرب نظام الدخول المبسط"):
    name = st.text_input("ما اسمك؟")
    if name:
        st.success(f"مرحباً {name}! 👋")

# معلومات تقنية
with st.expander("⚙️ معلومات تقنية"):
    st.write("**الحالة:** 🟢 تعمل بشكل مثالي")
    st.write(f"**الوقت:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
    st.write("**البيئة:** Streamlit Cloud")
    st.code("""
    # للتحقق من عمل Python
    import platform
    print(f"Python: {platform.python_version()}")
    print(f"System: {platform.system()}")
    """)

# تذييل الصفحة
st.markdown("---")
st.caption("تم تطوير المنصة التعليمية باستخدام Streamlit | © 2024")
