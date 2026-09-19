# 🛡️ SafeBox - İzole Konteyner Masaüstü (Cinnamon)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04%20LTS-orange.svg)](https://ubuntu.com/)
[![Release](https://img.shields.io/badge/Release-v1.7.6-brightgreen.svg)](https://github.com/winexee/safebox/releases)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Bash](https://img.shields.io/badge/Bash-5.0+-red.svg)](https://www.gnu.org/software/bash/)

SafeBox, Linux üzerinde şüpheli dosyaları incelemek, güvenli ortamda gezinmek ve ana sistem dosya yapısını korumak için geliştirilmiş, **Bubblewrap** tabanlı bir **konteyner (namespace)** sanal alanıdır.

> ⚠️ **UYARI - İzolasyon Sınırları:** SafeBox bir "Sanal Makine (VM)" DEĞİLDİR. Tam donanım izolasyonu sağlamaz. Çekirdeği (Kernel) ana sistemle paylaşır. Grafik performansı için `/dev/dri` ve NVIDIA cihazları sandbox içine aktarılır. Bu nedenle izolasyon düzeyi standart bir konteyner sınırları içindedir.

---

## ✨ Temel Özellikler

### 🔒 Güvenlik & Konteyner İzolasyonu
* **Namespace İzolasyonu:** Bubblewrap ile User, PID, UTS, IPC ve Mount namespace'leri ayrılır.
* **Sınırlandırılmış Kaynaklar:** Cgroup v2 ile maksimum CPU ve RAM kullanım limiti koyulur.
* **Ağ İzolasyonu:** İstendiğinde ağ namespace'i tamamen koparılır (Air-gapped) veya host interneti doğrudan paylaşılır.
* **Sistem Dosyası Koruma:** Host sistem dosyaları sandbox'a bağlanmaz. Kendi izole `debootstrap` rootfs'i kullanılır.

### 🖥️ Kullanıcı Deneyimi
* **Cinnamon Masaüstü:** Sade, anlaşılır ve bilindik masaüstü arayüzü.
* **Pratik Otomatik Kurulum:** Tek tuşla `safebox-setup` tetiklenerek gerekli RootFS hazırlanır.
* **GTK3 Kontrol Merkezi:** RAM limiti, işlemci limiti ve ağ erişimi gibi temel izinleri yönetin.

### 📦 Standart İçerik (RootFS)
* **Firefox:** Web tarayıcısı
* **Nemo:** Dosya yöneticisi
* **GNOME Terminal:** Komut satırı
* **Xed:** Metin düzenleyici
* **GNOME System Monitor:** Kaynak takibi

---

## 🚀 Kurulum

### 1. Bağımlılıkların Kurulması

```bash
sudo apt update
sudo apt install bubblewrap xserver-xephyr dbus-x11 python3 python3-gi gir1.2-gtk-3.0 debootstrap policykit-1
```

### 2. Projenin Kurulması

```bash
git clone https://github.com/winexee/safebox.git
cd safebox
sudo cp usr/bin/safebox-core /usr/bin/
sudo cp usr/bin/safebox-setup /usr/bin/
sudo cp -r usr/share/safebox /usr/share/
sudo cp usr/bin/safebox /usr/bin/
```

### 3. RootFS Hazırlanması (Önemli!)

SafeBox'ın çalışabilmesi için izole dosya sisteminin oluşturulması gerekir:

```bash
sudo safebox-setup
```
*(Bu işlem internet hızınıza bağlı olarak birkaç dakika sürebilir. Cinnamon tabanlı minimal bir Ubuntu sistemi `/var/lib/safebox/rootfs` dizinine kurulur.)*

---

## 💻 Kullanım

Uygulamayı başlatmak için terminale yazın:

```bash
safebox
```

### Kontrol Merkezi Ayarları

| Ayar | Açıklama |
|---------|----------|
| **RAM Sınırı** | Cgroup v2 kullanılarak SafeBox süreçlerinin tüketebileceği maksimum RAM miktarı belirlenir. |
| **CPU Sınırı** | Cgroup v2 kullanılarak işlemci kullanım kotası belirlenir. (Gerçek sanal çekirdek oluşturmaz, sadece kullanım oranını sınırlar) |
| **İnternet ve Ağ** | Açık: Host ağını kullanır. Kapalı: Ağ namespace'ini izole eder (İnternet kesilir). |
| **Paylaşım** | `~/SafeBox-Paylasim` klasörü sandbox içerisine bağlanır. Çift yönlü dosya aktarımı için kullanılır. |

### Sistem Testi (Doctor)

Konsol sekmesinden "doctor" komutunu çalıştırdığınızda şu gerçek zamanlı kontroller yapılır:
1. RootFS'in düzgün kurulup kurulmadığı.
2. Arka planda aktif bir SafeBox sürecinin olup olmadığı.
3. Cgroup v2 bellek ve işlemci kısıtlamalarının başarıyla uygulanıp uygulanmadığı.

---

## 🛡️ Güvenlik Mimarisi ve Sınırlar

- **Loglama:** SafeBox içindeki işlemler RAM'de tutulur, ancak başlangıç ve hatalara ait süreç logları (engine log) ana sisteminizde `~/.local/share/safebox/` altında saklanır.
- **RootFS (Dosya Sistemi):** Kendi özel RootFS'i olduğu için ana sisteminizdeki kişisel dosyalarınıza (`/home`) ve sistem yapılandırmalarınıza (`/etc`, `/usr`) erişim yoktur.
- **GPU Erişimi:** Performanslı bir masaüstü deneyimi sunmak için `/dev/dri` düğümleri içeri aktarılır. Bu durum GPU tabanlı kaçış (escape) açıklarına karşı risk oluşturabilir. Tam güvenlik isteniyorsa kaynak koddan `dev-bind` kısımları çıkarılmalıdır.
- **İç İçe Sandbox (Nested):** Güvenlik gereği SafeBox içerisinden tekrar SafeBox veya farklı bir sandbox çalıştırılması engellenmiştir.

---

## 📞 Destek ve Lisans

Bu proje **MIT Lisansı** altında yayınlanmıştır.
Geliştirici: Mehmet Akif Şahin (winexee)

Bug raporları ve iletişim için: [GitHub Issues](https://github.com/winexee/safebox/issues)
