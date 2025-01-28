import os
import json
import requests
from flask import Flask, request
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# قراءة متغيرات البيئة
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALIEXPRESS_APP_KEY = os.getenv("ALIEXPRESS_APP_KEY")
ALIEXPRESS_APP_SECRET = os.getenv("ALIEXPRESS_APP_SECRET")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# رابط API تيليغرام
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# إنشاء تطبيق Flask
app = Flask(__name__)

def get_product_details(product_url):
    """استخراج تفاصيل المنتج من AliExpress API"""
    api_url = "https://api.aliexpress.com/product/details"
    params = {
        "app_key": ALIEXPRESS_APP_KEY,
        "product_url": product_url,
    }
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "product" in data:
            product = data["product"]
            return f"""
📦 *{product['title']}*
💰 السعر: {product['price']}
⭐ التقييم: {product['rating']}
🔗 [رابط المنتج]({product_url})
            """
    return "❌ حدث خطأ أثناء جلب بيانات المنتج."

@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    """استقبال الرسائل من تيليغرام"""
    update = request.get_json()
    
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]
        
        if "aliexpress.com" in text:
            reply_text = get_product_details(text)
        else:
            reply_text = "📌 أرسل رابط منتج من AliExpress للحصول على التفاصيل."
        
        requests.post(TELEGRAM_API_URL, json={"chat_id": chat_id, "text": reply_text, "parse_mode": "Markdown"})
    
    return "", 200

if __name__ == "__main__":
    app.run(port=5000)
