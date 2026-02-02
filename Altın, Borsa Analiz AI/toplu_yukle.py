import os
import rag_engine  # Senin yazdığın motoru kullanıyoruz

# --- AYARLAR ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BELGELER_DIR = os.path.join(BASE_DIR, 'yuklenenler')  

def toplu_taramayi_baslat():
    print("="*40)
    print("🚀 TOPLU PDF YÜKLEME MODÜLÜ BAŞLATILIYOR")
    print("="*40)

    # Klasör kontrolü
    if not os.path.exists(BELGELER_DIR):
        print(f"❌ HATA: '{BELGELER_DIR}' klasörü bulunamadı!")
        print("Lütfen 'belgeler' adında bir klasör oluşturup içine 'altin' ve 'borsa' klasörlerini açın.")
        return

    # Kategorileri Tara (altin ve borsa)
    kategoriler = ['altin', 'borsa']

    toplam_dosya = 0

    for kategori in kategoriler:
        kategori_yolu = os.path.join(BELGELER_DIR, kategori)
        
        # Eğer kategori klasörü yoksa uyar ve geç
        if not os.path.exists(kategori_yolu):
            print(f"⚠️ UYARI: '{kategori}' klasörü yok, geçiliyor...")
            continue
        
        print(f"\n📂 Kategori Taranıyor: {kategori.upper()}...")
        print("-" * 30)

        # Klasördeki dosyaları listele
        dosyalar = os.listdir(kategori_yolu)
        
        if not dosyalar:
            print("   (Bu klasör boş)")
            continue

        for dosya in dosyalar:
            # Sadece PDF dosyalarını al
            if dosya.lower().endswith('.pdf'):
                dosya_tam_yolu = os.path.join(kategori_yolu, dosya)
                
                print(f"   📄 İşleniyor: {dosya} ...", end="", flush=True)
                try:
                    # RAG Motorunu çağırıp işi yaptırıyoruz
                    rag_engine.index_pdf(dosya_tam_yolu, kategori)
                    print(" ✅ TAMAM")
                    toplam_dosya += 1
                except Exception as e:
                    print(f" ❌ HATA: {e}")
            else:
                print(f"   ⏩ Atlandı (PDF değil): {dosya}")

    print("\n" + "="*40)
    print(f"🎉 İŞLEM BİTTİ! Toplam {toplam_dosya} belge hafızaya eklendi.")
    print("="*40)

if __name__ == "__main__":
    toplu_taramayi_baslat()