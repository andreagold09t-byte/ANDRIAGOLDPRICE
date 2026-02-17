from flask import Flask, jsonify, send_file
import requests
from bs4 import BeautifulSoup
import threading
import time

app = Flask(name)
app.config['JSON_AS_ASCII'] = False

# 1️⃣ المتغير لتخزين الأسعار
cached_prices = {}

def fetch_prices_periodically():
    global cached_prices
    while True:
        try:
            url = "https://edahabapp.com/"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")

            prices = {}
            items = soup.find_all("div", class_="price-item")
            for item in items:
                title_span = item.find("span", class_="font-medium")
                if not title_span:
                    continue
                title = title_span.text.strip()
                numbers = item.find_all("span", class_="number-font")
                if len(numbers) == 0:
                    continue
                if "عيار" in title or "الذهب" in title:
                    if len(numbers) >= 2:
                        prices[title] = {
                            "بيع": numbers[0].text.strip(),
                            "شراء": numbers[1].text.strip()
                        }
                else:
                    prices[title] = numbers[0].text.strip()

            cached_prices = prices
            print("✅ تم تحديث الأسعار")
        except Exception as e:
            print("❌ خطأ في جلب الأسعار:", e)
        
        time.sleep(60)  # تحديث كل 60 ثانية

# 2️⃣ تشغيل التحديث في الخلفية
threading.Thread(target=fetch_prices_periodically, daemon=True).start()

# 3️⃣ API يعرض البيانات المخزنة مباشرة
@app.route("/api/prices")
def prices_api():
    return jsonify(cached_prices)

@app.route("/")
def index():
    return send_file("index.html")

if name == "main":
    app.run(host="0.0.0.0", port=5000)
