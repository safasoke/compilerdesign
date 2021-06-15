# Safa Söke 170508001 Derleyici Tasarımı
# Oluşturmaya çalıştığım bu dilin özellikleri
# Değişkenlere değer atama
# karşılaştırma ve matematiksel işlemler
# ekrana bilgi yazdırma
# kullanıcıdan değer alma
# koşul işlemleri
# döngüler
# açıklama satırı
# fonksiyonlar
# listeler
# gömülü metotlar
# return continue ve break metotları
# importlar
from stringoklari import *

import string
import os
import math

# Sabit değerler
# Bir karakterin rakam olup olmadığını tespit edebilmek için
RAKAMLAR = '0123456789'
# Bir karakterin harf olup olmadığını tespit edebilmek için
HARFLER = string.ascii_letters
# Bir karakterin harf + rakam olup olmadığını tespit edebilmek için
HARFLER_RAKAMLAR = HARFLER + RAKAMLAR


# Hatalar
# Aradığımız karakteri bulamazsak bazı hatalar vermemiz gerekir,
# bu yüzden burada yapacağım şey kendi özel hata sınıfımızı tanımlıyorum.
# Bu metotumuz hata ismi detaylar ve posizyon başlangıcı ve bitişi değerlerini alıyor

class Hata:
    def __init__(self, pos_baslangici, pos_bitisi, hata_ismi, detaylar):
        self.pos_baslangici = pos_baslangici
        self.pos_bitisi = pos_bitisi
        self.hata_ismi = hata_ismi
        self.detaylar = detaylar

    # Burada bir metot oluşturuyorum ve bu sadece bir string oluşturacak,
    # hata adını ve ayrıntılarını gösterecek.
    def goster(self):
        sonuc = f'{self.hata_ismi}: {self.detaylar}\n'
        sonuc += f'Dosya {self.pos_baslangici.dosya_adi}, satır {self.pos_baslangici.satir + 1}'
        sonuc += '\n\n' + stringoklari(self.pos_baslangici.dosya_metni, self.pos_baslangici, self.pos_bitisi)
        return sonuc


class KarakterHatasi(Hata):
    def __init__(self, pos_baslangici, pos_bitisi, detaylar):
        super().__init__(pos_baslangici, pos_bitisi, 'Geçersiz karakter', detaylar)


class BeklenenKarakterHatasi(Hata):
    def __init__(self, pos_baslangici, pos_bitisi, detaylar):
        super().__init__(pos_baslangici, pos_bitisi, 'Beklenen Karakter Hatası', detaylar)


# geçersiz bir syntax hatası sınıfı
# bu hatalar, ayrıştırma işleminde bir hata olduğunda oluşturulacaktır.
class GecersizSyntaxHatasi(Hata):
    def __init__(self, pos_baslangici, pos_bitisi, detaylar=''):
        super().__init__(pos_baslangici, pos_bitisi, 'Geçersiz Syntax', detaylar)


class CalismaHatasi(Hata):
    def __init__(self, pos_baslangici, pos_bitisi, detaylar, baglam):
        super().__init__(pos_baslangici, pos_bitisi, 'Çalışma Hatası', detaylar)
        self.baglam = baglam

    def goster(self):
        sonuc = self.geri_izleme()
        sonuc += f'{self.hata_ismi}: {self.detaylar}'
        sonuc += '\n\n' + stringoklari(self.pos_baslangici.dosya_metni, self.pos_baslangici, self.pos_bitisi)
        return sonuc

    def geri_izleme(self):
        sonuc = ''
        pos = self.pos_baslangici
        bglm = self.baglam

        while bglm:
            sonuc = f'  Dosya {pos.dosya_adi}, satır {str(pos.satir + 1)}, -> {bglm.goruntu_adi}\n' + sonuc
            pos = bglm.parent_giris_konumu
            bglm = bglm.parent

        return 'Geri izleme (en son arama):\n' + sonuc


# Konum
# Konum, satır numarası sütun numarasını ve mevcut indeksi takip edecektir.
# Ayrıca, konum sınıfındaki dosya adını ve dosya içeriğini takip edeceğim.
# Bunu yapmamızın nedeni, kullanıcıya tam olarak hangi dosya adının ve hatanın geldiğini söyleyebilmemiz
# ayrıca dosya metni özelliğinden alarak hatanın geldiği satırı da görüntüleyebilmemizdir.
# Daha sonra bunu 'lexer'da kullanacağım.
class Konum:
    def __init__(self, indeks, satir, sutun, dosya_adi, dosya_metni):
        self.indeks = indeks
        self.satir = satir
        self.sutun = sutun
        self.dosya_adi = dosya_adi
        self.dosya_metni = dosya_metni

    # Şimdi ilerle metotunu tanımlıyorum ve bu sadece bir sonraki indekse geçecek
    # ve ardından gerekirse satır ve sütun numaralarını güncelleyecek.
    def ilerle(self, guncel_karakter=None):
        self.indeks += 1
        self.sutun += 1
        # Yapmak istediğim, güncel karakterin yeni bir satıra eşit olup olmadığını kontrol etmek
        # bir satırı artıracağız ve sonra sütunu sıfırlayacağız.
        if guncel_karakter == '\n':
            self.satir += 1
            self.sutun = 0

        return self

    # Sadece konumun bir kopyasını oluşturacak bir kopyalama metotu oluşturuyorum.
    def kopyala(self):
        return Konum(self.indeks, self.satir, self.sutun, self.dosya_adi, self.dosya_metni)


# Tokenlar
# Farklı token türleri için  sabit tanımlıyorum.

TOKEN_INT = 'INT'
TOKEN_FLOAT = 'FLOAT'
TOKEN_STRING = 'STRING'
TOKEN_TANIMLAYICI = 'TANIMLAYICI'
TOKEN_KEYWORD = 'KEYWORD'
TOKEN_TOPLAMA = 'TOPLAMA'
TOKEN_CIKARMA = 'CIKARMA'
TOKEN_CARPMA = 'CARPMA'
TOKEN_BOLME = 'BOLME'
TOKEN_USALMA = 'USALMA'
TOKEN_ESITTIR = 'ESITTIR'
TOKEN_SOLPARANTEZ = 'SOLPARANTEZ'
TOKEN_SAGPARANTEZ = 'SAGPARANTEZ'
TOKEN_SOLKOSELIPARANTEZ = 'SOLKOSELIPARANTEZ'
TOKEN_SAGKOSELIPARANTEZ = 'SAGKOSELIPARANTEZ'
# ee=eşittir '=='
TOKEN_EE = 'EE'
# ed=eşit değildir '!='
TOKEN_ED = 'ED'
TOKEN_KUCUKTUR = 'KUCUKTUR'
TOKEN_BUYUKTUR = 'BUYUKTUR'
TOKEN_KUCUKEE = 'KUCUKEE'
TOKEN_BUYUKEE = 'BUYUKEE'
TOKEN_VIRGUL = 'VIRGUL'
TOKEN_OK = 'OK'
TOKEN_YENISATIR = 'YENISATIR'
TOKEN_DOSYASONU = 'DOSYASONU'
# Dilimizde kullanacağımız keywordler
KEYWORDS = [
    'VAR',
    'AND',
    'OR',
    'NOT',
    'IF',
    'ELIF',
    'ELSE',
    'FOR',
    'TO',
    'STEP',
    'WHILE',
    'FUN',
    'THEN',
    'END',
    'RETURN',
    'CONTINUE',
    'BREAK',
]


# Token, bir türü ve isteğe bağlı olarak bir değeri olan basit bir nesnedir.
# Her token, kodun yalnızca küçük bir bölümünden gelir.
# Token class'ında token'in tipi, değeri pozisyon başlangıcı ve bitişi bulunuyor
# Pozisyon başlangıç ve bitişi bize hatanın nerede olduğunu göstermek için var
class Token:
    def __init__(self, token_turu, deger=None, pos_baslangici=None, pos_bitisi=None):
        self.token_turu = token_turu
        self.deger = deger

        if pos_baslangici:
            self.pos_baslangici = pos_baslangici.kopyala()
            self.pos_bitisi = pos_baslangici.kopyala()
            self.pos_bitisi.ilerle()

        if pos_bitisi:
            self.pos_bitisi = pos_bitisi.kopyala()

    # Eğer token türü ve değeri eşleşirse
    def eslesme(self, tur_, deger):
        return self.token_turu == tur_ and self.deger == deger

    # Ayrıca, terminal penceresine yazdırıldığında güzel görünmesi için ona bir representation method veriyorum.
    def __repr__(self):
        if self.deger: return f'{self.token_turu}:{self.deger}'
        return f'{self.token_turu}'


# Token değere sahip olduktan sonra, türü ve ardından değeri yazdırır
# bir değeri yoksa, yalnızca türü yazdırır.

