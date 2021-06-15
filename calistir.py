import proje

# Bu dosya, terminal penceresinden ham girdiyi okuyacak sonsuz bir döngüye sahip olacak.
while True:
    metin = input('proje > ')
    if metin.strip() == "": continue
    sonuc, hata = proje.baslat('<stdin>', metin)

    if hata:
        print(hata.goster())
    elif sonuc:
        if len(sonuc.elemanlar) == 1:
            print(repr(sonuc.elemanlar[0]))
        else:
            print(repr(sonuc))
