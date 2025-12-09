from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "dev"

# ───────────────────────────── SORULAR ─────────────────────────────
QUESTIONS = {
    "start": {
        "id": "start",
        "title": "Nerede yaşıyorsun?",
        "images": ["01sehirli.png", "02koylu.png"],
        "multi": False,
        "options": [
            {"value": "koylu", "label": "Köylüyüm", "next": "k_1",      "score": 0},
            {"value": "sehirli", "label": "Şehirliyim", "next": "s_1",  "score": 0},
        ],
    },

    # ====================== KÖYLÜ YOLU ======================
    "k_1": {"id": "k_1", "title": "Bahçen var mı?", "image": "06koylu.png", "multi": False, "options": [
        {"value": "yes", "label": "Evet", "next": "k_1a",               "score": 0},
        {"value": "no",  "label": "Hayır", "next": "k_2",               "score": 0},
    ],},
    "k_1a": {"id": "k_1a", "title": "Bahçede damla sulama sistemi kullanıyor musun?", "image": "14koylu.png", "multi": False, "options": [
        {"value": "yes", "label": "Evet",                               "score": 10},
        {"value": "no",  "label": "Hayır",                              "score": -10},
    ], "next_default": "k_1b"},
    "k_1b": {"id": "k_1b", "title": "Bahçede neleri kullanıyorsun?", "image": "04"
    "koylu.png", "multi": False, "options": [
        {"value": "suni",  "label": "Suni gübre",                       "score": -10},
        {"value": "dogal", "label": "Doğal gübre",                      "score": 10},
    ], "next_default": "k_2"},
    "k_2": {"id": "k_2", "title": "Araban var mı?", "image": "27koylu.png", "multi": False, "options": [
        {"value": "yes", "label": "Evet", "next": "k_2a",               "score": 0},
        {"value": "no",  "label": "Hayır", "next": "k_2b",              "score": 0},
    ]},
    "k_2a": {"id": "k_2a", "title": "Hangi araçlara sahipsin?", "images": ["16koylu.png", "28koylu.png"], "multi": True, "options": [
        {"value": "tractor", "label": "Traktör",                        "score": 5},
        {"value": "car",     "label": "Araba",                          "score": -10},
        {"value": "jeep",    "label": "Jeep",                           "score": -20},
        {"value": "cart",    "label": "At arabası",                     "score": 15},
    ], "next_default": "k_3"},
    "k_2b": {"id": "k_2b", "title": "Ulaşım araçların?", "multi": True, "image": "15sehirli.png", "options": [
        {"value": "bus",   "label": "Toplu taşıma",                     "score": 8},
        {"value": "horse", "label": "At",                               "score": 15},
        {"value": "bike",  "label": "Bisiklet",                         "score": 10},
    ], "next_default": "k_3"},
    "k_3": {"id": "k_3", "title": "Şehir elektriği dışında enerji kullanıyor musun?", "image": "12koylu.png", "multi": False, "options": [
        {"value": "yes", "label": "Evet", "next": "k_3a",               "score": 0},
        {"value": "no",  "label": "Hayır", "next": "k_4",               "score": 0},
    ]},
   
    "k_3a": {"id": "k_3a", "title": "Hangi alternatif enerji?", "multi": True, "images": ["12koylu.png", "a4.png"] , "options": [
        {"value": "solar", "label": "Güneş paneli",                     "score": 15},
        {"value": "wind",  "label": "Rüzgâr türbini",                   "score": 15},
        {"value": "water", "label": "Su değirmeni",                     "score": 15},
    ], "next_default": "k_4"},

    "k_4": {"id": "k_4", "title": "Su Ayak İzi", "multi": True, "images": ["29koylu.png", "a3.png"] , "options": [
        {"value": "musluk", "label": "Musluğu açık bırakmam",           "score": 5},
        {"value": "machine",  "label": "Bulaşık makinesi kullanırım",   "score": 8},
        {"value": "pool", "label": "Havuzum var",                       "score": -20},
    ], "next_default": "k_4a"},

    "k_4a": {"id": "k_4a", "title": "Çamaşırları nasıl yıkarsın?", "images": ["19koylu.png", "30koylu.png"], "multi": False, "options": [
        {"value": "river", "label": "Nehirde yıkarım",                  "score": 15},
        {"value": "clotes",  "label": "Çamaşır makinesi kullanırım",    "score": -10},
    ], "next_default": "k_4b"},

    "k_4b": {"id": "k_4b", "title": "Nasıl yıkanırsın?", "multi": False, "images": ["17bath.png", "11koylu.png"], "options": [
        {"value": "home", "label": "Evde",                             "score": -5},
        {"value": "falls",  "label": "Nehirde",                          "score": 10},
    ], "next_default": "k_5"},

    "k_5": {"id": "k_5", "title": "Hava Ayak İzi", "images":[ "22koylu.png", "26sehirli.png"], "multi": True, "options": [
        {"value": "forest", "label": "Ormanda kontrollü ateş yakarım ",                         "score": 10},
        {"value": "forestfire",  "label": "Orman söndürme faaliyetlerine katılırım ",           "score": 15},
        {"value": "new_three",  "label": "Kestiğim ağaçların yerine yeni fidanlar dikerim",     "score": 12},
    ], "next_default": "k_6"},

    "k_6": {"id": "k_6", "title": "Atık ve Geri Dönüşüm", "images": ["23sehirli.png","a10.png"] , "multi": True, "options": [
        {"value": "picknic", "label": "Piknikte çöplerimi toplarım",                            "score": 5},
        {"value": "food",  "label": "Yemek artıklarını hayvanlara veririm",                     "score": 10},
    ], "next_default": "k_7"},

    "k_7": {"id": "k_7", "title": "Hangi ısınmayı/soğutmayı kullanıyorsun?", "image": "15sehirli.png", "multi": True, "options": [
        {"value": "fireplace", "label": "Şömine",                                           "score": -10},
        {"value": "electrics",  "label": "Şebeke elektriği (klima, ızgara)",                "score": -5},
        {"value": "Sun",  "label": "Doğal kaynak elektrik (Güneş, su veya rüzgâr)",         "score": 10},
    ], "next_default": "result"},

    # ====================== ŞEHİRLİ YOLU ======================
    "s_1": {"id": "s_1", "title": "Yeşil alışkanlıkların neler?", "images": ["25sehirli.png", "24sehirli.png"], "multi": True, "options": [
        {"value": "organik", "label": "Organik bahçem var",                         "score": 15},
        {"value": "balkon",  "label": "Balkonda sebze yetiştiriyorum",              "score": 12},
        {"value": "market",  "label": "Süpermarketten alıyorum",                    "score": -15},
    ], "next_default": "s_2"},

    "s_2": {"id": "s_2", "title": "Kişisel araban var mı?", "image": "21sehirli.png", "multi": False, "options": [
        {"value": "yes", "label": "Evet",  "next": "s_2a",                          "score": 0},
        {"value": "no",  "label": "Hayır", "next": "s_2b",                          "score": 0},
    ]},

    "s_2a": {"id": "s_2a", "title": "Araba türü?", "multi": True, "images": ["21sehirli.png", "31sehirli.png"], "options": [
        {"value": "electric", "label": "Elektrikli / Hibrit",                       "score": 15},
        {"value": "diesel",   "label": "Dizel",                                     "score": -5},
        {"value": "gasoline", "label": "Benzinli",                                  "score": -18},
        {"value": "GPL", "label": "LPG",                                            "score": 5},
    ], "next_default": "s_3"},

    "s_2b": {"id": "s_2b", "title": "Günlük ulaşımda en çok ne kullanıyorsun?", "image": "20sehirli.png", "multi": False, "options": [
        {"value": "public", "label": "Toplu taşıma",                                "score": 10},
        {"value": "bike",   "label": "Bisiklet",                                    "score": 15},
        {"value": "taxi",   "label": "Taksi",                                       "score": -5},
        {"value": "car",    "label": "Scooter",                                     "score": 12},
    ], "next_default": "s_3"},

    "s_3": {"id": "s_3", "title": "Elektrik tüketiminde nelere dikkat ediyorsun?", "image": "07sehirli.png", "multi": True, "options": [
        {"value": "e-ocak",              "label": "Elektrikli ocak/indüksiyon kullanıyorum",    "score": 5},
        {"value": "smart-home",         "label": "Akıllı ev sistemleri var",                    "score": 15},
        {"value": "e-etiket",            "label": "Elektrik tüketim etiketine bakarım",         "score": 5},
        {"value": "rechargeable_battery","label": "Şarj edilebilir pil kullanırım",             "score": 5},
    ], "next_default": "s_4"},

    "s_4": {"id": "s_4", "title": "Su kullanım alışkanlıkların nasıl?", "images":[ "10sehirli.png","18sehirli.png"], "multi": True, "options": [
        {"value": "water_musluk",       "label": "Diş fırçalarken musluğu kapatırım",      "score": 10},
        {"value": "bulasik_mashine",    "label": "Bulaşık makinesini tam doldururum",      "score": 8},
        {"value": "chamashir_mashine",  "label": "Çamaşır makinesini tam doldururum",      "score": 8},
        {"value": "havuz",              "label": "Evimde/ sitede havuz var",               "score": -15},
    ], "next_default": "s_4a"},

    "s_4a": {   
        "id": "s_4a",
        "title": "Banyoda nasıl yıkanıyorsun?",
        "images": ["16bath.png", "17bath.png"],
        "multi": False,
        "options": [
            {"value": "kuvet",      "label": "Küvet dolduruyorum",                  "score": -15},
            {"value": "uzun_dus",   "label": "Duşakabinde duş alıyorum",            "score": 10},
        ],
        "next_default": "s_5"
    },

    "s_5": {   
        "id": "s_5",
        "title": "Hava Ayak İzi",
        "images": ["26sehirli.png", "24sehirli.png"],
        "multi": True,
        "options": [
            {"value": "sprey",      "label": "Sprey ürünleri kullanırım",                   "score": -15},
            {"value": "babrika",   "label": "Olduğum fabrikada baca filtresi var",         "score": 10},
            {"value": "three",   "label": "Ağaçlandırma kampanyalarına katılırım",       "score": 15},
            {"value": "market",   "label": "Çevre dostu marketlerden alışveriş yaparım",  "score": 10},
        ],
        "next_default": "s_6"
    },

    "s_6": {
        "id": "s_6",
        "title": "Atık ve Geri Dönüşüm?",
        "images": ["13sehirli.png", "32sehirli.png"],
        "multi": True,
        "options": [
            {"value": "recycle", "label": "Geri dönüşüm çöpü kullanırım",               "score": 10},
            {"value": "paper",   "label": "Kâğıdı tasarruflu kullanırım",               "score": 10},
            {"value": "bicyle",  "label": "Mahallemdeki bisikletleri tamir ederim",     "score": 15},
        ],
        "next_default": "s_7"
    },

        "s_7": {
        "id": "s_7",
        "title": "Isınma Ayak İzi",
        "image": "15sehirli.png",
        "multi": False,
        "options": [
            {"value": "dogal_gaz",  "label": "Doğal gaz ",          "score": 15},
            {"value": "elektrik",   "label": "Elektrik ızgara",     "score": -5},
            {"value": "klimna",     "label": "Klima",               "score": -10},
            {"value": "soba",       "label": "Soba",                "score": -15},
        ],
        "next_default": "result"
    },

}