# LEXER
# Lexer, karakter karakter girdiden geçecek ve metni, süreçte tokens dediğimiz bir listeye bölecektir.
class Lexer:
    # Initialize method kısmında, işleyeceğimiz metni almamız gerekecek.
    # Bunu sadece self.text'e atayacağız
    # Mevcut pozisyonu ve aynı zamanda mevcut karakteri takip etmemiz gerekiyor.
    def __init__(self, dosya_adi, metin):
        self.dosya_adi = dosya_adi
        self.metin = metin
        # negatif bir konumla başlamamızın nedeni, ilerle methotunun onu hemen sıfırdan başlayacak şekilde artırmasıdır.
        self.konum = Konum(-1, 0, -1, dosya_adi, metin)
        self.guncel_karakter = None
        self.ilerle()

    # Metinde sadece bir sonraki karaktere ilerleyecek bir yöntem tanımlıyorum.
    # Pozisyonu artırıyorum ve ardından mevcut karakteri metin içinde o konumdaki karaktere ayarlıyorum.
    # Bunu ancak konum metnin uzunluğundan küçükse yapabiliriz.
    # Metnin sonuna ulaştığımızda, onu none olarak ayarlıyorum..
    def ilerle(self):
        self.konum.ilerle(self.guncel_karakter)
        self.guncel_karakter = self.metin[self.konum.indeks] if self.konum.indeks < len(self.metin) else None

    # Token oluştur metodu
    def token_olustur(self):
        tokens = []
        # Metindeki her karaktere giden bir döngü oluşturuyorum
        # mevcut karakterin none'a eşit olmadığını kontrol ediyorum.
        # Çünkü yukarıda metnin sonuna geldiğimizde onu none olarak ayarladım.
        # Boşluklar ve sekmeler gibi karakterleri yok sayarak başlıyorum,
        # sadece sekmedeki boşluk olup olmadığını kontrol ediyorum
        # ve öyleyse bir sonraki karakteri eklemek için ilerletiyorum.
        while self.guncel_karakter != None:
            if self.guncel_karakter in ' \t':
                self.ilerle()
            elif self.guncel_karakter == '#':
                self.yorum_satiri()
            elif self.guncel_karakter in ';\n':
                tokens.append(Token(TOKEN_YENISATIR, pos_baslangici=self.konum))
                self.ilerle()
                # Mevcut karakterin rakamlarda olup olmadığını kontrol edeceğiz.
            elif self.guncel_karakter in RAKAMLAR:
                tokens.append(self.rakam_olustur())
            elif self.guncel_karakter in HARFLER:
                tokens.append(self.tanimlayici_olustur())
            elif self.guncel_karakter == '"':
                tokens.append(self.string_olustur())
                # Mevcut karakterin bir toplama işareti olup olmadığını kontrol ederek başlıyorum
                # Eğer öyleyse, yeni tip toplama tokenini bir token listesine ekliyorum.
                # Ondan sonra bir sonraki karaktere geçebiliriz.
            elif self.guncel_karakter == '+':
                tokens.append(Token(TOKEN_TOPLAMA, pos_baslangici=self.konum))
                self.ilerle()
                # Burada toplama işlemi için yaptığım aynı şeyi diğerleri için de aşağıda yapıyorum
            elif self.guncel_karakter == '-':
                tokens.append(self.cikarma_veya_ok_olustur())
            elif self.guncel_karakter == '*':
                tokens.append(Token(TOKEN_CARPMA, pos_baslangici=self.konum))
                self.ilerle()
            elif self.guncel_karakter == '/':
                tokens.append(Token(TOKEN_BOLME, pos_baslangici=self.konum))
                self.ilerle()
            elif self.guncel_karakter == '^':
                tokens.append(Token(TOKEN_USALMA, pos_baslangici=self.konum))
                self.ilerle()
            elif self.guncel_karakter == '(':
                tokens.append(Token(TOKEN_SOLPARANTEZ, pos_baslangici=self.konum))
                self.ilerle()
            elif self.guncel_karakter == ')':
                tokens.append(Token(TOKEN_SAGPARANTEZ, pos_baslangici=self.konum))
                self.ilerle()
            elif self.guncel_karakter == '[':
                tokens.append(Token(TOKEN_SOLKOSELIPARANTEZ, pos_baslangici=self.konum))
                self.ilerle()
            elif self.guncel_karakter == ']':
                tokens.append(Token(TOKEN_SAGKOSELIPARANTEZ, pos_baslangici=self.konum))
                self.ilerle()
            elif self.guncel_karakter == '!':
                token, hata = self.esit_degildir_olustur()
                if hata: return [], hata
                tokens.append(token)
            elif self.guncel_karakter == '=':
                tokens.append(self.esittir_olustur())
            elif self.guncel_karakter == '<':
                tokens.append(self.kucuktur_olustur())
            elif self.guncel_karakter == '>':
                tokens.append(self.buyuktur_olustur())
            elif self.guncel_karakter == ',':
                tokens.append(Token(TOKEN_VIRGUL, pos_baslangici=self.konum))
                self.ilerle()
                # Aradığımız karakterle karşılaşmazsak, o karakteri bir değişkende saklayacağım
                # sonra boş bir liste oluşturuyorum, bu yüzden bir token geri veriyorum
                # ayrıca geçersiz bir karakter varsa karakterhatasi methodunu döndürüyorum
            else:
                pos_baslangici = self.konum.kopyala()
                karakter = self.guncel_karakter
                self.ilerle()
                return [], KarakterHatasi(pos_baslangici, self.konum, "'" + karakter + "'")
        # bu sadece parser içindeki dosyanın sonuna ulaşıp ulaşmadığımızı tespit etmemizi sağlar.
        tokens.append(Token(TOKEN_DOSYASONU, pos_baslangici=self.konum))
        # sonra metotun sonunda hata için none döndürüyorum
        return tokens, None

    # Sayı birden fazla karakter olabilir bu yüzden, aslında bir sayı yapan bir fonksiyon yapıyoruz.
    # Bu fonksiyon ya bir integer tokeni ya da bir float tokeni yapacaktır.
    def rakam_olustur(self):
        # Rakamları string formunda takip etmemiz gerekiyor
        rakam_stringi = ''
        # Ayrıca nokta sayısını da takip etmemiz gerekiyor.
        nokta_sayisi = 0
        pos_baslangici = self.konum.kopyala()
        # Sayıda nokta yoksa bu bir integerdir, ancak sayıda nokta varsa o zaman bir floattır.
        # Bu fonksiyonun içinde, mevcut karakterin none olmadığını
        # ve mevcut karakterin bir rakam veya nokta olup olmadığını kontrol edecek başka bir döngü oluşturuyorum.

        while self.guncel_karakter != None and self.guncel_karakter in RAKAMLAR + '.':
            # Geçerli karakter bir noktaysa eğer nokta sayısını artıracağız
            # nokta sayısının zaten bire eşit olması durumunda,döngüden çıkıyoruz çünkü tek sayıda iki nokta olamaz.
            if self.guncel_karakter == '.':
                if nokta_sayisi == 1: break
                nokta_sayisi += 1
            # Eğer nokta yoksa rakam stringini bir artırıyoruz çünkü sıradaki karakter bir rakam olmak zorunda
            rakam_stringi += self.guncel_karakter
            self.ilerle()
        # Nokta sayısının sıfıra eşit olup olmadığını kontrol ediyoruz eğer sıfırsa sayımız bir integer değilse floattır
        if nokta_sayisi == 0:
            return Token(TOKEN_INT, int(rakam_stringi), pos_baslangici, self.konum)
        else:
            return Token(TOKEN_FLOAT, float(rakam_stringi), pos_baslangici, self.konum)

    def string_olustur(self):
        string = ''
        pos_baslangici = self.konum.kopyala()
        kacis_karakteri = False
        self.ilerle()
        # yeni satır ve bir tab için kaçış karakterleri
        kacis_karakteri = {
            'n': '\n',
            't': '\t'
        }
        # Bu koşulun sonuna kaçış karakterimizi ekleyeceğiz, bu yüzden çift tırnak ile karşılaşsanız bile,
        # kaçış karakteri doğruysa çift tırnaktan kaçıyoruz ve döngüye devam ediyoruz.
        while self.guncel_karakter != None and (self.guncel_karakter != '"' or kacis_karakteri):
            if kacis_karakteri:
                string += kacis_karakteri.get(self.guncel_karakter, self.guncel_karakter)
            else:
                # Kaçış karakteri eklememiz gerekiyor, bu yüzden while döngümüzde mevcut karakterin
                # ters eğik çizgiye eşit olup olmadığını kontrol edeceğiz
                if self.guncel_karakter == '\\':
                    kacis_karakteri = True
                else:
                    string += self.guncel_karakter
            self.ilerle()
            # her döngünün sonunda kaçış karakterini false yapıyoruz
            kacis_karakteri = False

        self.ilerle()
        return Token(TOKEN_STRING, string, pos_baslangici, self.konum)

    def tanimlayici_olustur(self):
        tanimlayici_stringi = ''
        pos_baslangici = self.konum.kopyala()
        # rakam oluştur metotuna benzer şekilde yapıyoruz
        while self.guncel_karakter != None and self.guncel_karakter in HARFLER_RAKAMLAR + '_':
            tanimlayici_stringi += self.guncel_karakter
            self.ilerle()
        # dilimizde sahip olacağımız tüm farklı anahtar kelimelerin bir listesini tutmak için
        token_turu = TOKEN_KEYWORD if tanimlayici_stringi in KEYWORDS else TOKEN_TANIMLAYICI
        return Token(token_turu, tanimlayici_stringi, pos_baslangici, self.konum)

    # Ok ve çıkarma işlemlerinin ikisinde de '-' işareti kullanıldığı için onu belirtiyoruz
    def cikarma_veya_ok_olustur(self):
        token_turu = TOKEN_CIKARMA
        pos_baslangici = self.konum.kopyala()
        self.ilerle()
        # eğer '-'dan sonra '>' geliyorsa ok tokenidir
        if self.guncel_karakter == '>':
            self.ilerle()
            token_turu = TOKEN_OK

        return Token(token_turu, pos_baslangici=pos_baslangici, pos_bitisi=self.konum)

    def esit_degildir_olustur(self):
        pos_baslangici = self.konum.kopyala()
        self.ilerle()

        if self.guncel_karakter == '=':
            self.ilerle()
            return Token(TOKEN_ED, pos_baslangici=pos_baslangici, pos_bitisi=self.konum), None
        # Eğer eşit değildir sembolü eşittirden sonra geldiyse hata çıkarıyoruz
        self.ilerle()
        return None, BeklenenKarakterHatasi(pos_baslangici, self.konum, "'=' (sonra '!')")

    def esittir_olustur(self):
        token_turu = TOKEN_ESITTIR
        pos_baslangici = self.konum.kopyala()
        self.ilerle()

        if self.guncel_karakter == '=':
            self.ilerle()
            token_turu = TOKEN_EE

        return Token(token_turu, pos_baslangici=pos_baslangici, pos_bitisi=self.konum)

    def kucuktur_olustur(self):
        token_turu = TOKEN_KUCUKTUR
        pos_baslangici = self.konum.kopyala()
        self.ilerle()

        if self.guncel_karakter == '=':
            self.ilerle()
            token_turu = TOKEN_KUCUKEE

        return Token(token_turu, pos_baslangici=pos_baslangici, pos_bitisi=self.konum)

    def buyuktur_olustur(self):
        token_turu = TOKEN_BUYUKTUR
        pos_baslangici = self.konum.kopyala()
        self.ilerle()

        if self.guncel_karakter == '=':
            self.ilerle()
            token_turu = TOKEN_BUYUKEE

        return Token(token_turu, pos_baslangici=pos_baslangici, pos_bitisi=self.konum)

    def yorum_satiri(self):
        self.ilerle()

        while self.guncel_karakter != '\n':
            self.ilerle()

        self.ilerle()


# Düğümler
# Parser bir ağaç oluşturacak, önce birkaç farklı düğüm türü tanımlamamız gerekiyor

class SayiDugumu:
    def __init__(self, token):
        self.token = token

        self.pos_baslangici = self.token.pos_baslangici
        self.pos_bitisi = self.token.pos_bitisi

    # özel bir represent methodu tanımlıyorum ve bu sadece tokeni string olarak döndürecek.
    def __repr__(self):
        return f'{self.token}'


# sayı düğümü ile aynı
class StringDugumu:
    def __init__(self, token):
        self.token = token

        self.pos_baslangici = self.token.pos_baslangici
        self.pos_bitisi = self.token.pos_bitisi

    def __repr__(self):
        return f'{self.token}'


class ListeDugumu:
    def __init__(self, elemanlar_dugumu, pos_baslangici, pos_bitisi):
        self.elemanlar_dugumu = elemanlar_dugumu

        self.pos_baslangici = pos_baslangici
        self.pos_bitisi = pos_bitisi


class DegiskenErisimDugumu:
    def __init__(self, degisken_ismi_tokeni):
        self.degisken_ismi_tokeni = degisken_ismi_tokeni

        self.pos_baslangici = self.degisken_ismi_tokeni.pos_baslangici
        self.pos_bitisi = self.degisken_ismi_tokeni.pos_bitisi


class DegiskenAtamaDugumu:
    def __init__(self, degisken_ismi_tokeni, deger_dugumu):
        self.degisken_ismi_tokeni = degisken_ismi_tokeni
        self.deger_dugumu = deger_dugumu
        # pozisyon başlangıcını ve bitişini takip ediyoruz
        self.pos_baslangici = self.degisken_ismi_tokeni.pos_baslangici
        self.pos_bitisi = self.deger_dugumu.pos_bitisi


# Şimdi toplama çıkarma çarpma ve bölme işlemleri için işlem düğümü oluşturacağız,
# bunun için sol düğüme operatör token'a ve sağ düğüme ihtiyacımız var.
class IkiliOpDugumu:
    def __init__(self, sol_dugum, op_token, sag_dugum):
        self.sol_dugum = sol_dugum
        self.op_tok = op_token
        self.sag_dugum = sag_dugum
        # başlangıç konumu sol düğümün başlangıcındadır ve ardından bitiş konumu sağ düğümün sonundadır.
        self.pos_baslangici = self.sol_dugum.pos_baslangici
        self.pos_bitisi = self.sag_dugum.pos_bitisi

    def __repr__(self):
        return f'({self.sol_dugum}, {self.op_tok}, {self.sag_dugum})'


# Tek başına bir sayı girdiğimizde syntax hatası vermemesi için tekli operator düğümü sınıfı
class TekliOpDugumu:
    def __init__(self, op_token, dugum):
        self.op_tok = op_token
        self.dugum = dugum

        self.pos_baslangici = self.op_tok.pos_baslangici
        self.pos_bitisi = dugum.pos_bitisi

    def __repr__(self):
        return f'({self.op_tok}, {self.dugum})'


# If koşulu düğümü
class IfDugumu:
    def __init__(self, durumlar, else_durumu):
        self.durumlar = durumlar
        self.else_durumu = else_durumu
        # Burada pozisyon başlangıcı ve bitişi tuple'da tutuyoruz
        self.pos_baslangici = self.durumlar[0][0].pos_baslangici
        self.pos_bitisi = (self.else_durumu or self.durumlar[len(self.durumlar) - 1])[0].pos_bitisi


