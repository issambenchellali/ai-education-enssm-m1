import streamlit as st
import os

# ===============================
# صفحة بداية للتأكد من عمل التطبيق
# ===============================
def main():
    st.set_page_config(
        page_title="المنصة التعليمية الذكية",
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 المنصة التعليمية الذكية - النسخة المبسطة")
    st.markdown("### ✅ التطبيق يعمل بنجاح!")
    
    # عرض حالة النظام
    st.markdown("---")
    st.subheader("📊 معلومات النظام")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Python", os.sys.version.split()[0])
    with col2:
        st.metric("Streamlit", st.__version__)
    with col3:
        st.metric("البيئة", "Streamlit Cloud")
    
    # اختبار المكتبات
    st.markdown("---")
    st.subheader("🔧 اختبار المكتبات")
    
    libraries = [
        ("Streamlit", "✅ مثبتة", lambda: True),
        ("Pandas", "تحميل...", lambda: __import__('pandas')),
        ("Plotly", "تحميل...", lambda: __import__('plotly')),
    ]
    
    for lib_name, default_msg, import_func in libraries:
        try:
            import_func()
            st.success(f"{lib_name}: ✅ مثبتة وعاملة")
        except ImportError as e:
            st.error(f"{lib_name}: ❌ غير مثبتة - {e}")
    
    # صفحة تسجيل دخول مبسطة
    st.markdown("---")
    st.subheader("🔐 تسجيل الدخول التجريبي")
    
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    
    if st.button("تسجيل الدخول"):
        if username and password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"مرحباً {username}! تم تسجيل الدخول بنجاح")
            st.rerun()
        else:
            st.error("يرجى إدخال اسم المستخدم وكلمة المرور")
    
    # معلومات إضافية
    st.markdown("---")
    with st.expander("📋 معلومات فنية"):
        st.code(f"""
        مسار العمل: {os.getcwd()}
        ملفات في المسار: {', '.join(os.listdir('.'))}
        المتغيرات البيئية: {list(os.environ.keys())[:10]}
        """)

if __name__ == "__main__":
    main()
