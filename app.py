import json
import os
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

DATA_FILE = "participants.json"


def load_participants():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_participants_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/participants", methods=["GET"])
def get_participants():
    return jsonify(load_participants())


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "بيانات غير صالحة"}), 400

    name = str(data.get("name", "")).strip()
    number_raw = data.get("number")
    telegram = str(data.get("telegram", "")).strip()

    # 1. فحص الاسم
    if not name:
        return (
            jsonify({"status": "error", "message": "يرجى كتابة الاسم بشكل صحيح"}),
            400,
        )

    # 2. فحص التليجرام
    if not telegram.startsWith("@"):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "اكتب يوزرك ب الشكل الاتي مثال @mgpka باستخدام @",
                }
            ),
            400,
        )

    if telegram.lower() == "@mgpka":
        return (
            jsonify(
                {"status": "error", "message": "هذا اليوزر غير مسموح باستخدامه"}
            ),
            400,
        )

    # 3. فحص الرقم
    try:
        number = int(number_raw)
        if number < 1 or number > 30:
            raise ValueError()
    except Exception:
        return (
            jsonify(
                {"status": "error", "message": "خطأ: اختر رقم بين 1 و 30 فقط"}
            ),
            400,
        )

    participants = load_participants()

    # 4. فحص توفر الرقم بالسيرفر الموحد
    if any(p.get("number") == number for p in participants):
        return (
            jsonify({"status": "error", "message": "الرقم محجوز اختر رقم اخر"}),
            400,
        )

    # حفظ المشارك بالسيرفر
    participants.append({"name": name, "number": number, "telegram": telegram})
    save_participants_data(participants)

    return jsonify({"status": "success"})


@app.route("/api/delete", methods=["POST"])
def delete_participant():
    data = request.get_json()
    index = data.get("index")
    participants = load_participants()

    if index is not None and 0 <= index < len(participants):
        participants.pop(index)
        save_participants_data(participants)
        return jsonify({"status": "success"})

    return jsonify({"status": "error", "message": "العنصر غير موجود"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