# For döngüsü düğümü
class ForDugumu:
    def __init__(self, degisken_ismi_tokeni, baslangic_degeri_dugumu, bitis_degeri_dugumu, adim_degeri_dugumu,
                 govde_dugumu, null_dondurmeli):
        # for döngüsü için gerekli olan değerler
        self.degisken_ismi_tokeni = degisken_ismi_tokeni
        self.baslangic_degeri_dugumu = baslangic_degeri_dugumu
        self.bitis_degeri_dugumu = bitis_degeri_dugumu
        self.adim_degeri_dugumu = adim_degeri_dugumu
        self.govde_dugumu = govde_dugumu
        self.null_dondurmeli = null_dondurmeli

        self.pos_baslangici = self.degisken_ismi_tokeni.pos_baslangici
        self.pos_bitisi = self.govde_dugumu.pos_bitisi


# While döngüsü düğümü
class WhileDugumu:
    def __init__(self, kosul_dugumu, govde_dugumu, null_dondurmeli):
        self.kosul_dugumu = kosul_dugumu
        self.govde_dugumu = govde_dugumu
        self.null_dondurmeli = null_dondurmeli

        self.pos_baslangici = self.kosul_dugumu.pos_baslangici
        self.pos_bitisi = self.govde_dugumu.pos_bitisi


class FonksiyonTanimiDugumu:
    def __init__(self, degisken_ismi_tokeni, arg_ismi_tokeni, govde_dugumu, oto_geri_donmeli):
        self.degisken_ismi_tokeni = degisken_ismi_tokeni
        self.arg_ismi_tokeni = arg_ismi_tokeni
        self.govde_dugumu = govde_dugumu
        self.oto_geri_donmeli = oto_geri_donmeli

        if self.degisken_ismi_tokeni:
            self.pos_baslangici = self.degisken_ismi_tokeni.pos_baslangici
        elif len(self.arg_ismi_tokeni) > 0:
            self.pos_baslangici = self.arg_ismi_tokeni[0].pos_baslangici
        else:
            self.pos_baslangici = self.govde_dugumu.pos_baslangici

        self.pos_bitisi = self.govde_dugumu.pos_bitisi


class CagirmaDugumu:
    def __init__(self, cagrilacak_dugum, arg_dugumleri):
        self.cagrilacak_dugum = cagrilacak_dugum
        self.arg_dugumleri = arg_dugumleri

        self.pos_baslangici = self.cagrilacak_dugum.pos_baslangici

        if len(self.arg_dugumleri) > 0:
            self.pos_bitisi = self.arg_dugumleri[len(self.arg_dugumleri) - 1].pos_bitisi
        else:
            self.pos_bitisi = self.cagrilacak_dugum.pos_bitisi


class ReturnDugumu:
    def __init__(self, donus_dugumu, pos_baslangici, pos_bitisi):
        self.donus_dugumu = donus_dugumu

        self.pos_baslangici = pos_baslangici
        self.pos_bitisi = pos_bitisi


class ContinueDugumu:
    def __init__(self, pos_baslangici, pos_bitisi):
        self.pos_baslangici = pos_baslangici
        self.pos_bitisi = pos_bitisi


class BreakDugumu:
    def __init__(self, pos_baslangici, pos_bitisi):
        self.pos_baslangici = pos_baslangici
        self.pos_bitisi = pos_bitisi


#######################################
# Çözümleme Sonuçları
# Okları parser'a ekleme zamanı bunun için bunu daha kolay yapmak için çözümleme sonucu sınıfı oluşturuyorum

class CozumlemeSonucu:
    def __init__(self):
        self.hata = None
        self.dugum = None
        self.last_registered_advance_count = 0
        # kaç kere ilerleme yaptığımızı sayacak
        self.ilerleme_sayisi = 0
        self.terse_say = 0

    # Bu sınıfın 5 metodu olacak
    # bu metot sadece ilerleme için
    def ilerleme_kayit(self):
        self.last_registered_advance_count = 1
        self.ilerleme_sayisi += 1

    def kayit(self, sonuc):
        self.last_registered_advance_count = sonuc.ilerleme_sayisi
        self.ilerleme_sayisi += sonuc.ilerleme_sayisi
        if sonuc.hata: self.hata = sonuc.hata
        return sonuc.dugum

    def kayit_dene(self, sonuc):
        if sonuc.hata:
            self.terse_say = sonuc.ilerleme_sayisi
            return None
        return self.kayit(sonuc)

    def basari(self, dugum):
        self.dugum = dugum
        return self

    def basarisiz(self, hata):
        if not self.hata or self.last_registered_advance_count == 0:
            self.hata = hata
        return self


