// HTML elemanlarını seçiyoruz
const participantInput = document.getElementById('participantInput');
const addBtn = document.getElementById('addBtn');
const participantListUI = document.getElementById('participantList');
const countSpan = document.getElementById('count');
const drawBtn = document.getElementById('drawBtn');
const clearBtn = document.getElementById('clearBtn');
const resultContainer = document.getElementById('resultContainer');
const winnerName = document.getElementById('winnerName');
const fileInput = document.getElementById('fileInput');
const fileTabsContainer = document.getElementById('fileTabs');

// --- VERİ YAPISI ---
// collections = [ { id: 123, name: "SinifA.txt", list: ["Ali", "Veli"], drawn: ["Ali"] }, ... ]
let collections = []; 
let activeCollectionId = null; // Şu an hangi dosya seçili?

// --- YEREL DEPOLAMA ---
function saveToStorage() {
    localStorage.setItem('kura_collections', JSON.stringify(collections));
    localStorage.setItem('kura_activeId', JSON.stringify(activeCollectionId));
}

function loadFromStorage() {
    const storedCollections = localStorage.getItem('kura_collections');
    const storedActiveId = localStorage.getItem('kura_activeId');

    if (storedCollections) {
        collections = JSON.parse(storedCollections);
        // Eğer kayıtlı koleksiyon varsa ve id geçerliyse onu seç, yoksa ilkini seç
        if (collections.length > 0) {
            activeCollectionId = storedActiveId ? JSON.parse(storedActiveId) : collections[0].id;
        }
    } else {
        // Hiç veri yoksa varsayılan boş bir liste oluştur
        createDefaultCollection();
    }
    renderFileTabs();
    updateListUI();
}

// Varsayılan boş liste oluşturucu
function createDefaultCollection() {
    const newId = Date.now();
    collections.push({
        id: newId,
        name: "Genel Liste",
        list: [],
        drawn: []
    });
    activeCollectionId = newId;
    saveToStorage();
}

// --- DOSYA YÖNETİMİ (SEKMELER) ---
function renderFileTabs() {
    fileTabsContainer.innerHTML = '';
    
    if (collections.length === 0) createDefaultCollection();

    collections.forEach(col => {
        const tab = document.createElement('div');
        tab.className = `file-tab ${col.id === activeCollectionId ? 'active' : ''}`;
        
        // Dosya adı
        const nameSpan = document.createElement('span');
        nameSpan.innerText = col.name;
        nameSpan.onclick = () => switchCollection(col.id); // Tıklayınca geçiş yap
        
        // Silme butonu
        const delBtn = document.createElement('span');
        delBtn.className = 'delete-file-btn';
        delBtn.innerHTML = '&times;';
        delBtn.onclick = (e) => {
            e.stopPropagation(); // Tıklama yukarı gitmesin
            deleteCollection(col.id);
        };

        tab.appendChild(nameSpan);
        tab.appendChild(delBtn);
        fileTabsContainer.appendChild(tab);
    });
}

function switchCollection(id) {
    activeCollectionId = id;
    resultContainer.classList.add('hidden'); // Sonuç ekranını gizle
    winnerName.innerText = "???";
    saveToStorage();
    renderFileTabs(); // Aktif rengini güncellemek için
    updateListUI();   // Aşağıdaki listeyi güncellemek için
}

function deleteCollection(id) {
    if (collections.length <= 1) {
        alert("En az bir liste kalmalıdır!");
        return;
    }
    if (confirm("Bu dosyayı ve içindeki listeyi silmek istediğine emin misin?")) {
        collections = collections.filter(c => c.id !== id);
        // Eğer sildiğimiz dosya aktifse, başkasına geç
        if (id === activeCollectionId) {
            activeCollectionId = collections[0].id;
        }
        saveToStorage();
        renderFileTabs();
        updateListUI();
    }
}

// --- LİSTE GÖRÜNTÜLEME (İLLÜZYONLU) ---
function updateListUI() {
    participantListUI.innerHTML = '';
    
    // Aktif koleksiyonu bul
    const activeCol = collections.find(c => c.id === activeCollectionId);
    if (!activeCol) return;

    activeCol.list.forEach((name, index) => {
        const li = document.createElement('li');
        // Renk değişimi yok, hepsi normal görünüyor
        li.innerHTML = `${name} <span onclick="removeParticipant(${index})">&times;</span>`;
        participantListUI.appendChild(li);
    });
    
    countSpan.innerText = activeCol.list.length;
}

