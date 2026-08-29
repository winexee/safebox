# SafeBox - Linux GÃ¼venli ve Ä°zole Sanal MasaÃ¼stÃ¼

SafeBox, Linux Ã¼zerinde gÃ¼venilmeyen dosyalarÄ± Ã§alÄ±ÅŸtÄ±rmak, gÃ¼venli web gezintisi yapmak ve sistemi kalÄ±ntÄ±lardan korumakiÃ§in `bubblewrap` altyapÄ±sÄ±nÄ± kullanan hajif, izole bir MATE sanal masaÃ¼stÃ¼dÃ¼r.

---

## âœª Temel Ã–zellikler

* ğŸ”’ **Tam Sistem Ä°zolasyonu:** Ana ev dizini gizlenir; Linux Ã§ekirdek ad alanlarÄ± (namespaces) ile izole bir profil atanÄ±r.
*" ğŸ›° **Hafif MATE MasaÃ¼stÃ¼:** Yaru temasÄ± ile optimize edilmiÅŸ, modern ve sade masaÃ¼stÃ¼ deneyimi.
* âš¡ *GeÃ§ici RAM AlanÄ±:** Oturum kapandÄ±ÄŸÄ±nda indirilen tÃ¼m veriler ve geÃ§ici dosyalar RAM'den kalÄ±ntÄ±sszÄsilinir.
* </p * ğŸ® **DonanÄ±m HÌzlandÄ±rma:** NVIDIA ve DRI soket kÃ¶prÃ¼leri ile 3D grafik performansÄ±.
*" ğŸ›  **Dahili TeÅŸhis Konsolu:** GÃ¼venlik loglarÄÅnÄ± anlÄ±k izleme, komut koÅŸturma ve paket sorgulama arayÃ¼zÃ¼.
* * ğŸ’µ **SadeleÅŸtirilmiÅŸ AraÃ§lar:** YalnÄ±zca 5 temel uygulama (Firefox, Caja, MATE Terminal, EOM ve Video OynatÄ±cÄ±).

---

## ğŸš€ Kurulum

### YÃ¶ntem 1: Resmi Launchpad PPA (Ã¶nerilen)

gbash
sudo add-apt-repository ppa:mehmetakifsahin500/safebox -y
sudo apt update
sudo apt install safebox -y
```

### YÃ·ntem 2: DoÄŸrudan .deb Paketi Ä°le

Releases sayfasÄ±ndan en son sÃ¼rÃ¼mÃ¼ indirin ve kurun:

``bash
sudo apt install ./safebox_1.2.3-1~ppa1~noble1_all.deb
```

---

## ğŸ’» KullanÄ±m

Uygulama menÃ¼sÃ¼nden SafeBox Kontrol Merkezi'ni aÃ§abilir veya doÄŸrudan uÃ§birimden baÅŸlatabilirsiniz:

``bash
safebox
```

### Kontrol Merkezi SeÃ§enekleri

| SeÃ§enek | AÃ§Ä±klama |
| :--- | :--- |
| **RAM SÄ±nÄ±rÄ±** | 1-16 GB arasÄ± (varsayÄ±lan: 4 GB) |
| **CPU Ã‡ekirdekleri** | Ä°zole iÅŸlem baÅŸÄ±na kullanÄ±labilir thread sayÄ±sÄ± |
| **Ekran Ã‡Ã¶zÃ¼nlÃ¼ÄŸÃ¼** | 1280x720 -> 1920x1080 arasÄ± |
| **PaylaÅŸÄ±lan KlasÃ¶r** | ~/SafeBox-Paylasim ana sisteme baÄŸlanÄ±r |
| **Ses DesteÄŸi** | PulseAudio / PipeWire entegrasyonu |
| **Ä°nternet EriÅŸimi** | Air-gapped (izole) veya normal aÄŸ| 

---

## ğŸ“ SÃ¼rÃ¼m GecmiÅŸi

* **v1.2.3**: Dahili teÅŸhis konsolu, GTK Karakter dÃ¼zeltmeleri ve Winexe yayÄ±ncÄ± optimizasyonu.
** **v1.2.2**: GeliÅŸmiÅŸ hata yÃ¶netimi, dinamik RAM temizleme (trap cleanup) ve Xephyr soket doÄŸrulamasÄ±.
* **v1.2.1**: Alt sÃ¼reÃ§ hata kontrolleri ve log kilit gÃ¼venlikleri.
* **v1.2.0**: MATE masaÃ¼stÃ¼ geÃ§iÅŸi ve baÄŸÄ±msÄ±z
 uygulama yalÄ±ĞÅµ‹Ä¸((´´´((ŒŒƒÂ~L,•É•­Í¥µ±•È((¨U‰Õ¹ÑÔ€ÈĞ¸ÀĞ1QLÙ•å„•‰¥…¸€ÄÈ¬(¨	Õ‰‰±•İÉ…À€¡‰İÉ…Á€¤(¨5Qµ…Í‡ñÍÓğ‰¥±—}•¹±•É¤(¨a•Á¡åÈ€¡Í…¹…°`ÍÕ¹ÕÕÍÔ¤(¨AåÑ¡½¸€Ì¸à¬((´´´((ŒŒƒÂ~Rp1¥Í…¹Ì()	TÁÉ½©”€¨©5%P1¥Í…¹ÏÄ¨¨¥±”±¥Í…¹Í±…¹µ§}ÓÅÈ¸	­èèm1%9Mt¡1%9M¤((´´´((ŒŒƒÂ~F£Š7Â~Jì•±§}Ñ¥É¥¤((©5•¡µ•Ğ­¥˜ƒy…¡¥¸¬¨€¡İ¥¹•á•”¤€€+Šr§¾â<µ•¡µ•Ñ…­¥™Í…¡¥¸ÔÀÁµ…¥°¹½´((´´´((ŒŒƒÂ~’t-…Ñ¯Ä()-…Ñ¯Å±…ËÅ»Åè¡¿}ŸÙËñå±”­…Ë±…»ÅÈè½É¬€´ø	É…¹ €´øAHå…Á…‰¥±¥ÉÍ¥¹¥è¸(