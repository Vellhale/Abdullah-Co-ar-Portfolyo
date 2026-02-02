from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import datetime

# --- KRİTİK NOKTA: ARTIK BURADA UZUN IMPORTLAR YOK ---
# Yapay zeka işini "rag_engine.py" dosyasına devrettik.
try:
    import rag_engine
    print("✅ RAG Motoru başarıyla bağlandı!")
except ImportError as e:
    print(f"❌ HATA: rag_engine.py dosyası bulunamadı! {e}")

app = Flask(__name__)

# --- AYARLAR ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'yuklenenler')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'piyasa.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class AnalizGecmisi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tarih = db.Column(db.DateTime, default=datetime.datetime.now)

with app.app_context():
    db.create_all()

# --- 1. GÜNCEL FİYAT (AGRESİF GETİRİCİ) ---
def altin_fiyati_getir():
    fiyat = None
    # 1. Bigpara
    try:
        url = "https://bigpara.hurriyet.com.tr/altin/gram-altin-fiyati/"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=3)
        soup = BeautifulSoup(r.text, "html.parser")
        etiket = soup.find("span", class_="text-2")
        if etiket: fiyat = etiket.text.strip()
    except: pass

    # 2. Altin.in
    if not fiyat:
        try:
            url2 = "https://altin.in/"
            r2 = requests.get(url2, headers={"User-Agent": "Mozilla/5.0"}, timeout=3)
            soup2 = BeautifulSoup(r2.text, "html.parser")
            etiket2 = soup2.find("li", id="c-gram-altin").find("span", class_="mid")
            if etiket2: fiyat = etiket2.text.strip()
        except: pass

    # 3. Hesaplama (Son Çare)
    if not fiyat:
        try:
            data = yf.download("GC=F TRY=X", period="5d", interval="1d", progress=False)
            if not data.empty:
                ons = data['Close']['GC=F'].iloc[-1]
                dolar = data['Close']['TRY=X'].iloc[-1]
                gram_hesap = (ons * dolar) / 31.1035
                if not pd.isna(gram_hesap):
                    fiyat = f"{gram_hesap:.2f}".replace('.', ',')
        except: pass

    if not fiyat or "nan" in str(fiyat).lower():
        return "Veri Bekleniyor..."
    return fiyat

# --- 2. GRAFİK VERİSİ ---
def piyasa_verisi_getir(periyot_grafik):
    try:
        data = yf.download("GC=F TRY=X", period="1y", interval="1d", group_by='ticker', auto_adjust=True, progress=False)
        if data.empty: return [], []
        
        try:
            ons = data['GC=F']['Close'] if 'GC=F' in data else data['Close']['GC=F']
            dolar = data['TRY=X']['Close'] if 'TRY=X' in data else data['Close']['TRY=X']
        except: return [], []

        df = pd.concat([ons, dolar], axis=1)
        df.columns = ['Ons', 'Dolar']
        df = df.ffill().dropna()
        df['Gram_TL'] = (df['Ons'] * df['Dolar']) / 31.1035

        if periyot_grafik == "1d": df_grafik = df.tail(5)
        elif periyot_grafik == "1mo": df_grafik = df.tail(22)
        else: df_grafik = df

        tarihler = [d.strftime("%d %b") for d in df_grafik.index]
        fiyatlar = [round(v, 2) for v in df_grafik['Gram_TL']]
        return tarihler, fiyatlar
    except: return [], []

# --- ROTALAR ---
@app.route('/')
def ana_sayfa(): return render_template('index.html')

@app.route('/api/fiyat', methods=['GET'])
def api_fiyat(): return jsonify({"fiyat": altin_fiyati_getir()})

@app.route('/api/analiz', methods=['GET'])
def api_analiz():
    periyot = request.args.get('periyot', '1mo')
    g_tarih, g_fiyat = piyasa_verisi_getir(periyot)
    return jsonify({
        "fiyat": altin_fiyati_getir(),
        "grafik": {"etiketler": g_tarih, "veriler": g_fiyat}
    })

# --- YENİ: KATEGORİLİ YÜKLEME ---
@app.route('/api/yukle', methods=['POST'])
def dosya_yukle():
    if 'file' not in request.files: return jsonify({"durum": "hata", "mesaj": "Dosya yok"})
    file = request.files['file']
    kategori = request.form.get('kategori', 'altin')
    if file.filename == '': return jsonify({"durum": "hata", "mesaj": "İsim boş"})
    if file:
        filename = secure_filename(file.filename)
        dosya_yolu = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(dosya_yolu)
        try:
            # MOTORU ÇAĞIRIYORUZ
            rag_engine.index_pdf(dosya_yolu, kategori)
            return jsonify({"durum": "basarili", "mesaj": f"{filename} '{kategori}' hafızasına eklendi!"})
        except Exception as e:
            return jsonify({"durum": "hata", "mesaj": str(e)})

# --- YENİ: KATEGORİLİ SORU SORMA ---
@app.route('/api/uzmana_sor', methods=['POST'])
def uzmana_sor():
    veri = request.json
    soru = veri.get('soru', '')
    kategori = veri.get('kategori', 'altin')
    if not soru: return jsonify({"cevap": "Soru boş."})
    try:
        # MOTORU ÇAĞIRIYORUZ
        cevap = rag_engine.ask_question(soru, kategori)
        return jsonify({"cevap": cevap})
    except Exception as e:
        return jsonify({"cevap": f"Hata: {str(e)}"})
    
# --- YENİ: HABER ANALİZİ ROTASI ---
@app.route('/api/piyasa_yorumu', methods=['POST'])
def piyasa_yorumu():
    try:
        veri = request.json
        kategori = veri.get('kategori', 'altin')
        
        # RAG Motoruna "Haberleri Oku ve Yorumla" diyoruz
        analiz = rag_engine.analyze_market_with_news(kategori)
        
        return jsonify({"durum": "basarili", "cevap": analiz})
    except Exception as e:
        return jsonify({"durum": "hata", "cevap": f"Analiz Hatası: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)