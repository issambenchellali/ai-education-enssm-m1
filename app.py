import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI

# ===============================
# تحميل المتغيرات السرية
# ===============================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ===============================
# التحقق من المتغيرات
# ===============================
if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
    st.error("❌ يرجى إعداد جميع المتغيرات البيئية في ملف .env")
    st.stop()

# ===============================
# إنشاء العملاء
# ===============================
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_resource
def init_openai():
    return OpenAI(api_key=OPENAI_API_KEY)

supabase = init_supabase()
ai_client = init_openai()

# ===============================
# دوال المصادقة والإدارة
# ===============================
def authenticate(username, password):
    """المصادقة مع قاعدة البيانات"""
    try:
        res = supabase.table("users").select("*").eq("username", username).execute()
        if res.data and res.data[0]["password"] == password:
            return {
                "role": res.data[0]["role"],
                "user_id": res.data[0]["id"],
                "username": username
            }
    except Exception as e:
        st.error(f"خطأ في المصادقة: {e}")
    return None

def log_activity(user_id, activity_type, details=None):
    """تسجيل النشاط"""
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
                st.session_state.update({
                    "logged_in": True,
                    "role": user_data["role"],
                    "user_id": user_data["user_id"],
                    "username": user_data["username"]
                })
                log_activity(user_data["user_id"], "login")
                st.success("✅ تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
    
    # قسم التسجيل (للتوضيح)
    with st.expander("🔧 تجربة سريعة (للتطوير)"):
        st.markdown("""
        **للتجربة السريعة أثناء التطوير:**
        
        **طالب:**  
        - اسم المستخدم: student1  
        - كلمة المرور: 123456
        
        **أستاذ:**  
        - اسم المستخدم: teacher1  
        - كلمة المرور: 123456
        
        **إداري:**  
        - اسم المستخدم: admin1  
        - كلمة المرور: 123456
        """)

# ===============================
# القائمة الجانبية المشتركة
# ===============================
def sidebar_menu():
    with st.sidebar:
        st.title(f"👋 مرحباً، {st.session_state.username}")
        st.markdown(f"**الدور:** {st.session_state.role}")
        st.divider()
        
        # القائمة حسب الدور
        if st.session_state.role == "طالب":
            menu_options = [
                "🏠 الرئيسية",
                "📚 الدروس",
                "🧠 التمارين الذكية",
                "📊 تقدمي",
                "🤖 المساعد التعليمي"
            ]
        elif st.session_state.role == "أستاذ":
            menu_options = [
                "🏠 الرئيسية",
                "📤 رفع الدروس",
                "✏️ إنشاء تمارين",
                "👨‍🎓 متابعة الطلاب",
                "📊 إحصائيات"
            ]
        else:  # إداري
            menu_options = [
                "🏠 الرئيسية",
                "👥 إدارة المستخدمين",
                "📊 لوحة التحكم",
                "📈 التقارير",
                "⚙️ الإعدادات"
            ]
        
        selected = st.radio("القائمة", menu_options, label_visibility="collapsed")
        st.divider()
        
        if st.button("🚪 تسجيل الخروج", use_container_width=True, type="secondary"):
            log_activity(st.session_state.user_id, "logout")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        return selected

# ===============================
# الصفحات الرئيسية حسب الدور
# ===============================
def student_dashboard(selected):
    if selected == "🏠 الرئيسية":
        st.title("🏠 لوحة الطالب")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("الدروس المكتملة", "12", "+3")
        with col2:
            st.metric("التمارين المحلولة", "47", "+8")
        with col3:
            st.metric("مستوى التقدم", "75%", "+5%")
        
        # اقتراح ذكي
        st.subheader("🎯 نشاط مقترح لك اليوم")
        suggestion = suggest_activity(st.session_state.user_id)
        if suggestion:
            st.info(f"نقترح عليك: {suggestion}")
            if st.button("بدء النشاط المقترح"):
                st.session_state.selected_activity = suggestion
                st.rerun()
    
    elif selected == "📚 الدروس":
        st.title("📚 مكتبة الدروس")
        display_lessons()
    
    elif selected == "🧠 التمارين الذكية":
        st.title("🧠 التمارين الذكية")
        smart_exercises_page()
    
    elif selected == "📊 تقدمي":
        st.title("📊 تتبع تقدمي")
        progress_page()
    
    elif selected == "🤖 المساعد التعليمي":
        st.title("🤖 المساعد التعليمي")
        chatbot_page()

def teacher_dashboard(selected):
    if selected == "🏠 الرئيسية":
        st.title("👨‍🏫 لوحة الأستاذ")
        
        # إحصائيات سريعة
        col1, col2 = st.columns(2)
        with col1:
            st.metric("عدد الدروس", "24")
            st.metric("الطلاب النشطين", "15")
        with col2:
            st.metric("التمارين المنشأة", "56")
            st.metric("متوسط التفاعل", "82%")
        
        # إجراءات سريعة
        st.subheader("🛠 إجراءات سريعة")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📤 رفع درس جديد", use_container_width=True):
                st.session_state.show_upload = True
                st.rerun()
        with col2:
            if st.button("✏️ إنشاء تمرين", use_container_width=True):
                st.session_state.create_exercise = True
                st.rerun()
        with col3:
            if st.button("📊 عرض التقارير", use_container_width=True):
                st.session_state.show_reports = True
                st.rerun()
    
    elif selected == "📤 رفع الدروس" or st.session_state.get('show_upload'):
        st.title("📤 رفع درس جديد")
        upload_lesson_page()
    
    elif selected == "✏️ إنشاء تمارين" or st.session_state.get('create_exercise'):
        st.title("✏️ إنشاء تمارين ذكية")
        create_exercise_page()
    
    elif selected == "👨‍🎓 متابعة الطلاب":
        st.title("👨‍🎓 متابعة أداء الطلاب")
        monitor_students_page()
    
    elif selected == "📊 إحصائيات":
        st.title("📊 الإحصائيات التفصيلية")
        statistics_page()

def admin_dashboard(selected):
    if selected == "🏠 الرئيسية":
        st.title("👨‍💼 لوحة الإدارة")
        
        # نظرة عامة
        st.subheader("📈 نظرة عامة على النظام")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي المستخدمين", "156")
        with col2:
            st.metric("الدروس المرفوعة", "89")
        with col3:
            st.metric("التفاعلات اليوم", "1,234")
        
        # مخطط سريع
        st.subheader("📊 نشاط النظام")
        chart_data = pd.DataFrame({
            'اليوم': ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة'],
            'التفاعلات': [345, 456, 567, 432, 543]
        })
        st.bar_chart(chart_data.set_index('اليوم'))
    
    elif selected == "👥 إدارة المستخدمين":
        st.title("👥 إدارة المستخدمين")
        manage_users_page()
    
    elif selected == "📊 لوحة التحكم":
        st.title("📊 لوحة التحكم الشاملة")
        control_panel_page()
    
    elif selected == "📈 التقارير":
        st.title("📈 التقارير التفصيلية")
        reports_page()
    
    elif selected == "⚙️ الإعدادات":
        st.title("⚙️ إعدادات النظام")
        settings_page()

# ===============================
# الدوال المساعدة (يتم نقلها لملفات منفصلة لاحقاً)
# ===============================
def suggest_activity(user_id):
    """اقتراح نشاط بناءً على تاريخ الطالب"""
    try:
        res = supabase.table("activity_log")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        
        if res.data:
            # هنا يمكن تطوير خوارزمية ذكية
            suggestions = [
                "درس الجبر للمبتدئين",
                "تمارين التفاضل والتكامل",
                "قراءة نص أدبي",
                "تجربة علمية بسيطة"
            ]
            import random
            return random.choice(suggestions)
    except:
        pass
    return None

def display_lessons():
    """عرض الدروس المتاحة"""
    try:
        res = supabase.table("lessons")\
            .select("*")\
            .execute()
        
        if res.data:
            for lesson in res.data:
                with st.expander(f"📖 {lesson['title']}"):
                    st.write(f"**المادة:** {lesson['subject']}")
                    st.write(f"**المستوى:** {lesson['level']}")
                    st.write(f"**الوصف:** {lesson.get('description', 'لا يوجد وصف')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📖 ابدأ الدرس", key=f"start_{lesson['id']}"):
                            st.session_state.current_lesson = lesson
                            log_activity(st.session_state.user_id, "start_lesson", lesson)
                    with col2:
                        if st.button("🧠 تمارين", key=f"ex_{lesson['id']}"):
                            generate_and_show_exercise(lesson)
        else:
            st.info("📭 لا توجد دروس متاحة بعد.")
    except Exception as e:
        st.error(f"خطأ في تحميل الدروس: {e}")

def upload_lesson_page():
    """صفحة رفع الدروس"""
    with st.form("upload_form"):
        title = st.text_input("عنوان الدرس")
        subject = st.selectbox("المادة", ["رياضيات", "علوم", "فيزياء", "كيمياء", "لغة عربية", "لغة إنجليزية"])
        level = st.selectbox("المستوى", ["ابتدائي", "متوسط", "ثانوي", "جامعي"])
        description = st.text_area("وصف الدرس")
        
        uploaded_file = st.file_uploader("رفع ملف الدرس", type=['pdf', 'txt', 'jpg', 'png', 'pptx', 'docx'])
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("📤 رفع الدرس", type="primary")
        with col2:
            ai_generate = st.form_submit_button("🤖 إنشاء محتوى بالذكاء الاصطناعي")
        
        if submit and uploaded_file:
            # هنا يتم رفع الملف لـ Supabase Storage
            file_path = f"lessons/{uploaded_file.name}"
            
            try:
                # رفع الملف
                supabase.storage.from_("educational_content")\
                    .upload(file_path, uploaded_file.getvalue())
                
                # حفظ في قاعدة البيانات
                supabase.table("lessons").insert({
                    "title": title,
                    "subject": subject,
                    "level": level,
                    "description": description,
                    "file_path": file_path,
                    "uploaded_by": st.session_state.user_id
                }).execute()
                
                st.success("✅ تم رفع الدرس بنجاح!")
                log_activity(st.session_state.user_id, "upload_lesson", {"title": title})
                
            except Exception as e:
                st.error(f"❌ خطأ في رفع الملف: {e}")
        
        elif ai_generate:
            # توليد محتوى بالذكاء الاصطناعي
            with st.spinner("🤖 جاري إنشاء المحتوى..."):
                prompt = f"""
                أنشئ محتوى تعليمي لدرس بعنوان:
                {title}
                
                المادة: {subject}
                المستوى: {level}
                
                المطلوب:
                1. مقدمة
                2. أهداف الدرس
                3. شرح مفصل
                4. أمثلة توضيحية
                5. ملخص
                """
                
                response = ai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                )
                
                st.markdown("### المحتوى المنشأ:")
                st.write(response.choices[0].message.content)
                st.download_button(
                    "📥 تحميل المحتوى",
                    response.choices[0].message.content,
                    file_name=f"{title}.txt"
                )