# ───────────────────────────── ROUTES ─────────────────────────────
@app.route("/")
def index():
    session.clear()
    session["answers"] = {}
    return redirect(url_for("question", qid="start"))

@app.route("/q/<qid>", methods=["GET", "POST"])
def question(qid):
    # Sonuç sayfasına direkt /result gidiyoruz, /q/result diye bir şey yok
    if qid == "result":
        return redirect(url_for("result"))

    current_question = QUESTIONS.get(qid)
    if not current_question:
        return redirect(url_for("result"))

    if request.method == "POST":
        # Cevabı al
        if current_question["multi"]:
            selected = request.form.getlist("choice")
            session["answers"][qid] = selected or []
        else:
            selected = request.form.get("choice")
            if not selected:
                return "Lütfen bir seçenek seçin!", 400
            session["answers"][qid] = selected

        # Özel next varsa ona git
        if not current_question["multi"] and selected:
            for opt in current_question["options"]:
                if opt["value"] == selected and "next" in opt:
                    return redirect(url_for("question", qid=opt["next"]))

        # Default next
        next_qid = current_question.get("next_default")
        session.modified = True
        if not next_qid or next_qid == "result":
            return redirect(url_for("result"))
        return redirect(url_for("question", qid=next_qid))

    return render_template("question.html", question=current_question)

@app.route("/result")
def result():
    # Session boşsa başa dön
    if not session.get("answers"):
        return redirect(url_for("index"))

    answers = session["answers"]
    details = []
    total = 0

    print("SESSION CEVAPLARI:", answers)  # terminalde gör

    for qid, answer in answers.items():
        q = QUESTIONS.get(qid)
        if not q or not answer:
            continue

        selected = answer if isinstance(answer, list) else [answer]
        q_score = 0
        labels = []

        for opt in q["options"]:
            if opt["value"] in selected:
                labels.append(opt["label"])
                q_score += int(opt.get("score", 0))

        total += q_score
        if labels:
            details.append({
                "question": q["title"],
                "selected": ", ".join(labels),
                "points": q_score
            })

    # Sonuç seviyesi
    if total >= 130:
        label, color = "Tam bir çevre şampiyonusun!", "success"
    elif total >= 70:
        label, color = "Çok iyi, çevre dostusun!", "info"
    elif total >= 30:
        label, color = "Orta seviyede karbon ayak izi", "warning"
    else:
        label, color = "Karbon ayak izin oldukça yüksek!", "danger"

    return render_template("result.html", score=total, label=label, color=color, details=details)

if __name__ == "__main__":
    app.run(debug=True)