# Parser
# bir 'Parser' sınıfı tanımlıyorum, bunun token listesi alması gerekiyor
# Parser, lexer'a benzer şekilde mevcut token indeksini takip etmek zorunda
class Parser:
    def __init__(self, tokenlar):
        self.tokenlar = tokenlar
        self.token_indeks = -1
        self.ilerle()

    # token indeksini artırmak zorundayız ve eğer bu token indeksi tokenlar aralığındaysa
    # mevcut tokenı alabiliriz.
    def ilerle(self):
        self.token_indeks += 1
        self.mevcut_tokeni_guncelle()
        return self.mevcut_token

    def terse_git(self, miktar=1):
        self.token_indeks -= miktar
        self.mevcut_tokeni_guncelle()
        return self.mevcut_token

    def mevcut_tokeni_guncelle(self):
        if self.token_indeks >= 0 and self.token_indeks < len(self.tokenlar):
            self.mevcut_token = self.tokenlar[self.token_indeks]

    def cozumle(self):
        yanit = self.komutlar()
        # Bitirmek üzere olduğumuz halde hala dosyanın sonuna gelmediysek
        # Hala çözümlenmemiş kod var demektir bu da syntax hatası var demektir
        if not yanit.hata and self.mevcut_token.token_turu != TOKEN_DOSYASONU:
            return yanit.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                "Token, önceki tokenlar'dan sonra görünemez."
            ))
        return yanit

    # Burada yapmamız gereken grammar kurallarımızı koda dönüştürmek,
    def komutlar(self):
        sonuc = CozumlemeSonucu()
        komutlar = []
        pos_baslangici = self.mevcut_token.pos_baslangici.kopyala()
        # birden fazla satırda kodumuz olduğu durumda
        while self.mevcut_token.token_turu == TOKEN_YENISATIR:
            sonuc.ilerleme_kayit()
            self.ilerle()

        komut = sonuc.kayit(self.komut())
        if sonuc.hata: return sonuc
        komutlar.append(komut)

        daha_fazla_komutlar = True

        while True:
            yenisatir_sayisi = 0
            while self.mevcut_token.token_turu == TOKEN_YENISATIR:
                sonuc.ilerleme_kayit()
                self.ilerle()
                yenisatir_sayisi += 1
            if yenisatir_sayisi == 0:
                daha_fazla_komutlar = False
            # eğer daha fazla komut yoksa döngüden çık
            if not daha_fazla_komutlar: break
            komut = sonuc.kayit_dene(self.komut())
            if not komut:
                self.terse_git(sonuc.terse_say)
                daha_fazla_komutlar = False
                continue
            komutlar.append(komut)

        return sonuc.basari(ListeDugumu(
            komutlar,
            pos_baslangici,
            self.mevcut_token.pos_bitisi.kopyala()
        ))

    def komut(self):
        sonuc = CozumlemeSonucu()
        pos_baslangici = self.mevcut_token.pos_baslangici.kopyala()
        # eğer token return'e eşitse aldığı değeri geri dönecektr
        if self.mevcut_token.eslesme(TOKEN_KEYWORD, 'RETURN'):
            sonuc.ilerleme_kayit()
            self.ilerle()

            ifade = sonuc.kayit_dene(self.ifade())
            if not ifade:
                self.terse_git(sonuc.terse_say)
            return sonuc.basari(ReturnDugumu(ifade, pos_baslangici, self.mevcut_token.pos_baslangici.kopyala()))

        if self.mevcut_token.eslesme(TOKEN_KEYWORD, 'CONTINUE'):
            sonuc.ilerleme_kayit()
            self.ilerle()
            return sonuc.basari(ContinueDugumu(pos_baslangici, self.mevcut_token.pos_baslangici.kopyala()))

        if self.mevcut_token.eslesme(TOKEN_KEYWORD, 'BREAK'):
            sonuc.ilerleme_kayit()
            self.ilerle()
            return sonuc.basari(BreakDugumu(pos_baslangici, self.mevcut_token.pos_baslangici.kopyala()))

        ifade = sonuc.kayit(self.ifade())
        if sonuc.hata:
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                "Beklenen 'RETURN', 'CONTINUE', 'BREAK', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, tanımlayıcı, '+', '-', '(', '[' ya da 'NOT'"
            ))
        return sonuc.basari(ifade)

    def ifade(self):
        sonuc = CozumlemeSonucu()

        if self.mevcut_token.eslesme(TOKEN_KEYWORD, 'VAR'):
            sonuc.ilerleme_kayit()
            self.ilerle()
            # önce mevcut toke türünün bir tanımlayıcıya eşit olup
            # olmadığını kontrol etmeliyiz ve bu durumda bir hata oluşturabiliriz
            if self.mevcut_token.token_turu != TOKEN_TANIMLAYICI:
                return sonuc.basarisiz(GecersizSyntaxHatasi(
                    self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                    "Beklenen tanımlayıcı"
                ))

            degisken_ismi = self.mevcut_token
            sonuc.ilerleme_kayit()
            self.ilerle()

            if self.mevcut_token.token_turu != TOKEN_ESITTIR:
                return sonuc.basarisiz(GecersizSyntaxHatasi(
                    self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                    "Beklenen '='"
                ))

            sonuc.ilerleme_kayit()
            self.ilerle()
            ifade = sonuc.kayit(self.ifade())
            if sonuc.hata: return sonuc
            return sonuc.basari(DegiskenAtamaDugumu(degisken_ismi, ifade))

        dugum = sonuc.kayit(self.ikili_islemler(self.karsi_ifade, ((TOKEN_KEYWORD, 'AND'), (TOKEN_KEYWORD, 'OR'))))

        if sonuc.hata:
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                "Beklenen 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, tanımlayıcı, '+', '-', '(', '[' ya da 'NOT'"
            ))

        return sonuc.basari(dugum)

    # Karşılaştırma ifadeleri
    def karsi_ifade(self):
        sonuc = CozumlemeSonucu()
        # Eğer mevcut token not ifadesine eşitse karşılaştırma ifadesidir
        if self.mevcut_token.eslesme(TOKEN_KEYWORD, 'NOT'):
            op_token = self.mevcut_token
            sonuc.ilerleme_kayit()
            self.ilerle()

            dugum = sonuc.kayit(self.karsi_ifade())
            if sonuc.hata: return sonuc
            return sonuc.basari(TekliOpDugumu(op_token, dugum))

        dugum = sonuc.kayit(self.ikili_islemler(self.arit_ifade, (
            TOKEN_EE, TOKEN_ED, TOKEN_KUCUKTUR, TOKEN_BUYUKTUR, TOKEN_KUCUKEE, TOKEN_BUYUKEE)))
        # Eğer geçersiz syntax girilirse
        if sonuc.hata:
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                "Beklenen int, float, tanımlayıcı, '+', '-', '(', '[', 'IF', 'FOR', 'WHILE', 'FUN' ya da 'NOT'"
            ))

        return sonuc.basari(dugum)

    # Aritmetik ifadeler
    def arit_ifade(self):
        return self.ikili_islemler(self.terim, (TOKEN_TOPLAMA, TOKEN_CIKARMA))

    # Bu kısımda ilk önce bir faktör aramalıyız ve sonra döngüde mevcut token'in çarpılıp çarpılmadığını
    # veya tokenin bölünüp bölünmediğini kontrol etmeye devam ediyoruz
    # tek bir terimde birden çok ve çarpma ve bölme operatörlerine sahip olabilir.
    def terim(self):
        return self.ikili_islemler(self.faktor, (TOKEN_CARPMA, TOKEN_BOLME))

    # Bir integer veya float araması gereken faktör
    def faktor(self):
        sonuc = CozumlemeSonucu()

        token = self.mevcut_token
        # Mevcut token'i alıyoruz, tokenin integer mi yoksa float mı olduğunu kontrol edeceğiz.
        # Eğer öyleyse, ilerleyebiliriz
        if token.token_turu in (TOKEN_TOPLAMA, TOKEN_CIKARMA):
            sonuc.ilerleme_kayit()
            self.ilerle()
            factor = sonuc.kayit(self.faktor())
            if sonuc.hata: return sonuc
            return sonuc.basari(TekliOpDugumu(token, factor))

        return self.usalma()

    # Burada ikili işlemler fonksiyonunu kullanıyoruz
    def usalma(self):
        return self.ikili_islemler(self.cagir, (TOKEN_USALMA,), self.faktor)

    def cagir(self):
        sonuc = CozumlemeSonucu()
        oncelik = sonuc.kayit(self.oncelik())
        if sonuc.hata: return sonuc
        # çağırma işlemi için öncelikle sol parantez gelmeli
        if self.mevcut_token.token_turu == TOKEN_SOLPARANTEZ:
            sonuc.ilerleme_kayit()
            self.ilerle()
            arg_dugumleri = []
            # değişken düğümleri girildikten sonra sağ parantez ile parantez kapatılmalı
            if self.mevcut_token.token_turu == TOKEN_SAGPARANTEZ:
                sonuc.ilerleme_kayit()
                self.ilerle()
            else:
                arg_dugumleri.append(sonuc.kayit(self.ifade()))
                if sonuc.hata:
                    return sonuc.basarisiz(GecersizSyntaxHatasi(
                        self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                        "Beklenen ')', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, tanımlayıcı, '+', '-', '(', '[' ya da 'NOT'"
                    ))
                # değişken isimleri arasına virgül gelmeli
                while self.mevcut_token.token_turu == TOKEN_VIRGUL:
                    sonuc.ilerleme_kayit()
                    self.ilerle()

                    arg_dugumleri.append(sonuc.kayit(self.ifade()))
                    if sonuc.hata: return sonuc
                # en son sağ parantez ile kapatılması gerekiyor
                if self.mevcut_token.token_turu != TOKEN_SAGPARANTEZ:
                    return sonuc.basarisiz(GecersizSyntaxHatasi(
                        self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                        f"Beklenen ',' ya da ')'"
                    ))

                sonuc.ilerleme_kayit()
                self.ilerle()
            return sonuc.basari(CagirmaDugumu(oncelik, arg_dugumleri))
        return sonuc.basari(oncelik)

    def oncelik(self):
        sonuc = CozumlemeSonucu()
        token = self.mevcut_token

        if token.token_turu in (TOKEN_INT, TOKEN_FLOAT):
            sonuc.ilerleme_kayit()
            self.ilerle()
            return sonuc.basari(SayiDugumu(token))

        elif token.token_turu == TOKEN_STRING:
            sonuc.ilerleme_kayit()
            self.ilerle()
            return sonuc.basari(StringDugumu(token))
        # Token türü ve tanımı eşitse değişken erişim düğümünü dönecek
        elif token.token_turu == TOKEN_TANIMLAYICI:
            sonuc.ilerleme_kayit()
            self.ilerle()
            return sonuc.basari(DegiskenErisimDugumu(token))

        elif token.token_turu == TOKEN_SOLPARANTEZ:
            sonuc.ilerleme_kayit()
            self.ilerle()
            ifade = sonuc.kayit(self.ifade())
            if sonuc.hata: return sonuc
            if self.mevcut_token.token_turu == TOKEN_SAGPARANTEZ:
                sonuc.ilerleme_kayit()
                self.ilerle()
                return sonuc.basari(ifade)
            else:
                return sonuc.basarisiz(GecersizSyntaxHatasi(
                    self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                    "Beklenen ')'"
                ))

        elif token.token_turu == TOKEN_SOLKOSELIPARANTEZ:
            liste_komutu = sonuc.kayit(self.liste_komutu())
            if sonuc.hata: return sonuc
            return sonuc.basari(liste_komutu)
        # Eğer token if'e eşitse
        elif token.eslesme(TOKEN_KEYWORD, 'IF'):
            if_komutu = sonuc.kayit(self.if_komutu())
            if sonuc.hata: return sonuc
            return sonuc.basari(if_komutu)

        elif token.eslesme(TOKEN_KEYWORD, 'FOR'):
            for_komutu = sonuc.kayit(self.for_komutu())
            if sonuc.hata: return sonuc
            return sonuc.basari(for_komutu)

        elif token.eslesme(TOKEN_KEYWORD, 'WHILE'):
            while_komutu = sonuc.kayit(self.while_komutu())
            if sonuc.hata: return sonuc
            return sonuc.basari(while_komutu)

        elif token.eslesme(TOKEN_KEYWORD, 'FUN'):
            fonk_tanimi = sonuc.kayit(self.fonk_tanimi())
            if sonuc.hata: return sonuc
            return sonuc.basari(fonk_tanimi)

        return sonuc.basarisiz(GecersizSyntaxHatasi(
            token.pos_baslangici, token.pos_bitisi,
            "Beklenen ifadeler int, float, tanımlayıcı, '+', '-', '(', '[', IF', 'FOR', 'WHILE', 'FUN'"
        ))

    def liste_komutu(self):
        sonuc = CozumlemeSonucu()
        elemanlar_dugumu = []
        pos_baslangici = self.mevcut_token.pos_baslangici.kopyala()
        # Listemiz sol köşeli parantez ile başlamak zorunda eğer öyle değilse syntax hatası veriyoruz
        if self.mevcut_token.token_turu != TOKEN_SOLKOSELIPARANTEZ:
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen '['"
            ))
        # hata yoksa ilerliyoruz
        sonuc.ilerleme_kayit()
        self.ilerle()
        # Eğer sonrasında sağ köşeli parantez gelirse listeyi bitiriyoruz
        if self.mevcut_token.token_turu == TOKEN_SAGKOSELIPARANTEZ:
            sonuc.ilerleme_kayit()
            self.ilerle()
        else:
            # aksi durumda elemanları aralarında virgül olacak şekilde listeye ekliyoruz
            elemanlar_dugumu.append(sonuc.kayit(self.ifade()))
            if sonuc.hata:
                return sonuc.basarisiz(GecersizSyntaxHatasi(
                    self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                    "Beklenen ']', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, tanımlayıcı, '+', '-', '(', '[' ya da 'NOT'"
                ))

            while self.mevcut_token.token_turu == TOKEN_VIRGUL:
                sonuc.ilerleme_kayit()
                self.ilerle()

                elemanlar_dugumu.append(sonuc.kayit(self.ifade()))
                if sonuc.hata: return sonuc

            if self.mevcut_token.token_turu != TOKEN_SAGKOSELIPARANTEZ:
                return sonuc.basarisiz(GecersizSyntaxHatasi(
                    self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                    f"Beklenen ',' ya da ']'"
                ))

            sonuc.ilerleme_kayit()
            self.ilerle()

        return sonuc.basari(ListeDugumu(
            elemanlar_dugumu,
            pos_baslangici,
            self.mevcut_token.pos_bitisi.kopyala()
        ))

    # Eğer if komutu varsa
    def if_komutu(self):
        sonuc = CozumlemeSonucu()
        tum_durumlar = sonuc.kayit(self.if_komutu_durumlari('IF'))
        if sonuc.hata: return sonuc
        durumlar, else_durumlari = tum_durumlar
        return sonuc.basari(IfDugumu(durumlar, else_durumlari))

    # Elif komutu varsa
    def if_komutu_b(self):
        return self.if_komutu_durumlari('ELIF')

    # Else komutu varsa
    def if_komutu_c(self):
        sonuc = CozumlemeSonucu()
        else_durumu = None

        if self.mevcut_token.eslesme(TOKEN_KEYWORD, 'ELSE'):
            sonuc.ilerleme_kayit()
            self.ilerle()
            # Else'den sonra ne geldiğine bakıyoruz
            if self.mevcut_token.token_turu == TOKEN_YENISATIR:
                sonuc.ilerleme_kayit()
                self.ilerle()

                komutlar = sonuc.kayit(self.komutlar())
                if sonuc.hata: return sonuc
                else_durumu = (komutlar, True)
                # Eğer end geldiyse
                if self.mevcut_token.eslesme(TOKEN_KEYWORD, 'END'):
                    sonuc.ilerleme_kayit()
                    self.ilerle()
                else:
                    return sonuc.basarisiz(GecersizSyntaxHatasi(
                        self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                        "Beklenen 'END'"
                    ))
            else:
                ifade = sonuc.kayit(self.komut())
                if sonuc.hata: return sonuc
                else_durumu = (ifade, False)

        return sonuc.basari(else_durumu)

    def if_komutu_b_veya_c(self):
        sonuc = CozumlemeSonucu()
        durumlar, else_durumu = [], None
        # Eğer mevcut toke elif ise sonucu b durumuna kaydediyoruz değilse c durumuna kaydediyoruz
        if self.mevcut_token.eslesme(TOKEN_KEYWORD, 'ELIF'):
            tum_durumlar = sonuc.kayit(self.if_komutu_b())
            if sonuc.hata: return sonuc
            durumlar, else_durumu = tum_durumlar
        else:
            else_durumu = sonuc.kayit(self.if_komutu_c())
            if sonuc.hata: return sonuc

        return sonuc.basari((durumlar, else_durumu))

    def if_komutu_durumlari(self, durum_keywordu):
        sonuclar = CozumlemeSonucu()
        durumlar = []
        else_durumu = None
        # Eğer geçersiz bir syntax girildiyse
        if not self.mevcut_token.eslesme(TOKEN_KEYWORD, durum_keywordu):
            return sonuclar.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen '{durum_keywordu}'"
            ))

        sonuclar.ilerleme_kayit()
        self.ilerle()
        # koşulu kaydediyoruz
        kosul = sonuclar.kayit(self.ifade())
        if sonuclar.hata: return sonuclar
        # Eğer sonrasında then gelmediyse syntax hatası veriyoruz
        if not self.mevcut_token.eslesme(TOKEN_KEYWORD, 'THEN'):
            return sonuclar.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen 'THEN'"
            ))

        sonuclar.ilerleme_kayit()
        self.ilerle()
        # Eğer yeni satıra geçtiyse
        if self.mevcut_token.token_turu == TOKEN_YENISATIR:
            sonuclar.ilerleme_kayit()
            self.ilerle()
            # komutu kaydediyoruz ve durumlara koşulu ve komutu ekliyoruz
            komutlar = sonuclar.kayit(self.komutlar())
            if sonuclar.hata: return sonuclar
            durumlar.append((kosul, komutlar, True))
            # Eğer sonrasında END geldiyse ilerlemeyi kaydediyoruz
            if self.mevcut_token.eslesme(TOKEN_KEYWORD, 'END'):
                sonuclar.ilerleme_kayit()
                self.ilerle()
                # Yeni durum varsa ya da else durumuysa durumları yeni durumlarla genişletiyoruz
            else:
                tum_durumlar = sonuclar.kayit(self.if_komutu_b_veya_c())
                if sonuclar.hata: return sonuclar
                yeni_durumlar, else_durumu = tum_durumlar
                durumlar.extend(yeni_durumlar)
        else:
            ifade = sonuclar.kayit(self.komut())
            if sonuclar.hata: return sonuclar
            durumlar.append((kosul, ifade, False))

            tum_durumlar = sonuclar.kayit(self.if_komutu_b_veya_c())
            if sonuclar.hata: return sonuclar
            yeni_durumlar, else_durumu = tum_durumlar
            durumlar.extend(yeni_durumlar)

        return sonuclar.basari((durumlar, else_durumu))

    def for_komutu(self):
        sonuc = CozumlemeSonucu()
        # Eğer mevcut token for ile eşleşmiyorsa geçersiz syntax hatası veriyoruz
        if not self.mevcut_token.eslesme(TOKEN_KEYWORD, 'FOR'):
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen 'FOR'"
            ))
        # Eğer for'sa ilerliyoruz
        sonuc.ilerleme_kayit()
        self.ilerle()
        # Eğer mevcut token değişkeni tanımladığımız isimle eşleşmiyorsa tanımlayıcı hatası veriyoruz
        if self.mevcut_token.token_turu != TOKEN_TANIMLAYICI:
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen tanımlayıcı"
            ))
        # Eğer tanımlanan isimle eşleştiyse ilerlemeye devam ediyoruz
        degisken_ismi = self.mevcut_token
        sonuc.ilerleme_kayit()
        self.ilerle()
        # Eğer tanımlamadan sonra eşittir gelmediyse hata veriyoruz
        if self.mevcut_token.token_turu != TOKEN_ESITTIR:
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen '='"
            ))
        # hata yoksa devam ediyoruz
        sonuc.ilerleme_kayit()
        self.ilerle()
        # Başlangıç değerini okuyoruz
        baslangic_degeri = sonuc.kayit(self.ifade())
        if sonuc.hata: return sonuc
        # başlangıç değerinden sonra to gelmediyse hata veriyoruz
        if not self.mevcut_token.eslesme(TOKEN_KEYWORD, 'TO'):
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen 'TO'"
            ))
        # hata yoksa devam ediyoruz
        sonuc.ilerleme_kayit()
        self.ilerle()
        # to'dan sonra bitiş değeri gelmeli bitiş değerini okuyoruz
        bitis_degeri = sonuc.kayit(self.ifade())
        if sonuc.hata: return sonuc
        # döngüdeki değeri değiştirmek için adım değerini okuyoruz
        if self.mevcut_token.eslesme(TOKEN_KEYWORD, 'STEP'):
            sonuc.ilerleme_kayit()
            self.ilerle()

            adim_degeri = sonuc.kayit(self.ifade())
            if sonuc.hata: return sonuc
        else:
            adim_degeri = None
        # sonrasında then gelmeli eğer then yoksa hata veriyoruz
        if not self.mevcut_token.eslesme(TOKEN_KEYWORD, 'THEN'):
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen 'THEN'"
            ))
        # hata yoksa devam ediyoruz
        sonuc.ilerleme_kayit()
        self.ilerle()
        # artık döngü için yeni satıra geçmeliyiz yeni satıra geçtiyse devam ediyoruz
        if self.mevcut_token.token_turu == TOKEN_YENISATIR:
            sonuc.ilerleme_kayit()
            self.ilerle()
            # döngünün gövde kısmı
            govde = sonuc.kayit(self.komutlar())
            if sonuc.hata: return sonuc
            # daha sonrasında end gelmediyse hata veriyoruz
            if not self.mevcut_token.eslesme(TOKEN_KEYWORD, 'END'):
                return sonuc.basarisiz(GecersizSyntaxHatasi(
                    self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                    f"Beklenen 'END'"
                ))
            # hata yoksa devam ediyoruz
            sonuc.ilerleme_kayit()
            self.ilerle()
            # değerlerimizi başarılı bir şekilde geri döndürüyoruz
            return sonuc.basari(ForDugumu(degisken_ismi, baslangic_degeri, bitis_degeri, adim_degeri, govde, True))

        govde = sonuc.kayit(self.komut())
        if sonuc.hata: return sonuc

        return sonuc.basari(ForDugumu(degisken_ismi, baslangic_degeri, bitis_degeri, adim_degeri, govde, False))

    def while_komutu(self):
        sonuc = CozumlemeSonucu()
        # eğer tokenimiz while ile eşleşmiyorsa syntax hatası veriyoruz
        if not self.mevcut_token.eslesme(TOKEN_KEYWORD, 'WHILE'):
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen 'WHILE'"
            ))
        # hata yoksa devam ediyoruz
        sonuc.ilerleme_kayit()
        self.ilerle()
        # While döngüsü için gerekli olan koşulu okuyoruz
        kosul = sonuc.kayit(self.ifade())
        if sonuc.hata: return sonuc
        # koşuldan sonra then gelmeli yoksa syntax hatası veriyoruz
        if not self.mevcut_token.eslesme(TOKEN_KEYWORD, 'THEN'):
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen 'THEN'"
            ))
        # hata yoksa devam ediyoruz
        sonuc.ilerleme_kayit()
        self.ilerle()
        # döngü gövdesi için yeni satıra geçmeliyiz
        if self.mevcut_token.token_turu == TOKEN_YENISATIR:
            sonuc.ilerleme_kayit()
            self.ilerle()
            # döngünün gerçekleşeceği gövde kısmı
            govde = sonuc.kayit(self.komutlar())
            if sonuc.hata: return sonuc
            # eğer sonrasında end gelmediyse hata veriyoruz
            if not self.mevcut_token.eslesme(TOKEN_KEYWORD, 'END'):
                return sonuc.basarisiz(GecersizSyntaxHatasi(
                    self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                    f"Beklenen 'END'"
                ))
            # hata yoksa devam ediyoruz
            sonuc.ilerleme_kayit()
            self.ilerle()

            return sonuc.basari(WhileDugumu(kosul, govde, True))

        govde = sonuc.kayit(self.komut())
        if sonuc.hata: return sonuc
        # sonucu başarılı şekilde dönüyoruz
        return sonuc.basari(WhileDugumu(kosul, govde, False))

    def fonk_tanimi(self):
        sonuc = CozumlemeSonucu()
        # eğer başlangıç FUN ile başlamıyorsa syntax hatası
        if not self.mevcut_token.eslesme(TOKEN_KEYWORD, 'FUN'):
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen 'FUN'"
            ))
        # hata yoksa devam
        sonuc.ilerleme_kayit()
        self.ilerle()
        # Burada fonksiyon isminin tanım kısmı
        if self.mevcut_token.token_turu == TOKEN_TANIMLAYICI:
            degisken_ismi_tokeni = self.mevcut_token
            sonuc.ilerleme_kayit()
            self.ilerle()
            # eğer isim tanımından sonra sol parantez gelmediyse syntax hatası veriyoruz
            if self.mevcut_token.token_turu != TOKEN_SOLPARANTEZ:
                return sonuc.basarisiz(GecersizSyntaxHatasi(
                    self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                    f"Beklenen '('"
                ))
        else:
            # isim tanımlaması veya parantez yoksa yine syntax hatası veriyoruz
            degisken_ismi_tokeni = None
            if self.mevcut_token.token_turu != TOKEN_SOLPARANTEZ:
                return sonuc.basarisiz(GecersizSyntaxHatasi(
                    self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                    f"Beklenen tanımlayıcı ya da '('"
                ))
        # hata yoksa ilerliyoruz
        sonuc.ilerleme_kayit()
        self.ilerle()
        arg_isim_tokeni = []
        # fonksiyonda kullanılacak değişken isimlerini giriyoruz
        if self.mevcut_token.token_turu == TOKEN_TANIMLAYICI:
            arg_isim_tokeni.append(self.mevcut_token)
            sonuc.ilerleme_kayit()
            self.ilerle()
            # değişkenler arasında virgül olması gerekiyor
            while self.mevcut_token.token_turu == TOKEN_VIRGUL:
                sonuc.ilerleme_kayit()
                self.ilerle()

                if self.mevcut_token.token_turu != TOKEN_TANIMLAYICI:
                    return sonuc.basarisiz(GecersizSyntaxHatasi(
                        self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                        f"Beklenen tanımlayıcı"
                    ))

                arg_isim_tokeni.append(self.mevcut_token)
                sonuc.ilerleme_kayit()
                self.ilerle()
            # değişken isimlerinde sonra sağ parantez gelmesi gerekiyor
            if self.mevcut_token.token_turu != TOKEN_SAGPARANTEZ:
                return sonuc.basarisiz(GecersizSyntaxHatasi(
                    self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                    f"Beklenen ',' ya da ')'"
                ))
        else:
            if self.mevcut_token.token_turu != TOKEN_SAGPARANTEZ:
                return sonuc.basarisiz(GecersizSyntaxHatasi(
                    self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                    f"Beklenen tanımlayıcı ya da ')'"
                ))

        sonuc.ilerleme_kayit()
        self.ilerle()
        # değişken isimleri tanımlamasından sonra ok gelecek '->'
        if self.mevcut_token.token_turu == TOKEN_OK:
            sonuc.ilerleme_kayit()
            self.ilerle()
            # sonrasında fonksiyon kısmı
            govde = sonuc.kayit(self.ifade())
            if sonuc.hata: return sonuc

            return sonuc.basari(FonksiyonTanimiDugumu(
                degisken_ismi_tokeni,
                arg_isim_tokeni,
                govde,
                True
            ))

        if self.mevcut_token.token_turu != TOKEN_YENISATIR:
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen '->' ya da NEWLINE"
            ))

        sonuc.ilerleme_kayit()
        self.ilerle()

        govde = sonuc.kayit(self.komutlar())
        if sonuc.hata: return sonuc
        # en sonunda end ile bitmesi gerekiyor
        if not self.mevcut_token.eslesme(TOKEN_KEYWORD, 'END'):
            return sonuc.basarisiz(GecersizSyntaxHatasi(
                self.mevcut_token.pos_baslangici, self.mevcut_token.pos_bitisi,
                f"Beklenen 'END'"
            ))

        sonuc.ilerleme_kayit()
        self.ilerle()

        return sonuc.basari(FonksiyonTanimiDugumu(
            degisken_ismi_tokeni,
            arg_isim_tokeni,
            govde,
            False
        ))

    # Bu method hem terim hem de ifade tarafından paylaşılabilir.
    # Bu, aradığımız kurala karşılık geliyor ve daha sonra, ifade durumunda toplama ve çıkarma olacak ve terim durumunda
    # çarpma veya bölöe şekilde kabul edilebilecek bir işlem tokenlerı listesi alması gerekiyor
    def ikili_islemler(self, fonksiyon_a, ops, fonksiyon_b=None):
        if fonksiyon_b == None:
            fonksiyon_b = fonksiyon_a

        sonuc = CozumlemeSonucu()
        sol = sonuc.kayit(fonksiyon_a())
        if sonuc.hata: return sonuc

        while self.mevcut_token.token_turu in ops or (self.mevcut_token.token_turu, self.mevcut_token.deger) in ops:
            op_tok = self.mevcut_token
            sonuc.ilerleme_kayit()
            self.ilerle()
            sag = sonuc.kayit(fonksiyon_b())
            if sonuc.hata: return sonuc
            sol = IkiliOpDugumu(sol, op_tok, sag)

        return sonuc.basari(sol)


