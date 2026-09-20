with open("README.md", "r") as f:
    content = f.read()

audio_note = """
### Ses İzolasyonu (Audio Socket)
Kullanıcı GUI üzerinden sesi açtığında (Audio=1), Host'a ait PulseAudio veya PipeWire soketi doğrudan Guest ortamına bind edilir. Bu özellik ses aktarımı için zorunlu ve bilinçli bir davranış olsa da, teknik olarak host'un ses altyapısı ile bir paylaşım tüneli oluşturur. Tam bir sanal makine (VM) izolasyonu sunmaz, host'taki ses servisine kontrollü erişim sağlar.
"""
if "Ses İzolasyonu (Audio Socket)" not in content:
    content += audio_note

with open("README.md", "w") as f:
    f.write(content)
