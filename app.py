# ==========================================
# AI Educational Activity Recommendation App
# ==========================================
import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# ------------------------------------------
# Configuration
# ------------------------------------------
st.set_page_config(
    page_title="نظام اقتراح أنشطة تعليمية",
    layout="centered"
)

st.title("نظام ذكي لاقتراح الأنشطة التعليمية")
st.write("نظام يقترح أنشطة تعليمية مناسبة حسب الإعاقة السمعية والمستوى والمادة")

# ------------------------------------------
# Google Sheet CSV URL
# ------------------------------------------
# مهم جدًا: غيّر هذا الرابط إلى رابط الـ CSV الصحيح
# كيف تحصل عليه؟
# 1. افتح الـ Google Sheet
# 2. File > Share > Publish to the web
# 3. اختر التبويب (Sheet) المطلوب
# 4. اختر Comma-separated values (.csv)
# 5. اضغط Publish وانسخ الرابط اللي يظهر
CSV_URL = "https://docs.google.com/spreadsheets/d/16K7B_HHqz3VYFE2CgHe15XjxNZxcm-4m94mWKtz08jU/export?format=csv&gid=0"  # عدل gid إذا كان التبويب مختلف

# أو رابط بديل شائع: /export?format=csv (بدون gid للتبويب الأول)

# ------------------------------------------
# Load Data
# ------------------------------------------
@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()  # تنظيف أسماء الأعمدة
    return df

try:
    df = load_data(CSV_URL)
except Exception as e:
    st.error(f"خطأ في تحميل البيانات: {e}")
    st.info("تأكد من أن الرابط صحيح وأن الـ Sheet منشور كـ CSV عام (Publish to the web).")
    st.stop()

# ------------------------------------------
# Sidebar Filters
# ------------------------------------------
st.sidebar.header("معايير المتعلم")

level = st.sidebar.selectbox(
    "المستوى الدراسي",
    options=sorted(df["level_stage"].unique())
)

subject = st.sidebar.selectbox(
    "المادة التعليمية",
    options=sorted(df["subject"].unique())
)

hearing = st.sidebar.selectbox(
    "درجة الإعاقة السمعية",
    options=sorted(df["hearing_type"].unique())
)

# ------------------------------------------
# Recommendation Button
# ------------------------------------------
if st.button("اقتراح النشاط المناسب"):
    filtered = df[
        (df["level_stage"] == level) &
        (df["subject"] == subject) &
        (df["hearing_type"] == hearing)
    ]
    
    if filtered.empty:
        st.warning("لا يوجد نشاط مطابق لهذه المعايير")
    else:
        activity = filtered.sample(1).iloc[0]
        st.success("النشاط المقترح")
        st.subheader(activity["activity"])
        st.write(activity["description"])
        
        # ----------------------------------
        # Display Image
        # ----------------------------------
        try:
            response = requests.get(activity["image_url"])
            response.raise_for_status()  # تحقق من نجاح الطلب
            img = Image.open(BytesIO(response.content))
            st.image(img, caption="صورة النشاط", use_column_width=True)
        except Exception:
            st.info("تعذر تحميل الصورة (تأكد من صحة الرابط في عمود image_url)")

# ------------------------------------------
# Footer
# ------------------------------------------
st.markdown("---")
st.caption("مشروع جامعي | الذكاء الاصطناعي في التعليم الدامج")