#######################################
# Çalışma Zamanı Sonuçları
# Mevcut sonucu takip edecek ve varsa bir hatayı da takip edecek.

class RTSonucu:
    def __init__(self):
        self.reset()

    def reset(self):
        self.deger = None
        self.hata = None
        self.fonksiyon_donus_degeri = None
        self.dongu_devam_etmeli = False
        self.donguden_cikilmali = False

    def kayit(self, sonuc):
        self.hata = sonuc.hata
        self.fonksiyon_donus_degeri = sonuc.fonksiyon_donus_degeri
        self.dongu_devam_etmeli = sonuc.dongu_devam_etmeli
        self.donguden_cikilmali = sonuc.donguden_cikilmali
        return sonuc.deger

    def basari(self, deger):
        self.reset()
        self.deger = deger
        return self

    def basari_return(self, deger):
        self.reset()
        self.fonksiyon_donus_degeri = deger
        return self

    def basari_continue(self):
        self.reset()
        self.dongu_devam_etmeli = True
        return self

    def basari_break(self):
        self.reset()
        self.donguden_cikilmali = True
        return self

    def basarisiz(self, hata):
        self.reset()
        self.hata = hata
        return self

    def geri_donmeli(self):
        # Bu, devam etmemizi ve mevcut fonksiyonun dışına çıkmamızı sağlar.
        return (
                self.hata or
                self.fonksiyon_donus_degeri or
                self.dongu_devam_etmeli or
                self.donguden_cikilmali
        )


# Değerler
#

