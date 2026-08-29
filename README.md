# 🛡️ SafeBox - Linux Güvenli ve İzole Sanal Masaüstü

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04%20LTS-orange.svg)](https://ubuntu.com/)
[![Release](https://img.shields.io/badge/Release-v1.2.3-blue.svg)](https://github.com/winexee/safebox/releases)

SafeBox, Linux üzerinde güvenilmeyen dosyaları çalıştırmak, güvenli web gezintisi yapmak ve sistemi kalıntılardan korumak için Bubblewrap altyapısını kullanan hafif, izole bir MATE sanal masaüstüdür.

---

## ✨ Temel Özellikler

* 🔒 **Tam Sistem İzolasyonu:** Ana ev dizini gizlenir; Linux çekirdek ad alanları (namespaces) ile izole bir profil atanır.
* 🖥️ **Hafif MATE Masaüstü:** Yaru teması ile optimize edilmiş, modern ve sade masaüstü deneyimi.
* ⚡ **Geçici RAM Alanı:** Oturum kapandığında indirilen tüm veriler ve geçici dosyalar RAM'den kalıntısız silinir.
* 🎮 **Donanım Hızlandırma:** NVIDIA ve DRI soket köprüleri ile 3D grafik performansı.
* 🛠️ **Dahili Teşhis Konsolu:** Güvenlik loglarını anlık izleme, komut koşturma ve paket sorgulama arayüzü.
* 📦 **Sadeleştirilmiş Araçlar:** Yalnızca 5 temel uygulama (Firefox, Caja, MATE Terminal, EOM ve Video Oynatıcı).

---

## 🚀 Kurulum

### Yöntem 1: Resmi Launchpad PPA (Önerilen)

\`\`\`bash
sudo add-apt-repository ppa:mehmetakifsahin500/safebox -y
sudo apt update
sudo apt install safebox -y
\`\`\`

### Yöntem 2: Doğrudan .deb Paketi İle

Releases sayfasından en son sürümü indirin ve kurun:

\`\`\`bash
sudo apt install ./safebox_1.2.3-1~ppa1~noble1_all.deb
\`\`\`

---

## 💻 Kullanım

Uygulama menüsünden SafeBox Kontrol Merkezi'ni açabilir veya doğrudan uçbirimden başlatabilirsiniz:

\`\`\`bash
safebox
\`\`\`

### Kontrol Merkezi Seçenekleri

| Seçenek | Açıklama |
|---------|----------|
| **RAM Sınırı** | 1-16 GB arası (varsayılan: 4 GB) |
| **CPU Çekirdekleri** | İzole işlem başına kullanılabilir thread sayısı |
| **Ekran Çözünürlüğü** | 1280x720 → 1920x1080 arası |
| **Paylaşılan Klasör** | ~/SafeBox-Paylasim ana sisteme bağlanır |
| **Ses Desteği** | PulseAudio / PipeWire entegrasyonu |
| **İnternet Erişimi** | Air-gapped (izole) veya normal ağ |

---

## 📋 Sürüm Geçmişi

* **v1.2.3**: Dahili teşhis konsolu, GTK karakter düzeltmeleri ve Winexe yayıncı optimizasyonu.
* **v1.2.2**: Gelişmiş hata yönetimi, dinamik RAM temizleme (trap cleanup) ve Xephyr soket doğrulaması.
* **v1.2.1**: Alt süreç hata kontrolleri ve log kilit güvenlikleri.
* **v1.2.0**: MATE masaüstü geçişi ve bağımsız uygulama yalıtımı.

---

## 🔧 Gereksinimler

- Ubuntu 24.04 LTS veya Debian 12+
- Bubblewrap (bwrap)
- MATE masaüstü bileşenleri
- Xephyr (sanal X sunucusu)
- Python 3.8+

---

## 📜 Lisans

Bu proje **MIT Lisansı** ile lisanslanmıştır. Bkz: [LICENSE](LICENSE)

---

## 👨‍💻 Geliştirici

**Mehmet Akif Şahin** (winexee)  
📧 mehmetakifsahin500@gmail.com

---

## 🤝 Katkı

Katkılarınız hoştur! Fork → Branch → PR yapabilirsiniz.

