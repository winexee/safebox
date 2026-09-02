# 🛡️ SafeBox - Linux Güvenli ve İzole Sanal Masaüstü

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04%20LTS-orange.svg)](https://ubuntu.com/)
[![Release](https://img.shields.io/badge/Release-v1.7.5-brightgreen.svg)](https://github.com/winexee/safebox/releases)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Bash](https://img.shields.io/badge/Bash-5.0+-red.svg)](https://www.gnu.org/software/bash/)

SafeBox, Linux üzerinde güvenilmeyen dosyaları çalıştırmak, güvenli web gezintisi yapmak ve sistemi kalıntılardan korumak için **Bubblewrap** altyapısını kullanan hafif, izole bir **MATE** sanal masaüstü ortamıdır. Tam sistem izolasyonu, donanım hızlandırması ve sıfır kalıntı garantisi sunar.

---

## ✨ Temel Özellikler

### 🔒 Güvenlik & İzolasyon
* **Tam Sistem İzolasyonu:** Bubblewrap ile User/PID/UTS/IPC/Mount namespaces
* **Çekirdek İzolasyonu:** Linux cgroup v2 ile RAM ve CPU kısıtlaması
* **Kimlik Yalıtımı:** Statik passwd/group/shadow ve sahte machine-id
* **Sıfır Kalıntı:** Tüm veriler oturum sonunda RAM'den silinir
* **Sistem Bütünlüğü:** Sistem dosyaları read-only bağlanır

### 🖥️ Kullanıcı Deneyimi
* **Modern MATE Arayüzü:** Yaru teması ile optimize edilmiş modern masaüstü
* **Hafif & Hızlı:** Minimal bileşenlerle düşük sistem kullanımı
* **Kontrol Merkezi:** GTK3 GUI ile kolay konfigürasyon ve izleme

### ⚡ Performans & Donanım
* **Donanım Hızlandırma:** NVIDIA/DRI desteği ile tam 3D grafik
* **Ses Desteği:** PulseAudio ve PipeWire entegrasyonu
* **Paylaşılan Klasör:** Güvenli dosya aktarımı (~/SafeBox-Paylasim)
* **Yapılandırılabilir Kaynaklar:** RAM (1-16GB) ve CPU çekirdekleri

### 📦 Standart Araçlar
* **Firefox:** Güvenli web tarayıcısı
* **Caja:** Dosya yöneticisi
* **MATE Terminal:** Komut satırı
* **Eye of MATE:** Resim görüntüleyici
* **Video Oynatıcı:** Multimedya desteği (Celluloid/Totem/VLC)

---

## 🚀 Kurulum

### Yöntem 1: PPA (Ubuntu/Debian - Önerilen)

```bash
sudo add-apt-repository ppa:mehmetakifsahin500/safebox -y
sudo apt update
sudo apt install safebox -y
```

### Yöntem 2: Direct .deb Paketi

```bash
# Releases sayfasından v1.7.5+ indirin
sudo apt install ./safebox_*.deb
```

### Yöntem 3: Manuel Kurulum (Geliştirici)

```bash
git clone https://github.com/winexee/safebox.git
cd safebox
sudo cp usr/bin/safebox-core /usr/bin/
sudo cp usr/share/safebox/* /usr/share/safebox/
sudo cp usr/bin/safebox /usr/bin/
```

---

## 💻 Kullanım

### Başlangıç

```bash
safebox
```

veya uygulama menüsünden "SafeBox Kontrol Merkezi" arayın.

### Kontrol Merkezi Seçenekleri

| Seçenek | Aralık | Açıklama |
|---------|--------|----------|
| **RAM** | 1-16 GB | Sanal alana tahsis edilecek bellek |
| **CPU** | 1-N | Sanal alana tahsis edilecek çekirdek sayısı |
| **Ekran** | 1024x768-1920x1080 | Xephyr pencere çözünürlüğü |
| **Paylaşım** | On/Off | ~/SafeBox-Paylasim klasörü bağlama |
| **Ses** | On/Off | PulseAudio/PipeWire desteği |
| **İnternet** | On/Off | Ağ erişimi (Off = Air-gapped) |

### Konsolda Komutlar

Kontrol Merkezi konsoluna girin:

```
developer       # Geliştirici modu aç/kapat
doctor          # İzolasyon bütünlüğünü test et
sysinfo         # Sistem bilgisi göster
sysinfo         # SafeBox sürümü ve durum
purge           # Önbellek ve mock dosyalarını temizle
clear           # Konsolu temizle
```

---

## 🔧 Gereksinimler

### Minimum Sistem
- Ubuntu 24.04 LTS veya Debian 12+
- RAM: 2GB + (SafeBox için 1-16GB konfigüre edilir)
- CPU: 2 çekirdek (önerilir: 4+)
- Disk: 100MB

### Gerekli Paketler
```bash
sudo apt install \
    bubblewrap \
    xephyr \
    mate-desktop-environment \
    libgtk-3-0 \
    python3 \
    dbus-run-session
```

### Opsiyonel
- NVIDIA GPU: nvidia-container-runtime
- PulseAudio/PipeWire: Ses desteği

---

## 📋 Sürüm Geçmişi

### v1.7.5 (İŞLEMDE) - **Kritik Güvenlik & Stabilite Güncellemesi**
- ✅ **XDG_RUNTIME_DIR** tanımlanmamış sorunu çözüldü (Ses crash fix)
- ✅ Güvenlik açığı kapatıldı (shell=False, shlex.split)
- ✅ Subprocess timeout eklendi (10s)
- ✅ CPU cores validation (host cores > requested)
- ✅ Xephyr robust timeout polling (10s)
- ✅ X11 socket cleanup
- ✅ cgroup v2 RAM/CPU sınırlandırması
- ✅ Logging setup (file + console)
- ✅ Input validation & error handling
- ⚠️ **ÖNEMLİ:** v1.7.4'ten upgrade etmeden önce `.old` yedekleme yapın

### v1.7.4 - Cinnamon 2D & UI Restoration
- Cinnamon 2D oturumu entegre edildi
- 133 başlatma çökmesi giderildi
- GUI orijinal v1.6.4 tasarımına döndürüldü
- Fallback masaüstü desteği (xfwm4/tint2)

### v1.2.3 - Diagnostics Console
- Teşhis konsolu entegrasyonu
- GTK karakter düzeltmeleri
- Winexe yayıncı optimizasyonu

### v1.2.0 - İlk Çıkış
- MATE masaüstü desteği
- Bubblewrap izolasyonu
- 5 temel uygulama

---

## 🛡️ Güvenlik Mimarisi

### İzolasyon Katmanları

```
┌─────────────────────────────────────────────────────┐
│            Ana Linux Sistemi                        │
├──────────────────────────────────────────────────────┤
│ Bubblewrap (Namespace İzolasyonu)                   │
│  ├─ User Namespace (UID 1000 → 0)                  │
│  ├─ PID Namespace (init=guest-init)                │
│  ├─ UTS Namespace (hostname=safebox-sandbox)       │
│  ├─ IPC Namespace (sıralar izole)                  │
│  ├─ Mount Namespace (özel /proc, /sys, /etc)      │
│  └─ Network Namespace (--share-net veya --unshare) │
├──────────────────────────────────────────────────────┤
│ cgroup v2 (Kaynak Sınırlandırması)                 │
│  ├─ MemoryMax: 1-16 GB                             │
│  └─ CPUQuota: taskset affinity                     │
├──────────────────────────────────────────────────────┤
│ Xephyr (Sanal X Sunucusu)                          │
│  └─ X11 display: :10-:99 (dynamic)                │
├──────────────────────────────────────────────────────┤
│ MATE Masaüstü (Sandboxed)                          │
│  ├─ Cinnamon 2D (software rendering)              │
│  ├─ Marco (window manager)                         │
│  ├─ Mate-panel (panel)                            │
│  └─ Caja (file manager)                           │
└─────────────────────────────────────────────────────┘
```

### Dosya Sistemi Mimarisi

- `/etc` → Mock (passwd/group/machine-id)
- `/proc` → Mock (meminfo/cpuinfo/stat)
- `/sys` → tmpfs (safe)
- `/home/safebox` → tmpfs (RAM)
- `/tmp` → tmpfs (RAM)
- `/run` → tmpfs (RAM)
- `/usr`, `/lib`, `/bin` → Read-only bind
- `~/SafeBox-Paylasim` → Payload klasörü (optional)

---

## 🔍 Mimari Detaylar

### Başlangıç Akışı

1. **GUI Başlatma** (`safebox_gui.py`)
   - Kontrol Merkezi başlar (v1.7.5+)
   - Kaynak parametreleri alınır
   - Input validation yapılır

2. **Engine Başlatma** (`safebox-core`)
   - XDG_RUNTIME_DIR otomatik belirlenir
   - Display bulunur (:10-:99)
   - Xephyr başlatılır (10s timeout)
   - Mock dosyaları hazırlanır

3. **Bubblewrap Yapılandırması**
   - Namespace'ler kurulur
   - cgroup v2 sınırlandırmaları uygulanır
   - Sesli destek (pulse/pipewire)
   - Network (shared/isolated)

4. **Guest Oturumu** (`guest-init`)
   - Cinnamon 2D başlatılır
   - Desktop kısayolları kurulur
   - Dbus oturumu başlatılır

5. **Kapanış**
   - Xephyr sonlandırılır
   - RAM diskleri silinir
   - X11 soketleri temizlenir
   - Logs saklanır

---

## 🐛 Bilinen Sorunlar & Çözümleri

| Sorun | Çözüm | v1.7.5'te |
|-------|-------|-----------|
| Ses çalışmadı | XDG_RUNTIME_DIR tanımlanacak | ✅ Fixed |
| UI freeze | Subprocess timeout eklendi | ✅ Fixed |
| Hata mesajları | Logging setup | ✅ Fixed |
| CPU mismatch | Core validation | ✅ Fixed |
| Xephyr timeout | Robust polling | ✅ Fixed |
| X11 socket leak | Cleanup improved | ✅ Fixed |

---

## 📊 Sistem Performansı

### Tipik Kaynak Kullanımı

```
Konfigürasyon: 4GB RAM, 4 CPU
─────────────────────────────
Başlangıç:      ~200MB RAM, 15% CPU
Firefox açık:   ~800MB RAM, 25% CPU
İdle:           ~300MB RAM, 5% CPU
Kapanış:        0MB (tam cleanup)
```

---

## 🔐 Güvenlik Notları

### ✅ Desteklenen Tehdit Modelleri
- Güvenilmeyen web uygulamaları
- Şüpheli dosya indirmeleri
- Zararlı tarayıcı eklentileri
- Sistem dosyaları izolasyonu

### ❌ Desteklenmeyen Tehdit Modelleri
- Kernel exploits (AppArmor/SELinux tarafından koruma önerilir)
- CPU side-channel attacks (Spectre/Meltdown)
- Host sistem tamamen kötü niyetli
- Kernel 5.1 altı versiyonlar (eski cgroup yapısı)

### 🛡️ En İyi Uygulamalar
```bash
# 1. Düzenli update
sudo apt update && sudo apt upgrade -y

# 2. Kernel güncel tut
uname -r  # 5.10+

# 3. AppArmor/SELinux etkinleştir
sudo aa-status    # AppArmor
sudo getenforce   # SELinux

# 4. Dosyaları paylaşmadan temizle
rm -rf ~/SafeBox-Paylasim/*

# 5. Logları kontrol et
tail -f ~/.local/share/safebox/safebox-engine.log
```

---

## 🤝 Katkı

SafeBox geliştirmeye katkıda bulunmak isterseniz:

1. **Fork** yapın
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. **Commit** edin (`git commit -m 'Add: Amazing feature'`)
4. **Push** edin (`git push origin feature/amazing-feature`)
5. **Pull Request** açın

### Geliştirme Ortamı

```bash
# Klonla
git clone https://github.com/yourusername/safebox.git
cd safebox

# Kodu test et
python3 -m py_compile usr/share/safebox/safebox_gui.py
bash -n usr/bin/safebox-core

# Linting
pylint usr/share/safebox/safebox_gui.py
shellcheck usr/bin/safebox-core
```

---

## 📞 Destek & İletişim

- **Issues**: [GitHub Issues](https://github.com/winexee/safebox/issues)
- **Email**: mehmetakifsahin500@gmail.com
- **PPA Updates**: ppa:mehmetakifsahin500/safebox

---

## 📜 Lisans

Bu proje **MIT Lisansı** altında yayınlanmıştır.

```
MIT License

Copyright (c) 2026 Mehmet Akif Şahin (winexee)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

Detaylar için [LICENSE](LICENSE) dosyasını okuyun.

---

## 👨‍💻 Geliştirici

**Mehmet Akif Şahin (winexee)**
- GitHub: [@winexee](https://github.com/winexee)
- Email: mehmetakifsahin500@gmail.com
- Location: 🇹🇷 Turkey

---

## 🎯 Yol Haritası (Planlanan)

### v1.8 (Q4 2026)
- [ ] AppArmor profili
- [ ] SELinux policy
- [ ] Clipboard proxy
- [ ] VPN integration

### v2.0 (2027)
- [ ] Wayland support
- [ ] Multi-monitor
- [ ] GPU isolation
- [ ] Network namespaces

---

## 📚 Referanslar

- [Bubblewrap Documentation](https://github.com/containers/bubblewrap)
- [Linux Namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [cgroups v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [Xephyr Guide](https://www.x.org/wiki/Events/XDC2014/XDC2014-Xephyr/)

---

## 📖 Changelog Detaylı

Detaylı changelog için: [CHANGELOG.md](CHANGELOG.md) (yakında)

Bug raporları ve feature requests için: [Issues](https://github.com/winexee/safebox/issues)

---

**Son Güncelleme:** 2 Eylül 2026  
**v1.7.5** (Beta) - Kritik güvenlik düzeltmeleri uygulanmıştır