class Deger:
    def __init__(self):
        self.pos_ayarla()
        self.baglam_ayarla()

    def pos_ayarla(self, pos_baslangici=None, pos_bitisi=None):
        self.pos_baslangici = pos_baslangici
        self.pos_bitisi = pos_bitisi
        return self

    def baglam_ayarla(self, baglam=None):
        self.baglam = baglam
        return self

    def toplama(self, baska):
        return None, self.gecersiz_islem(baska)

    def cikarma(self, baska):
        return None, self.gecersiz_islem(baska)

    def carpma(self, baska):
        return None, self.gecersiz_islem(baska)

    def bolme(self, baska):
        return None, self.gecersiz_islem(baska)

    def us_alma(self, baska):
        return None, self.gecersiz_islem(baska)

    def get_karsilastirma_esittir(self, baska):
        return None, self.gecersiz_islem(baska)

    def get_karsilastirma_esit_degildir(self, baska):
        return None, self.gecersiz_islem(baska)

    def get_karsilastirma_kucuktur(self, baska):
        return None, self.gecersiz_islem(baska)

    def get_karsilastirma_buyuktur(self, baska):
        return None, self.gecersiz_islem(baska)

    def get_karsilastirma_kucuk_esittir(self, baska):
        return None, self.gecersiz_islem(baska)

    def get_karsilastirma_buyuk_esittir(self, baska):
        return None, self.gecersiz_islem(baska)

    def ve_ifadesi(self, baska):
        return None, self.gecersiz_islem(baska)

    def veya_ifadesi(self, baska):
        return None, self.gecersiz_islem(baska)

    def degil_ifadesi(self, other):
        return None, self.gecersiz_islem(other)

    def yurut(self, args):
        return RTSonucu().basarisiz(self.gecersiz_islem())

    def kopyala(self):
        raise Exception('Kopyala metodu tanımlanmadı.')

    def is_true(self):
        return False

    def gecersiz_islem(self, baska=None):
        if not baska: baska = self
        return CalismaHatasi(
            self.pos_baslangici, baska.pos_bitisi,
            'Geçersiz işlem',
            self.baglam
        )


# Bu sınıf sadece sayıları depolamak ve daha sonra diğer sayılarla çalışmak için olacak.
class Sayi(Deger):
    def __init__(self, deger):
        super().__init__()
        self.deger = deger

    # Toplama için olacak metot
    def toplama(self, baska):
        if isinstance(baska, Sayi):
            return Sayi(self.deger + baska.deger).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    # Çıkarma için olacak metot
    def cikarma(self, baska):
        if isinstance(baska, Sayi):
            return Sayi(self.deger - baska.deger).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    # carpma için olacak metot
    def carpma(self, baska):
        if isinstance(baska, Sayi):
            return Sayi(self.deger * baska.deger).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    # Bölme için olacak metot
    def bolme(self, baska):
        if isinstance(baska, Sayi):
            if baska.deger == 0:
                return None, CalismaHatasi(
                    baska.pos_baslangici, baska.pos_bitisi,
                    'Sıfıra bölündü',
                    self.baglam
                )

            return Sayi(self.deger / baska.deger).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    def us_alma(self, baska):
        if isinstance(baska, Sayi):
            return Sayi(self.deger ** baska.deger).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    def get_karsilastirma_esittir(self, baska):
        if isinstance(baska, Sayi):
            return Sayi(int(self.deger == baska.deger)).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    def get_karsilastirma_esit_degildir(self, baska):
        if isinstance(baska, Sayi):
            return Sayi(int(self.deger != baska.deger)).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    def get_karsilastirma_kucuktur(self, baska):
        if isinstance(baska, Sayi):
            return Sayi(int(self.deger < baska.deger)).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    def get_karsilastirma_buyuktur(self, baska):
        if isinstance(baska, Sayi):
            return Sayi(int(self.deger > baska.deger)).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    def get_karsilastirma_kucuk_esittir(self, baska):
        if isinstance(baska, Sayi):
            return Sayi(int(self.deger <= baska.deger)).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    def get_karsilastirma_buyuk_esittir(self, baska):
        if isinstance(baska, Sayi):
            return Sayi(int(self.deger >= baska.deger)).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    def ve_ifadesi(self, baska):
        if isinstance(baska, Sayi):
            return Sayi(int(self.deger and baska.deger)).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    def veya_ifadesi(self, baska):
        if isinstance(baska, Sayi):
            return Sayi(int(self.deger or baska.deger)).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    def degil_ifadesi(self):
        return Sayi(1 if self.deger == 0 else 0).baglam_ayarla(self.baglam), None

    def kopyala(self):
        kopyala = Sayi(self.deger)
        kopyala.pos_ayarla(self.pos_baslangici, self.pos_bitisi)
        kopyala.baglam_ayarla(self.baglam)
        return kopyala

    def is_true(self):
        return self.deger != 0

    def __str__(self):
        return str(self.deger)

    def __repr__(self):
        return str(self.deger)


Sayi.null = Sayi(0)
Sayi.false = Sayi(0)
Sayi.true = Sayi(1)
Sayi.math_PI = Sayi(math.pi)


class String(Deger):
    def __init__(self, deger):
        super().__init__()
        self.deger = deger

    # iki stringi birleştirmek için
    def toplama(self, baska):
        if isinstance(baska, String):
            return String(self.deger + baska.deger).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    # bir stringi bir sayı kadar tekrarlamak için
    def carpma(self, baska):
        if isinstance(baska, Sayi):
            return String(self.deger * baska.deger).baglam_ayarla(self.baglam), None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    def is_true(self):
        return len(self.deger) > 0

    # Ayrıca diğer tüm değerler gibi bir kopya yöntemine ihtiyacımız var, böylece bu yeni bir string oluşturacak ve
    # aynı değeri iletecek ve ardından yeni bir stringin konumunu ve bağlamını ayarlayacak
    def kopyala(self):
        kopyala = String(self.deger)
        kopyala.pos_ayarla(self.pos_baslangici, self.pos_bitisi)
        kopyala.baglam_ayarla(self.baglam)
        return kopyala

    def __str__(self):
        return self.deger

    def __repr__(self):
        return f'"{self.deger}"'


class Liste(Deger):
    def __init__(self, elemanlar):
        super().__init__()
        self.elemanlar = elemanlar

    # listeye eleman eklemek için
    def toplama(self, baska):
        yeni_liste = self.kopyala()
        yeni_liste.elemanlar.append(baska)
        return yeni_liste, None

    # listeden eleman çıkarmak için
    def cikarma(self, baska):
        if isinstance(baska, Sayi):
            yeni_liste = self.kopyala()
            try:
                yeni_liste.elemanlar.pop(baska.deger)
                return yeni_liste, None
            except:
                return None, CalismaHatasi(
                    baska.pos_baslangici, baska.pos_bitisi,
                    'Bu indeksteki öğe, indeks sınırlarının dışında olduğundan listeden kaldırılamadı.',
                    self.baglam
                )
        else:
            return None, Deger.gecersiz_islem(self, baska)

    # listeleri birleştirmek için
    def carpma(self, baska):
        if isinstance(baska, Liste):
            yeni_liste = self.kopyala()
            yeni_liste.elemanlar.extend(baska.elemanlar)
            return yeni_liste, None
        else:
            return None, Deger.gecersiz_islem(self, baska)

    # listeden elemanları almak için
    def bolme(self, baska):
        if isinstance(baska, Sayi):
            try:
                return self.elemanlar[baska.deger], None
            except:
                return None, CalismaHatasi(
                    baska.pos_baslangici, baska.pos_bitisi,
                    'Bu indeksteki öğe, indeks sınırlarının dışında olduğundan listeden alınamadı.',
                    self.baglam
                )
        else:
            return None, Deger.gecersiz_islem(self, baska)

    def kopyala(self):
        kopyala = Liste(self.elemanlar)
        kopyala.pos_ayarla(self.pos_baslangici, self.pos_bitisi)
        kopyala.baglam_ayarla(self.baglam)
        return kopyala

    def __str__(self):
        return ", ".join([str(x) for x in self.elemanlar])

    def __repr__(self):
        return f'[{", ".join([repr(x) for x in self.elemanlar])}]'


class TemelFonksiyon(Deger):
    def __init__(self, isim):
        super().__init__()
        self.isim = isim or "<anonim>"

    def yeni_baglam_olustur(self):
        yeni_baglam = Baglam(self.isim, self.baglam, self.pos_baslangici)
        yeni_baglam.sembol_tablosu = SembolTablosu(yeni_baglam.parent.sembol_tablosu)
        return yeni_baglam

    # argsları kontrol edecek
    def args_kontrol_et(self, arg_isimleri, args):
        sonuc = RTSonucu()

        if len(args) > len(arg_isimleri):
            return sonuc.basarisiz(CalismaHatasi(
                self.pos_baslangici, self.pos_bitisi,
                f"{len(args) - len(arg_isimleri)} çok fazla args geçti {self}",
                self.baglam
            ))

        if len(args) < len(arg_isimleri):
            return sonuc.basarisiz(CalismaHatasi(
                self.pos_baslangici, self.pos_bitisi,
                f"{len(arg_isimleri) - len(args)} çok az args geçti {self}",
                self.baglam
            ))

        return sonuc.basari(None)

    # bu sadece tüm argsları sembol tablosuna koyacaktır.
    def args_doldur(self, arg_isimleri, args, calisan_baglam):
        for i in range(len(args)):
            arg_ismi = arg_isimleri[i]
            arg_degeri = args[i]
            arg_degeri.baglam_ayarla(calisan_baglam)
            calisan_baglam.sembol_tablosu.set(arg_ismi, arg_degeri)

    # argsları hem kontrol edecek hem de dolduracak
    def args_kontrol_et_ve_doldur(self, arg_isimleri, args, calisan_baglam):
        sonuc = RTSonucu()
        sonuc.kayit(self.args_kontrol_et(arg_isimleri, args))
        if sonuc.geri_donmeli(): return sonuc
        self.args_doldur(arg_isimleri, args, calisan_baglam)
        return sonuc.basari(None)


class Fonksiyon(TemelFonksiyon):
    def __init__(self, isim, govde_dugumu, arg_isimleri, oto_geri_donmeli):
        super().__init__(isim)
        self.govde_dugumleri = govde_dugumu
        self.arg_isimleri = arg_isimleri
        self.oto_geri_donmeli = oto_geri_donmeli

    # execute kısmı
    def yurut(self, args):
        sonuc = RTSonucu()
        interpreter = Interpreter()
        baglami_yurut = self.yeni_baglam_olustur()

        sonuc.kayit(self.args_kontrol_et_ve_doldur(self.arg_isimleri, args, baglami_yurut))
        if sonuc.geri_donmeli(): return sonuc

        deger = sonuc.kayit(interpreter.gez(self.govde_dugumleri, baglami_yurut))
        if sonuc.geri_donmeli() and sonuc.fonksiyon_donus_degeri == None: return sonuc

        donus_degeri = (deger if self.oto_geri_donmeli else None) or sonuc.fonksiyon_donus_degeri or Sayi.null
        return sonuc.basari(donus_degeri)

    def kopyala(self):
        kopyala = Fonksiyon(self.isim, self.govde_dugumleri, self.arg_isimleri, self.oto_geri_donmeli)
        kopyala.baglam_ayarla(self.baglam)
        kopyala.pos_ayarla(self.pos_baslangici, self.pos_bitisi)
        return kopyala

    def __repr__(self):
        return f"<fonksiyon {self.isim}>"


