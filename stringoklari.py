# Sadece hatanın nereden geldiğini gösteren okları görüntüler
def stringoklari(metin, pos_baslangici, pos_bitisi):
    sonuc = ''

    # Indeksleri hesapla
    indeks_baslangici = max(metin.rfind('\n', 0, pos_baslangici.idx), 0)
    indeks_bitisi = metin.find('\n', indeks_baslangici + 1)
    if indeks_bitisi < 0: indeks_bitisi = len(metin)

    # Her satırı oluştur
    satir_sayisi = pos_bitisi.ln - pos_baslangici.ln + 1
    for i in range(satir_sayisi):
        # Satır sütunları hesapla
        satir = metin[indeks_baslangici:indeks_bitisi]
        sutun_baslangici = pos_baslangici.col if i == 0 else 0
        sutun_bitisi = pos_bitisi.col if i == satir_sayisi - 1 else len(satir) - 1

        # sonuca ekle
        sonuc += satir + '\n'
        sonuc += ' ' * sutun_baslangici + '^' * (sutun_bitisi - sutun_baslangici)

        # Indeksleri tekrar hesapla
        indeks_baslangici = indeks_bitisi
        indeks_bitisi = metin.find('\n', indeks_baslangici + 1)
        if indeks_bitisi < 0: indeks_bitisi = len(metin)

    return sonuc.replace('\t', '')