def smart_exercises_page():
    """صفحة التمارين الذكية"""
    st.markdown("### 🎯 تمارين مخصصة لمستواك")
    
    # تحديد التفضيلات
    col1, col2 = st.columns(2)
    with col1:
        subject = st.selectbox("اختر المادة", ["رياضيات", "علوم", "فيزياء", "لغة عربية"], key="ex_subject")
        difficulty = st.select_slider("مستوى الصعوبة", ["سهل", "متوسط", "صعب"])
    with col2:
        topic = st.text_input("الموضوع (اختياري)")
        num_questions = st.number_input("عدد الأسئلة", min_value=1, max_value=10, value=3)
    
    if st.button("🧠 توليد تمارين ذكية", type="primary"):
        with st.spinner("🤖 جاري إنشاء تمارين مخصصة لك..."):
            prompt = f"""
            أنشئ {num_questions} تمارين تعليمية:
            
            المادة: {subject}
            المستوى: {difficulty}
            الموضوع: {topic if topic else 'عام'}
            
            لكل تمرين:
            1. السؤال
            2. الخيارات (إذا كان اختيار من متعدد)
            3. الحل التفصيلي
            4. نصائح للطالب
            """
            
            response = ai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
            
            st.markdown("### 📝 تمارينك الذكية:")
            st.write(response.choices[0].message.content)
            
            # حفظ التمارين
            log_activity(st.session_state.user_id, "generate_exercises", {
                "subject": subject,
                "difficulty": difficulty,
                "count": num_questions
            })

