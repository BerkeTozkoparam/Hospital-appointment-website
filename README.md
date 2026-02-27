# 🏥 Hastane Randevu Sistemi

Python Flask ve SQLite ile geliştirilmiş, tarayıcı tabanlı hastane randevu yönetim sistemi.

---

## Özellikler

- **Hasta Yönetimi** — Hasta ekleme, listeleme, arama (ad/soyad/TC) ve silme
- **Doktor Yönetimi** — Doktor ekleme, listeleme ve silme
- **Randevu Yönetimi** — Randevu alma, listeleme, filtreleme, iptal etme ve silme
- **Modern Arayüz** — Bootstrap 5 ile responsive tasarım, modal formlar
- **Anlık Bildirimler** — İşlem sonuçları için flash mesajları

---

## Kurulum

### Gereksinimler
- Python 3.8+
- pip

### Adımlar

```bash
# 1. Depoyu klonlayın
git clone https://github.com/Ecemestanogluu/hastane-randevu.git
cd hastane-randevu

# 2. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 3. Uygulamayı başlatın
python app.py
```

Tarayıcıda açın: **http://localhost:5000**

---

## Proje Yapısı

```
hastane_web/
├── app.py                  # Flask uygulaması, rotalar, veritabanı
├── requirements.txt        # Python bağımlılıkları
├── hastane.db              # SQLite veritabanı (otomatik oluşur)
└── templates/
    ├── base.html           # Ortak layout, navbar
    ├── index.html          # Ana sayfa
    ├── hastalar.html       # Hasta yönetimi
    ├── doktorlar.html      # Doktor yönetimi
    └── randevular.html     # Randevu yönetimi
```

---

## Ekran Görüntüleri

| Sayfa | Açıklama |
|-------|----------|
| Ana Sayfa | İstatistik kartları ve son randevular |
| Hastalar | Liste, arama ve hasta ekleme formu |
| Doktorlar | Liste ve doktor ekleme formu |
| Randevular | Liste, hasta/durum filtresi, randevu alma |

---

## Teknolojiler

- **Backend:** Python, Flask
- **Veritabanı:** SQLite (sqlite3)
- **Frontend:** HTML5, Bootstrap 5, Bootstrap Icons
- **Şablon Motoru:** Jinja2

---

## Terminal Versiyonu (C)

Projenin `hastane_randevu.c` dosyasında ncurses tabanlı terminal arayüzü de mevcuttur.

```bash
gcc -o hastane_randevu hastane_randevu.c -lncurses
./hastane_randevu
```
