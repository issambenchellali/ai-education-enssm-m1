import streamlit as st
import pandas as pd
import random

# تحميل البيانات
@st.cache_data
def load_data():
    return pd.read_csv("activities.csv")

data = load_data()

st.title("📘 منصة تعليمية ذكية")

# اختيار الطور
level = st.selectbox("اختر الطور الدراسي", data["level_stage"].unique())

# اختيار المادة
subjects = data[data["level_stage"] == level]["subject"].unique()
subject = st.selectbox("اختر المادة", subjects)

# اختيار الحصة
lessons = data[
    (data["level_stage"] == level) &
    (data["subject"] == subject)
]["lesson"].unique()
lesson = st.selectbox("اختر الحصة", lessons)

# زر اقتراح النشاط
if st.button("🔄 اقتراح نشاط"):
    filtered = data[
        (data["level_stage"] == level) &
        (data["subject"] == subject) &
        (data["lesson"] == lesson)
    ]

    if len(filtered) == 0:
        st.warning("لا يوجد نشاط متاح")
    else:
        # اختيار النشاط الأقل استعمالًا
        activity = filtered.sort_values("usage_count").iloc[0]

        st.subheader("📖 الشرح")
        st.write(activity["description"])

        st.subheader("✏️ التمارين")
        st.write(activity["exercises"])

        st.subheader("🧪 التطبيق")
        st.write(activity["application"])

        # تحديث عدد الاستعمال
        data.loc[data["id"] == activity["id"], "usage_count"] += 1
        data.to_csv("activities.csv", index=False)

        st.success("تم اقتراح نشاط جديد ✅")