class GomuluFonksiyon(TemelFonksiyon):
    def __init__(self, isim):
        super().__init__(isim)

    def yurut(self, args):
        sonuc = RTSonucu()
        calisan_baglam = self.yeni_baglam_olustur()

        metot_ismi = f'execute_{self.isim}'
        metot = getattr(self, metot_ismi, self.olmayan_gez_metotu)

        sonuc.kayit(self.args_kontrol_et_ve_doldur(metot.arg_isimleri, args, calisan_baglam))
        if sonuc.geri_donmeli(): return sonuc

        donus_degeri = sonuc.kayit(metot(calisan_baglam))
        if sonuc.geri_donmeli(): return sonuc
        return sonuc.basari(donus_degeri)

    def olmayan_gez_metotu(self, dugum, baglam):
        raise Exception(f'execute_{self.isim} metotu tanımlanmamış')

    def kopyala(self):
        kopyala = GomuluFonksiyon(self.isim)
        kopyala.baglam_ayarla(self.baglam)
        kopyala.pos_ayarla(self.pos_baslangici, self.pos_bitisi)
        return kopyala

    def __repr__(self):
        return f"<gömülü fonksiyon {self.isim}>"

    #####################################
    # yazdırma metotu
    def execute_yazdir(self, calisan_baglam):
        print(str(calisan_baglam.sembol_tablosu.get('deger')))
        return RTSonucu().basari(Sayi.null)

    execute_yazdir.arg_isimleri = ['deger']

    # yazdırılanı döndüren metot
    def execute_yazdir_dondur(self, calisan_baglam):
        return RTSonucu().basari(String(str(calisan_baglam.sembol_tablosu.get('deger'))))

    execute_yazdir_dondur.arg_isimleri = ['deger']

    # girdi metotu
    def execute_girdi(self):
        metin = input()
        return RTSonucu().basari(String(metin))

    execute_girdi.arg_isimleri = []

    # tam sayı girdi metotu
    def execute_girdi_int(self):
        while True:
            metin = input()
            try:
                sayi = int(metin)
                break
            except ValueError:
                print(f"'{metin}' tam sayı olmalı. Tekrar deneyin!")
        return RTSonucu().basari(Sayi(sayi))

    execute_girdi_int.arg_isimleri = []

    # ekranı temizleme metotu
    def execute_temizle(self):
        os.system('cls' if os.name == 'nt' else 'cls')
        return RTSonucu().basari(Sayi.null)

    execute_temizle.arg_isimleri = []

    # değişkenin sayı olup olmadığını dönen metot
    def execute_sayi_mi(self, calisan_baglam):
        sayi_mi = isinstance(calisan_baglam.sembol_tablosu.get("deger"), Sayi)
        return RTSonucu().basari(Sayi.true if sayi_mi else Sayi.false)

    execute_sayi_mi.arg_isimleri = ["deger"]

    # değişkenin string olup olmadığını dönen metot
    def execute_string_mi(self, calisan_baglam):
        sayi_mi = isinstance(calisan_baglam.sembol_tablosu.get("deger"), String)
        return RTSonucu().basari(Sayi.true if sayi_mi else Sayi.false)

    execute_string_mi.arg_isimleri = ["deger"]

    # değişkenin liste olup olmadığını dönen metot
    def execute_liste_mi(self, calisan_baglam):
        sayi_mi = isinstance(calisan_baglam.sembol_tablosu.get("deger"), Liste)
        return RTSonucu().basari(Sayi.true if sayi_mi else Sayi.false)

    execute_liste_mi.arg_isimleri = ["deger"]

    # değişkenin fonksiyon olup olmadığını dönen metot
    def execute_fonksiyon_mu(self, calisan_baglam):
        sayi_mi = isinstance(calisan_baglam.sembol_tablosu.get("deger"), TemelFonksiyon)
        return RTSonucu().basari(Sayi.true if sayi_mi else Sayi.false)

    execute_fonksiyon_mu.arg_isimleri = ["deger"]

    # listeye eleman eklemeye yarayan metot
    def execute_ekle(self, calisan_baglam):
        liste_ = calisan_baglam.sembol_tablosu.get("liste")
        deger = calisan_baglam.sembol_tablosu.get("deger")

        if not isinstance(liste_, Liste):
            return RTSonucu().basarisiz(CalismaHatasi(
                self.pos_baslangici, self.pos_bitisi,
                "İlk değişken liste olmak zorunda",
                calisan_baglam
            ))

        liste_.elemanlar.append(deger)
        return RTSonucu().basari(Sayi.null)

    execute_ekle.arg_isimleri = ["liste", "deger"]

    # listeden eleman silmeye yarayan metot
    def execute_sil(self, calisan_baglam):
        liste_ = calisan_baglam.sembol_tablosu.get("liste")
        indeks = calisan_baglam.sembol_tablosu.get("indeks")

        if not isinstance(liste_, Liste):
            return RTSonucu().basarisiz(CalismaHatasi(
                self.pos_baslangici, self.pos_bitisi,
                "İlk değişken liste olmak zorunda",
                calisan_baglam
            ))

        if not isinstance(indeks, Sayi):
            return RTSonucu().basarisiz(CalismaHatasi(
                self.pos_baslangici, self.pos_bitisi,
                "İkinci değişken sayı olmak zorunda",
                calisan_baglam
            ))

        try:
            eleman = liste_.elemanlar.pop(indeks.deger)
        except:
            return RTSonucu().basarisiz(CalismaHatasi(
                self.pos_baslangici, self.pos_bitisi,
                'Bu indeksteki öğe, indeks sınırlarının dışında olduğundan listeden kaldırılamadı.',
                calisan_baglam
            ))
        return RTSonucu().basari(eleman)

    execute_sil.arg_isimleri = ["liste", "indeks"]

    # iki listeyi birbiriyle birleştirmeye yarayan metot
    def execute_extend(self, calisan_baglam):
        listeA = calisan_baglam.sembol_tablosu.get("listeA")
        listeB = calisan_baglam.sembol_tablosu.get("listeB")

        if not isinstance(listeA, Liste):
            return RTSonucu().basarisiz(CalismaHatasi(
                self.pos_baslangici, self.pos_bitisi,
                "İlk değişken liste olmak zorunda",
                calisan_baglam
            ))

        if not isinstance(listeB, Liste):
            return RTSonucu().basarisiz(CalismaHatasi(
                self.pos_baslangici, self.pos_bitisi,
                "İkinci değişken liste olmak zorunda",
                calisan_baglam
            ))

        listeA.elemanlar.extend(listeB.elemanlar)
        return RTSonucu().basari(Sayi.null)

    execute_extend.arg_isimleri = ["listeA", "listeB"]

    # listenin uzunluğunu veren fonksiyon
    def execute_uzunluk(self, calisan_baglam):
        liste_ = calisan_baglam.sembol_tablosu.get("liste")

        if not isinstance(liste_, Liste):
            return RTSonucu().basarisiz(CalismaHatasi(
                self.pos_baslangici, self.pos_bitisi,
                "Değişken liste olmak zorunda",
                calisan_baglam
            ))

        return RTSonucu().basari(Sayi(len(liste_.elemanlar)))

    execute_uzunluk.arg_isimleri = ["liste"]

    # çalıştırma fonksiyonu
    def execute_calistir(self, calisan_baglam):
        dosya_adi = calisan_baglam.sembol_tablosu.get("dosya_adi")

        if not isinstance(dosya_adi, String):
            return RTSonucu().basarisiz(CalismaHatasi(
                self.pos_baslangici, self.pos_bitisi,
                "İkinci değişken string olmak zorunda",
                calisan_baglam
            ))

        dosya_adi = dosya_adi.deger

        try:
            with open(dosya_adi, "r") as dosya:
                kodlar = dosya.read()
        except Exception as e:
            return RTSonucu().basarisiz(CalismaHatasi(
                self.pos_baslangici, self.pos_bitisi,
                f"Yüklerken sorun oluştu \"{dosya_adi}\"\n" + str(e),
                calisan_baglam
            ))

        _, hata = baslat(dosya_adi, kodlar)

        if hata:
            return RTSonucu().basarisiz(CalismaHatasi(
                self.pos_baslangici, self.pos_bitisi,
                f"Yürütmeyi bitirirken sorun oluştu \"{dosya_adi}\"\n" +
                hata.goster(),
                calisan_baglam
            ))

        return RTSonucu().basari(Sayi.null)

    execute_calistir.arg_isimleri = ["dosya_adi"]


GomuluFonksiyon.print = GomuluFonksiyon("print")
GomuluFonksiyon.print_ret = GomuluFonksiyon("print_ret")
GomuluFonksiyon.input = GomuluFonksiyon("input")
GomuluFonksiyon.input_int = GomuluFonksiyon("input_int")
GomuluFonksiyon.clear = GomuluFonksiyon("clear")
GomuluFonksiyon.is_number = GomuluFonksiyon("is_number")
GomuluFonksiyon.is_string = GomuluFonksiyon("is_string")
GomuluFonksiyon.is_list = GomuluFonksiyon("is_list")
GomuluFonksiyon.is_function = GomuluFonksiyon("is_function")
GomuluFonksiyon.append = GomuluFonksiyon("append")
GomuluFonksiyon.pop = GomuluFonksiyon("pop")
GomuluFonksiyon.extend = GomuluFonksiyon("extend")
GomuluFonksiyon.len = GomuluFonksiyon("len")
GomuluFonksiyon.run = GomuluFonksiyon("run")


# Baglam(Context)
# Bu sınıf, programın mevcut bağlamını tutacak,
# böylece şu anda bir fonksiyonun içindeysek veya herhangi bir fonksiyonun içinde değilsek bağlam bir fonksiyon olabilir,
# o zaman bağlam programın tamamı olacaktır.

class Baglam:
    def __init__(self, goruntu_adi, parent=None, parent_giris_konumu=None):
        self.goruntu_adi = goruntu_adi
        self.parent = parent
        self.parent_giris_konumu = parent_giris_konumu
        self.sembol_tablosu = None


# Sembol tablosu
# Sembol tablosu bütü değişken isimlerini ve onların değerlerini tutacak

class SembolTablosu:
    def __init__(self, parent=None):
        # Semboller sözlüğü oluşturuyorum
        # bir fonksiyon çağrıldığında yeni bir sembol tablosu oluşturuyor,
        # böylece o fonksiyona atanmış tüm değişkenleri saklayacak olan semboller ve bu fonksiyon
        # tamamlandıktan sonra sembol tablosu yok olu ve hepsi artık kullanılamaz durumda olur
        # ama aynı zamanda bu sembol tablosunun bir parenti olacak
        # bu global sembol tablosu olacak, böylece koddaki tüm global değişkenlere sahip olacak,
        # böylece bunlara kodun herhangi bir yerinden erişilebilir.
        self.semboller = {}
        self.parent = parent

    # get ve set metotları
    def get(self, isim):
        deger = self.semboller.get(isim, None)
        if deger == None and self.parent:
            return self.parent.get(isim)
        return deger

    def set(self, isim, deger):
        self.semboller[isim] = deger

    def sil(self, isim):
        del self.semboller[isim]


# INTERPRETER