def chatbot_page():
    """صفحة المساعد التعليمي"""
    st.markdown("### 🤖 مساعدك التعليمي الذكي")
    
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
                response = ai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "أنت مساعد تعليمي ذكي تساعد الطلاب في فهم الدروس وحل التمارين. اشرح المفاهيم بطريقة مبسطة مع أمثلة."},
                        *[{"role": msg["role"], "content": msg["content"]} 
                          for msg in st.session_state.chat_history[-6:]]  # آخر 6 رسائل
                    ],
                    max_tokens=500
                )
                
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
        
        log_activity(st.session_state.user_id, "chatbot_query", {"query": prompt[:100]})

def progress_page():
    """صفحة تتبع التقدم"""
    st.markdown("### 📊 تتبع تقدمك التعليمي")
    
    # بيانات نموذجية (يتم استبدالها ببيانات حقيقية)
    progress_data = {
        "رياضيات": 85,
        "علوم": 70,
        "لغة عربية": 90,
        "فيزياء": 65
    }
    
    # مخطط التقدم
    import plotly.graph_objects as go
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(progress_data.keys()),
            y=list(progress_data.values()),
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        )
    ])
    
    fig.update_layout(
        title="تقدمك في المواد المختلفة",
        yaxis_title="النسبة المئوية",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # إحصائيات إضافية
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ساعات التعلم", "24.5")
    with col2:
        st.metric("التحديات المكتملة", "15")
    with col3:
        st.metric("التحسن الشهري", "+12%")

# ===============================
# الدالة الرئيسية للتشغيل
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
    </style>
    """, unsafe_allow_html=True)
    
    # التحقق من تسجيل الدخول
    if not st.session_state.get("logged_in"):
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

# ===============================
# تشغيل التطبيق
# ===============================
if __name__ == "__main__":
    main()
