# SafeBox Code Analysis & Fixes (v1.7.6)

## ✅ DÜZELTİLDİ — İzolasyon ve Dürüstlük Güncellemesi (Kullanıcı Bildirimleri)

### 1. Ağ İzolasyonu (NET Argümanı)
**Çözüm:** `--unshare-all` yerine spesifik namespace komutları eklendi. `NET=1` ise host ağı paylaşılır (`--share-net` muadili), `NET=0` ise `--unshare-net` eklenerek tam izole edilir.

### 2. /dev ve Donanım İzolasyonu Açıklamaları
**Çözüm:** Uygulamanın VM (Sanal Makine) olmadığı, konteyner olduğu açıkça belgelendi. `/dev/dri` pass-through nedeniyle izolasyon sınırları dürüstçe belirtildi.

### 3. Doctor Testi
**Çözüm:** GUI içindeki `doctor` komutu sahte namespace count testlerini bıraktı. Artık şunları ölçüyor:
1. RootFS varlığı ve bütünlüğü.
2. Arka planda aktif `safebox-core` process'i.
3. Çalışan süreçler için cgroup v2 (`MemoryMax`, `CPUQuota`) sınırlarının durumu.

### 4. Clipboard Kaldırılması
**Çözüm:** Çalışmayan ve fail-closed durumda olan clipboard kodu, argümanı ve UI butonu kaldırıldı.

### 5. RootFS Otomatik Kurulum (Exit 105)
**Çözüm:** `safebox-core` başlatılırken RootFS yoksa `exit 105` döner. `safebox_gui.py` bu kodu yakalar ve kullanıcıya "Kurulum başlasın mı?" diye sorup `pkexec safebox-setup` tetikler.

### 6. CPU ve RAM Terminolojisi
**Çözüm:** "Sanal RAM" yerine "RAM Sınırı (Cgroup v2)" gibi gerçeği yansıtan terminoloji kullanıldı.

### 7. README ve Dokümantasyon
**Çözüm:** README dosyası baştan yazılarak iddialar gerçekçi seviyelere çekildi. Loglama kalıntıları ve sistem mimarisi şeffaf bir şekilde eklendi.