class Interpreter:
    # Bu metot, o düğümü işleyecek ve ardından tüm alt düğümleri ziyaret edecek.
    def gez(self, dugum, baglam):
        # metot ismini almak için
        metot_ismi = f'gez_{type(dugum).__name__}'
        metot = getattr(self, metot_ismi, self.metot_yok)
        return metot(dugum, baglam)

    # Eğer o isimde bir metot yoksa
    def metot_yok(self, dugum, baglam):
        raise Exception(f'gez_{type(dugum).__name__} metodu tanımlı değil')

    # Her düğüm türü için gez metodu tanımlıyorum

    def gez_SayiDugumu(self, dugum, baglam):
        return RTSonucu().basari(
            Sayi(dugum.token.deger).baglam_ayarla(baglam).pos_ayarla(dugum.pos_baslangici, dugum.pos_bitisi)
        )

    def gez_StringDugumu(self, dugum, baglam):
        return RTSonucu().basari(
            String(dugum.token.deger).baglam_ayarla(baglam).pos_ayarla(dugum.pos_baslangici, dugum.pos_bitisi)
        )

    def gez_ListeDugumu(self, dugum, baglam):
        sonuc = RTSonucu()
        elemanlar = []

        for eleman_dugumu in dugum.elemanlar_dugumu:
            elemanlar.append(sonuc.kayit(self.gez(eleman_dugumu, baglam)))
            if sonuc.geri_donmeli(): return sonuc

        return sonuc.basari(
            Liste(elemanlar).baglam_ayarla(baglam).pos_ayarla(dugum.pos_baslangici, dugum.pos_bitisi)
        )

    def gez_DegiskenErisimDugumu(self, dugum, baglam):
        sonuc = RTSonucu()
        degisken_ismi = dugum.degisken_ismi_tokeni.deger
        deger = baglam.sembol_tablosu.get(degisken_ismi)
        # Eğer o değişken tanımlanmamışsa
        if not deger:
            return sonuc.basarisiz(CalismaHatasi(
                dugum.pos_baslangici, dugum.pos_bitisi,
                f"'{degisken_ismi}' tanımlanmamış",
                baglam
            ))

        deger = deger.kopyala().pos_ayarla(dugum.pos_baslangici, dugum.pos_bitisi).baglam_ayarla(baglam)
        return sonuc.basari(deger)

    def gez_DegiskenAtamaDugumu(self, dugum, baglam):
        sonuc = RTSonucu()
        degisken_ismi = dugum.degisken_ismi_tokeni.deger
        deger = sonuc.kayit(self.gez(dugum.deger_dugumu, baglam))
        if sonuc.geri_donmeli(): return sonuc

        baglam.sembol_tablosu.set(degisken_ismi, deger)
        return sonuc.basari(deger)

    def gez_IkiliOpDugumu(self, dugum, baglam):
        sonuc = RTSonucu()
        # Ayrıca sol ve sağ düğümlerini de ziyaret etmemiz gerekiyor
        # operatöre bakmamız ve bu operatörden hangi işlemin gerçekleştirileceğini belirlememiz gerekiyor.
        sol = sonuc.kayit(self.gez(dugum.sol_dugum, baglam))
        if sonuc.geri_donmeli(): return sonuc
        sag = sonuc.kayit(self.gez(dugum.sag_dugum, baglam))
        if sonuc.geri_donmeli(): return sonuc
        # hangi fonksiyonun çağrılması gerektiğini belirlemek için düğümün operatör token'ını kontrol ediyoruz.
        if dugum.op_tok.token_turu == TOKEN_TOPLAMA:
            sonuc, hata = sol.toplama(sag)
        elif dugum.op_tok.token_turu == TOKEN_CIKARMA:
            sonuc, hata = sol.cikarma(sag)
        elif dugum.op_tok.token_turu == TOKEN_CARPMA:
            sonuc, hata = sol.carpma(sag)
        elif dugum.op_tok.token_turu == TOKEN_BOLME:
            sonuc, hata = sol.bolme(sag)
        elif dugum.op_tok.token_turu == TOKEN_USALMA:
            sonuc, hata = sol.us_alma(sag)
        elif dugum.op_tok.token_turu == TOKEN_EE:
            sonuc, hata = sol.get_karsilastirma_esittir(sag)
        elif dugum.op_tok.token_turu == TOKEN_ED:
            sonuc, hata = sol.get_karsilastirma_esit_degildir(sag)
        elif dugum.op_tok.token_turu == TOKEN_KUCUKTUR:
            sonuc, hata = sol.get_karsilastirma_kucuktur(sag)
        elif dugum.op_tok.token_turu == TOKEN_BUYUKTUR:
            sonuc, hata = sol.get_karsilastirma_buyuktur(sag)
        elif dugum.op_tok.token_turu == TOKEN_KUCUKEE:
            sonuc, hata = sol.get_karsilastirma_kucuk_esittir(sag)
        elif dugum.op_tok.token_turu == TOKEN_BUYUKEE:
            sonuc, hata = sol.get_karsilastirma_buyuk_esittir(sag)
        elif dugum.op_tok.eslesme(TOKEN_KEYWORD, 'AND'):
            sonuc, hata = sol.ve_ifadesi(sag)
        elif dugum.op_tok.eslesme(TOKEN_KEYWORD, 'OR'):
            sonuc, hata = sol.veya_ifadesi(sag)

        if hata:
            return sonuc.basarisiz(hata)
        else:
            return sonuc.basari(sonuc.pos_ayarla(dugum.pos_baslangici, dugum.pos_bitisi))

    def gez_TekliOpDugumu(self, dugum, baglam):
        sonuc = RTSonucu()
        sayi = sonuc.kayit(self.gez(dugum.dugum, baglam))
        if sonuc.geri_donmeli(): return sonuc

        hata = None
        # Eğer operator tokeni eksi ise -1 ile çarpılmış olması gerekir
        if dugum.op_tok.token_turu == TOKEN_CIKARMA:
            sayi, hata = sayi.carpma(Sayi(-1))
            # Eğer operator tokeni not ile eşlesiyosa değilini alıyoruz
        elif dugum.op_tok.eslesme(TOKEN_KEYWORD, 'NOT'):
            sayi, hata = sayi.degil_ifadesi()

        if hata:
            return sonuc.basarisiz(hata)
        else:
            return sonuc.basari(sayi.pos_ayarla(dugum.pos_baslangici, dugum.pos_bitisi))

    def gez_IfDugumu(self, dugum, baglam):
        sonuc = RTSonucu()
        # Burada durumlarda koşul ve ifadeleri gezecek ve koşul değeri olarak kaydedecek
        for kosul, ifade, null_dondurmeli in dugum.durumlar:
            kosul_degeri = sonuc.kayit(self.gez(kosul, baglam))
            if sonuc.geri_donmeli(): return sonuc
            # Eğer koşul değeri 0'a eşit değil ise ifade değerini kaydedip başarılı şekilde dönecek
            if kosul_degeri.is_true():
                ifade_degeri = sonuc.kayit(self.gez(ifade, baglam))
                if sonuc.geri_donmeli(): return sonuc
                return sonuc.basari(Sayi.null if null_dondurmeli else ifade_degeri)

        if dugum.else_durumu:
            ifade, null_dondurmeli = dugum.else_durumu
            ifade_degeri = sonuc.kayit(self.gez(ifade, baglam))
            if sonuc.geri_donmeli(): return sonuc
            return sonuc.basari(Sayi.null if null_dondurmeli else ifade_degeri)

        return sonuc.basari(Sayi.null)

    def gez_ForDugumu(self, dugum, baglam):
        sonuc = RTSonucu()
        elemanlar = []

        baslangic_degeri = sonuc.kayit(self.gez(dugum.baslangic_degeri_dugumu, baglam))
        if sonuc.geri_donmeli(): return sonuc

        bitis_degeri = sonuc.kayit(self.gez(dugum.bitis_degeri_dugumu, baglam))
        if sonuc.geri_donmeli(): return sonuc

        if dugum.adim_degeri_dugumu:
            adim_degeri = sonuc.kayit(self.gez(dugum.adim_degeri_dugumu, baglam))
            if sonuc.geri_donmeli(): return sonuc
        else:
            adim_degeri = Sayi(1)

        i = baslangic_degeri.deger
        # adım değeri pozitif veya negatif olabilir
        # eğer adım değeri pozitifse başlangıç değeri bitiş değerinden küçük olmalı negatifse tam tersi durum
        if adim_degeri.deger >= 0:
            kosul = lambda: i < bitis_degeri.deger
        else:
            kosul = lambda: i > bitis_degeri.deger
        # döngü kısmında başlangıç değeri adım değerine göre değiştirilir
        while kosul():
            baglam.sembol_tablosu.set(dugum.degisken_ismi_tokeni.deger, Sayi(i))
            i += adim_degeri.deger

            deger = sonuc.kayit(self.gez(dugum.govde_dugumu, baglam))
            if sonuc.geri_donmeli() and sonuc.dongu_devam_etmeli == False and sonuc.donguden_cikilmali == False: return sonuc

            if sonuc.dongu_devam_etmeli:
                continue

            if sonuc.donguden_cikilmali:
                break

            elemanlar.append(deger)

        return sonuc.basari(
            Sayi.null if dugum.null_dondurmeli else
            Liste(elemanlar).baglam_ayarla(baglam).pos_ayarla(dugum.pos_baslangici, dugum.pos_bitisi)
        )

    def gez_WhileDugumu(self, dugum, baglam):
        sonuc = RTSonucu()
        elemanlar = []

        while True:
            kosul = sonuc.kayit(self.gez(dugum.kosul_dugumu, baglam))
            if sonuc.geri_donmeli(): return sonuc
            # koşul 0 ise döngüden çık
            if not kosul.is_true():
                break

            deger = sonuc.kayit(self.gez(dugum.govde_dugumu, baglam))
            if sonuc.geri_donmeli() and sonuc.dongu_devam_etmeli == False and sonuc.donguden_cikilmali == False: return sonuc

            if sonuc.dongu_devam_etmeli:
                continue

            if sonuc.donguden_cikilmali:
                break

            elemanlar.append(deger)

        return sonuc.basari(
            Sayi.null if dugum.null_dondurmeli else
            Liste(elemanlar).baglam_ayarla(baglam).pos_ayarla(dugum.pos_baslangici, dugum.pos_bitisi)
        )

    def gez_FonksiyonTanimiDugumu(self, dugum, baglam):
        sonuc = RTSonucu()

        fonksiyon_ismi = dugum.degisken_ismi_tokeni.deger if dugum.degisken_ismi_tokeni else None
        govde_dugumu = dugum.govde_dugumu
        arg_isimleri = [arg_ismi.deger for arg_ismi in dugum.arg_ismi_tokeni]
        fonksiyon_degeri = Fonksiyon(fonksiyon_ismi, govde_dugumu, arg_isimleri, dugum.oto_geri_donmeli).baglam_ayarla(
            baglam).pos_ayarla(
            dugum.pos_baslangici, dugum.pos_bitisi)

        if dugum.degisken_ismi_tokeni:
            baglam.sembol_tablosu.set(fonksiyon_ismi, fonksiyon_degeri)

        return sonuc.basari(fonksiyon_degeri)

    def gez_CagirmaDugumu(self, dugum, baglam):
        sonuc = RTSonucu()
        args = []

        cagrilacak_deger = sonuc.kayit(self.gez(dugum.cagrilacak_dugum, baglam))
        if sonuc.geri_donmeli(): return sonuc
        cagrilacak_deger = cagrilacak_deger.kopyala().pos_ayarla(dugum.pos_baslangici, dugum.pos_bitisi)

        for arg_dugumu in dugum.arg_dugumleri:
            args.append(sonuc.kayit(self.gez(arg_dugumu, baglam)))
            if sonuc.geri_donmeli(): return sonuc

        deger_don = sonuc.kayit(cagrilacak_deger.yurut(args))
        if sonuc.geri_donmeli(): return sonuc
        deger_don = deger_don.kopyala().pos_ayarla(dugum.pos_baslangici, dugum.pos_bitisi).baglam_ayarla(baglam)
        return sonuc.basari(deger_don)

    def gez_ReturnDugumu(self, dugum, baglam):
        sonuc = RTSonucu()

        if dugum.donus_dugumu:
            deger = sonuc.kayit(self.gez(dugum.donus_dugumu, baglam))
            if sonuc.geri_donmeli(): return sonuc
        else:
            deger = Sayi.null

        return sonuc.basari_return(deger)

    def gez_ContinueDugumu(self):
        return RTSonucu().basari_continue()

    def gez_BreakDugumu(self):
        return RTSonucu().basari_break()


# çalıştırma kısmı
# Global Sembol Tablosu
global_sembol_tablosu = SembolTablosu()
global_sembol_tablosu.set("NULL", Sayi.null)
global_sembol_tablosu.set("FALSE", Sayi.false)
global_sembol_tablosu.set("TRUE", Sayi.true)
global_sembol_tablosu.set("MATH_PI", Sayi.math_PI)
global_sembol_tablosu.set("PRINT", GomuluFonksiyon.print)
global_sembol_tablosu.set("PRINT_RET", GomuluFonksiyon.print_ret)
global_sembol_tablosu.set("INPUT", GomuluFonksiyon.input)
global_sembol_tablosu.set("INPUT_INT", GomuluFonksiyon.input_int)
global_sembol_tablosu.set("CLEAR", GomuluFonksiyon.clear)
global_sembol_tablosu.set("CLS", GomuluFonksiyon.clear)
global_sembol_tablosu.set("IS_NUM", GomuluFonksiyon.is_number)
global_sembol_tablosu.set("IS_STR", GomuluFonksiyon.is_string)
global_sembol_tablosu.set("IS_LIST", GomuluFonksiyon.is_list)
global_sembol_tablosu.set("IS_FUN", GomuluFonksiyon.is_function)
global_sembol_tablosu.set("APPEND", GomuluFonksiyon.append)
global_sembol_tablosu.set("POP", GomuluFonksiyon.pop)
global_sembol_tablosu.set("EXTEND", GomuluFonksiyon.extend)
global_sembol_tablosu.set("LEN", GomuluFonksiyon.len)
global_sembol_tablosu.set("RUN", GomuluFonksiyon.run)


# Çalıştır
# Bu metot metin alıp çalıştıracak.
def baslat(dosya_adi, metin):
    # Yeni bir lexer oluşturuyoruz
    lexer = Lexer(dosya_adi, metin)
    tokenler, hata = lexer.token_olustur()
    if hata: return None, hata

    # Soyut syntax ağacını oluşturuyoruz
    parser = Parser(tokenler)
    ssa = parser.cozumle()
    if ssa.hata: return None, ssa.hata

    # Programı çalıştır
    interpreter = Interpreter()
    baglam = Baglam('<program>')
    baglam.sembol_tablosu = global_sembol_tablosu
    sonuc = interpreter.gez(ssa.dugum, baglam)

    return sonuc.deger, sonuc.hata
