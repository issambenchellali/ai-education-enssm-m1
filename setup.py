import os

print("🚀 إعداد المنصة التعليمية الذكية")

# إنشاء ملف .env إذا لم يكن موجوداً
if not os.path.exists(".env"):
    with open(".env", "w") as f:
        f.write("""# إعدادات المنصة التعليمية الذكية
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
OPENAI_API_KEY=sk-your-api-key
""")
    print("✅ تم إنشاء ملف .env")

print("📦 قم بتثبيت المتطلبات:")
print("pip install -r requirements.txt")
print("\n🎯 قم بتشغيل التطبيق:")
print("streamlit run app.py")
