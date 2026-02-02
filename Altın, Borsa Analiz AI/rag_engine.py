import os
import feedparser
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- AYARLAR ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, 'chroma_db')

# --- MODELLER ---
embeddings = OllamaEmbeddings(model="llama3")
llm = Ollama(model="llama3")

# --- HABER KAYNAKLARI ---
RSS_FEEDS = {
    "altin": [
        "https://finance.yahoo.com/news/rssindex",
        "https://www.investing.com/rss/news_285.rss",
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839069"
    ],
    "borsa": [
        "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664"
    ]
}

def get_vector_db(kategori):
    save_path = os.path.join(CHROMA_PATH, kategori)
    vector_db = Chroma(persist_directory=save_path, embedding_function=embeddings)
    return vector_db

def index_pdf(dosya_yolu, kategori):
    print(f"----> İşleniyor: {dosya_yolu}")
    loader = PyPDFLoader(dosya_yolu)
    pages = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(pages)
    db = get_vector_db(kategori)
    db.add_documents(chunks)
    db.persist()
    print("----> Kayıt Başarılı!")

def fetch_latest_news(kategori):
    print(f"🌍 {kategori.upper()} için Dünya Haberleri taranıyor...")
    news_summary = ""
    feeds = RSS_FEEDS.get(kategori, RSS_FEEDS["altin"])
    
    count = 0
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                news_summary += f"- {entry.title}\n"
                count += 1
        except: pass
    
    return news_summary if news_summary else "Güncel haber bulunamadı."

def analyze_market_with_news(kategori):
    """
    TÜRKÇE ANALİZ MOTORU
    """
    guncel_haberler = fetch_latest_news(kategori)
    
    db = get_vector_db(kategori)
    retriever = db.as_retriever(search_kwargs={"k": 4})
    
    # --- BURASI DEĞİŞTİ: SERT TÜRKÇE EMRİ ---
    template = """
    Sen İstanbul Finans Merkezi'nde çalışan kıdemli, Türk bir Piyasa Stratejistisin.
    
    KURALLAR:
    1. Sana verilen haberler İngilizce olabilir. Sen bunları oku, anla ama cevabını KESİNLİKLE VE SADECE TÜRKÇE ver.
    2. Asla İngilizce cümle kurma. Finansal terimleri Türkçe açıkla.
    3. Analizini maddeler halinde, okunabilir şekilde yap.

    GÖREV:
    Aşağıdaki "GÜNCEL DÜNYA HABERLERİNİ" oku ve "AKADEMİK BİLGİ BANKASI"ndaki bilgilerle harmanlayarak bir piyasa yorumu yaz.

    GÜNCEL DÜNYA HABERLERİ (İngilizce Gelebilir):
    {news_context}
    
    AKADEMİK BİLGİ BANKASI (Senin Hafızan):
    {db_context}
    
    Lütfen şu formatta cevap ver:
    📰 **Piyasa Özeti:** (Haberlerde ne olduğunu kısaca Türkçe özetle)
    🧠 **Teorik Analiz:** (Raporlardaki bilgilere göre bu durum ne anlama geliyor?)
    🚀 **Yön Tahmini:** (Kısa vadeli beklentin nedir?)

    STRATEJİST YORUMU:
    """
    
    prompt = PromptTemplate.from_template(template)

    rag_chain = (
        {
            "news_context": lambda x: guncel_haberler,
            "db_context": retriever | (lambda docs: "\n".join([d.page_content for d in docs]))
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke("market analysis")

def ask_question(soru, kategori):
    db = get_vector_db(kategori)
    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    # Soru cevap kısmı için de Türkçe zorlaması
    template = """
    Sen uzman bir Türk analistsin. Verilen bağlamı kullanarak soruyu Türkçe cevapla.
    Bağlam: {context}
    Soru: {question}
    Cevap:
    """
    prompt = PromptTemplate.from_template(template)
    
    def format_docs(docs): return "\n\n".join(d.page_content for d in docs)
    
    rag_chain = ({"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser())
    return rag_chain.invoke(soru)