// --- İŞLEMLER (EKLEME / SİLME) ---
function addParticipant() {
    const name = participantInput.value.trim();
    const activeCol = collections.find(c => c.id === activeCollectionId);
    
    if (name && activeCol) {
        if (!activeCol.list.includes(name)) {
            activeCol.list.push(name);
            participantInput.value = '';
            updateListUI();
            saveToStorage();
        } else {
            alert("Bu isim zaten listede var!");
        }
    }
}

window.removeParticipant = function(index) {
    const activeCol = collections.find(c => c.id === activeCollectionId);
    if (activeCol) {
        const nameToDelete = activeCol.list[index];
        activeCol.list.splice(index, 1);
        
        // Gizli listeden de sil (drawn)
        const drawnIndex = activeCol.drawn.indexOf(nameToDelete);
        if(drawnIndex > -1) activeCol.drawn.splice(drawnIndex, 1);
        
        updateListUI();
        saveToStorage();
    }
};

// --- DOSYA YÜKLEME (YENİ DOSYA OLUŞTURMA) ---
fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        const names = text.split(/\r?\n/).map(n => n.trim()).filter(n => n.length > 0);
        
        // Yeni bir koleksiyon oluştur
        const newCollection = {
            id: Date.now(),
            name: file.name, // Dosya adı (örn: 12-A.txt)
            list: names,
            drawn: [] // Her dosyanın kendi çekilenler listesi var
        };
        
        collections.push(newCollection);
        switchCollection(newCollection.id); // Yeni yüklenene otomatik geç
        
        alert(`${file.name} başarıyla yüklendi!`);
        fileInput.value = ''; 
    };
    reader.readAsText(file);
});

// --- KURA ÇEKME (AKTİF DOSYADAN) ---
drawBtn.addEventListener('click', () => {
    const activeCol = collections.find(c => c.id === activeCollectionId);
    if (!activeCol) return;

    // Sadece bu dosyanın "drawn" listesinde olmayanlar
    const availableCandidates = activeCol.list.filter(p => !activeCol.drawn.includes(p));

    if (availableCandidates.length === 0) {
        alert("Sıfırlamak için butonu kullanın.");
        return;
    }

    // Animasyon (Listede herkes döner - İllüzyon)
    let counter = 0;
    const interval = setInterval(() => {
        const randomIndex = Math.floor(Math.random() * activeCol.list.length);
        winnerName.innerText = activeCol.list[randomIndex];
        counter++;

        if (counter > 20) { 
            clearInterval(interval);
            finalizeDraw(activeCol, availableCandidates); 
        }
    }, 100);
});

function finalizeDraw(activeCol, availableCandidates) {
    const winningIndex = Math.floor(Math.random() * availableCandidates.length);
    const winner = availableCandidates[winningIndex];

    winnerName.innerText = `🎉 ${winner} 🎉`;
    resultContainer.classList.remove('hidden');

    // Sadece bu dosyanın gizli listesine ekle
    activeCol.drawn.push(winner);
    saveToStorage();
}

// --- SIFIRLAMA (SADECE AKTİF LİSTEYİ) ---
clearBtn.innerText = "Bu Listeyi Sıfırla (Kura Geçmişi)";
clearBtn.addEventListener('click', () => {
    const activeCol = collections.find(c => c.id === activeCollectionId);
    
    if (confirm(`"${activeCol.name}" için kura geçmişi silinecek.  Emin misiniz?`)) {
        activeCol.drawn = []; // Sadece bu dosyanın geçmişini sil
        resultContainer.classList.add('hidden');
        winnerName.innerText = '???';
        saveToStorage();
        alert("Liste sıfırlandı.");
    }
});

// Enter tuşu ve Başlangıç
participantInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') addParticipant(); });
addBtn.addEventListener('click', addParticipant);
document.addEventListener('DOMContentLoaded', loadFromStorage);