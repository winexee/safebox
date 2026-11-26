# 🛡️ SafeBox - İzole Konteyner Masaüstü (Cinnamon)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04%20LTS-orange.svg)](https://ubuntu.com/)
[![Release](https://img.shields.io/badge/Release-v1.7.30-brightgreen.svg)](https://github.com/winexee/safebox/releases)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Bash](https://img.shields.io/badge/Bash-5.0+-red.svg)](https://www.gnu.org/software/bash/)
[![safebox](https://snapcraft.io/safebox/badge.svg)](https://snapcraft.io/safebox)

🌐 **[English Documentation (README.en.md)](README.en.md)** | 🏗️ **[Mimari ve Geliştirici Rehberi (docs/ARCHITECTURE.md)](docs/ARCHITECTURE.md)**

SafeBox, Linux üzerinde şüpheli dosyaları incelemek, güvenli ortamda gezinmek ve ana sistem dosya yapısını korumak için geliştirilmiş, **Bubblewrap** tabanlı bir **konteyner (namespace)** sanal alanıdır.

> ⚠️ **UYARI - İzolasyon Sınırları:** SafeBox bir "Sanal Makine (VM)" DEĞİLDİR. Tam donanım izolasyonu sağlamaz. Çekirdeği (Kernel) ana sistemle paylaşır. Grafik işleme kararlılığı ve izolasyon için donanım GPU düğümleri (`/dev/dri`, NVIDIA) aktarılmaz; Xephyr (`-nolisten tcp`) içinde yazılım tabanlı render (`CINNAMON_SOFTWARE_RENDERING=1`) kullanılır.

---

## ✨ Temel Özellikler

### 🔒 Güvenlik & Konteyner İzolasyonu
* **Namespace İzolasyonu:** Bubblewrap ile User, PID, UTS, IPC ve Mount namespace'leri ayrılır.
* **Seccomp BPF Koruması:** `seccomp_filter.py` tarafından üretilen cBPF filtresi varsayılan olarak aktiftir; `unshare`, `setns`, `mount`, `bpf`, `userfaultfd`, `io_uring_*`, `kexec_load`, `keyctl` ve `ptrace` gibi tehlikeli çekirdek çağrılarını `-EPERM` ile engeller.
* **Sınırlandırılmış Kaynaklar:** Cgroup v2 (`systemd-run --user --scope`) ile maksimum CPU ve RAM kullanım limiti fail-closed olarak uygulanır.
* **Ağ İzolasyonu:** İstendiğinde ağ namespace'i tamamen koparılır (Air-gapped) veya host interneti paylaşılır.
* **Sistem Dosyası Koruma:** Host sistem dosyaları sandbox'a bağlanmaz. Kendi izole `debootstrap` rootfs'i salt-okunur bağlanır; yazılabilir alanlar RAM (`tmpfs`) üzerindedir.

### 🖥️ Kullanıcı Deneyimi
* **Cinnamon Masaüstü:** Sade, anlaşılır ve bilindik masaüstü arayüzü (Cinnamon 2D yazılım render modu).
* **Pratik Otomatik Kurulum:** Tek tuşla `safebox-setup` tetiklenerek gerekli RootFS atomik olarak hazırlanır.
* **GTK3 Kontrol Merkezi:** RAM limiti, işlemci limiti, Seccomp, ağ ve paylaşım izinlerini yönetin.

### 📦 Standart İçerik (RootFS)
* **Epiphany:** Web tarayıcısı
* **Nemo:** Dosya yöneticisi
* **GNOME Terminal:** Komut satırı
* **Gedit:** Metin düzenleyici
* **GNOME System Monitor:** Kaynak takibi

---

## 🚀 Kurulum

### 1. Bağımlılıkların Kurulması

```bash
sudo apt update
sudo apt install bubblewrap libseccomp2 xserver-xephyr dbus-x11 python3 python3-gi gir1.2-gtk-3.0 debootstrap pkexec x11-utils
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
| **RAM Sınırı** | Cgroup v2 (`MemoryMax`) kullanılarak SafeBox süreçlerinin tüketebileceği maksimum RAM miktarı belirlenir. |
| **CPU Sınırı** | Cgroup v2 (`CPUQuota`) ve `taskset` ile işlemci kullanım kotası belirlenir. |
| **Seccomp BPF** | Varsayılan açıktır; yüksek riskli çekirdek, mount ve iç içe namespace sistem çağrılarını engeller. |
| **İnternet ve Ağ** | Açık: Host ağını kullanır. Kapalı: Ağ namespace'ini izole eder (İnternet kesilir). |
| **Paylaşım** | `~/SafeBox-Paylasim` klasörü sandbox içerisine çift yönlü bağlanır. |

### Sistem Testi (Test & Otomatik Testler)

GUI içindeki Konsol sekmesinden önce `developer` komutunu girerek Geliştirici Modunu açıp ardından `test` veya `test ultra` komutunu çalıştırdığınızda şu gerçek zamanlı kontroller yapılır:
1. RootFS bütünlüğü ve çalışan SafeBox süreci.
2. Cgroup v2 (`MemoryMax`, `CPUQuota`) ve CPU affinity sınırları.
3. `test ultra` ile ek olarak namespace izolasyonu, `mountinfo`, `/dev` yalıtımı, UTS hostname, `NoNewPrivs=1` ve `Seccomp=2` durumu.

Yerel geliştirme sırasında otomatik birim ve seccomp test paketini çalıştırmak için:

```bash
python3 -m unittest discover -s tests -v
```

---

## 🛡️ Güvenlik Mimarisi ve İzolasyon Sınırları (Tavizler)

SafeBox, kullanım kolaylığı ve performans sağlamak amacıyla bazı katı sanallaştırma prensiplerinden bilinçli olarak taviz verir. Lütfen aşağıdaki güvenlik sınırlarını dikkate alın:

- **Çekirdek (Kernel) Paylaşımı:** Sistem ayrı bir çekirdek (VM) kullanmaz. `uname -r` host bilgisini gösterir. Ana sisteminizde çekirdek tabanlı (Kernel Exploit) bir zafiyet varsa SafeBox sizi koruyamaz.
- **Seccomp Filtrelemesi:** SafeBox artık varsayılan olarak bir Seccomp BPF denylist filtresi uygular (`unshare`, `setns`, `mount`, `bpf`, `userfaultfd`, `io_uring_*`, `kexec_load`, `keyctl`, `ptrace` vb. engellenir). Ancak bu bir denylist yaklaşımıdır; sıradan uygulama çağrıları açık bırakıldığı için tam VM/donanım yalıtımının yerini tutmaz.
- **Grafik / X11 Sınırı:** GPU aygıt düğümleri (`/dev/dri`, NVIDIA) aktarılmaz; host'un ana `:0` X11 soketi de paylaşılmaz. Bunun yerine `-nolisten tcp` ile başlatılan izole bir Xephyr sunucusu içinde yazılım tabanlı rendering kullanılır. Ancak Xephyr kendisi host X sunucusunun bir istemcisi olduğu için X11 protokol yüzeyi tamamen sıfır değildir.
- **Ses Soketleri:** Kullanıcı sesi açtığında (`Audio=1`), PulseAudio veya PipeWire soketi doğrudan ana sistemden bağlanır. İzole edilmemiş ses soketleri teknik olarak host mikrofona erişim veya ses dinleme riskine açıktır.
- **Loglama:** SafeBox içindeki dosya değişiklikleri RAM'de tutulur ve çıkışta silinir; ancak motor günlükleri ana sistemde `~/.local/share/safebox/safebox-engine.log` altında kalır.
- **İç İçe Sandbox (Nested):** `safebox-guest-blocker`, RootFS'te `bubblewrap` olmaması ve Seccomp BPF (`unshare`/`setns` engeli) ile iç içe sandbox oluşturma engellenmiştir.

---

## 📞 Destek ve Lisans

Bu proje **MIT Lisansı** altında yayınlanmıştır.
Geliştirici: Mehmet Akif Şahin (winexee)

Bug raporları ve iletişim için: [GitHub Issues](https://github.com/winexee/safebox/issues)

### Snap Confinement Notu
SafeBox Snap paketi olarak dağıtıldığında `confinement: classic` (klasik izolasyon) kullanır. Snap'in strict AppArmor/seccomp katmanı `bwrap`'ın namespace oluşturma ve `/var/lib/safebox/rootfs` erişim yeteneklerini engellediği için `classic` zorunludur. Gerçek izolasyon sınırı Snap tarafından değil, SafeBox'ın çalıştırdığı Bubblewrap, Cgroup v2 ve Seccomp BPF mimarisi tarafından sağlanmaktadır.
