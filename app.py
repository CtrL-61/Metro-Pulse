# Metro Pulse - Çok Şehirli Metro Rota Planlayıcı
# Bu proje eğitim amaçlıdır. Süre/doluluk verileri simülasyon amaçlı üretilmektedir.
# Durak koordinatları, hattın gerçek güzergahını yansıtacak şekilde yaklaşık olarak
# (harita üzerinde doğru bölgeye/konuma denk gelecek şekilde) girilmiştir.

import networkx as nx
import os
import random
from flask import Flask, render_template, request

#1. AYARLAR
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app = app  # Vercel için

#2. DURAK EŞLEŞTİRME (STATION MAPPING) - İBB API isimlerini graf isimlerine çevirir
STATION_MAPPING = {
    "YENIKAPI STATION": "Yenikapı",
    "MECIDIYEKOY STATION": "Şişli-Mecidiyeköy",
    "HALIC STATION": "Haliç",
    "TAKISM STATION": "Taksim",
    "USKUDAR STATION": "Üsküdar",
    "KADIKOY STATION": "Kadıköy",
    "SABIHA GOKCEN AIRPORT": "Sabiha Gökçen Havalimanı",
    # Yeni duraklar eklendikçe burayı güncelleyebilirsin.
}

#3. YARDIMCI FONKSİYONLAR
def get_announcement(lang):
    if lang == 'tr':
        return "Sistem normal: Tüm hatlar seferlerine devam etmektedir."
    return "System normal: All lines are operating on schedule."

def get_live_info(durak_adi):
    """API verisini durak isimlerine göre filtreler (canlı veri simülasyonu)."""
    api_karsiligi = next((k for k, v in STATION_MAPPING.items() if v == durak_adi), durak_adi)
    return {
        'dakika': random.randint(2, 12),
        'doluluk': random.choice(['Düşük', 'Orta', 'Yüksek']),
        'api_name': api_karsiligi
    }

# DİL SÖZLÜĞÜ
LANGUAGES = {
    'tr': {
        'title': 'Metro Pulse',
        'subtitle': 'Şehir İçi Rota Planlama',
        'departure': 'KALKIŞ DURAĞI',
        'destination': 'VARIŞ DURAĞI',
        'button': 'ROTA BUL',
        'error_path': 'Üzgünüz, bu iki durak arasında bir metro bağlantısı bulunamadı.',
        'error_same': 'Aynı durağı seçtiniz!'
    },
    'en': {
        'title': 'Metro Pulse',
        'subtitle': 'City Route Planning',
        'departure': 'DEPARTURE STATION',
        'destination': 'DESTINATION STATION',
        'button': 'FIND ROUTE',
        'error_path': 'Sorry, no metro connection found between these stations.',
        'error_same': 'You selected the same station!'
    }
}

#4. ŞEHİR / GRAF YAPISI
# Her şehrin kendi grafı ve durak koordinatları vardır. Bu sayede uygulama
# tek bir ülkeyle sınırlı kalmadan "küresel" olarak büyüyebilir.
CITIES = {
    'istanbul': {
        'name_tr': 'İstanbul',
        'name_en': 'Istanbul',
        'graph': nx.Graph(),
        'coords': {}
    },
    'ankara': {
        'name_tr': 'Ankara',
        'name_en': 'Ankara',
        'graph': nx.Graph(),
        'coords': {}
    },
}

CITY_ORDER = ['istanbul', 'ankara']  # Sekme sırası


def hat_ekle(city_key, hat_kodu, durak_metni, toplam_sure, coords=None):
    """
    Bir hattı, verilen şehrin grafına ekler.
    coords: {'Durak Adı': (lat, lon), ...} şeklinde, o hatta ait yeni durakların
    gerçek/yaklaşık koordinatlarını barındırır. Zaten eklenmiş bir durak
    (aktarma noktası) tekrar geçilirse coords'ta olmasına gerek yoktur.
    """
    G = CITIES[city_key]['graph']
    duraklar = [d.strip() for d in durak_metni.split(',')]
    sure = toplam_sure / (len(duraklar) - 1)
    for i in range(len(duraklar) - 1):
        G.add_edge(duraklar[i], duraklar[i + 1], weight=sure, hat=hat_kodu)
    if coords:
        CITIES[city_key]['coords'].update(coords)


# ======================================================================
# İSTANBUL HAT VERİLERİ
# ======================================================================
hat_ekle("istanbul", "M1A",
    "Yenikapı, Aksaray, Emniyet-Fatih, Topkapı-Ulubatlı, Bayrampaşa, Sağmalcılar, Kocatepe, Otogar, Terazidere, Davutpaşa, Merter, Zeytinburnu, Bakırköy-İncirli, Bahçelievler, Ataköy-Şirinevler, Yenibosna, DTM-İstanbul Fuar Merkezi, Atatürk Havalimanı",
    35,
    coords={
        "Yenikapı": (41.0052, 28.9498), "Aksaray": (41.0136, 28.9558),
        "Emniyet-Fatih": (41.0186, 28.9445), "Topkapı-Ulubatlı": (41.0192, 28.9270),
        "Bayrampaşa": (41.0356, 28.9145), "Sağmalcılar": (41.0400, 28.9050),
        "Kocatepe": (41.0330, 28.8950), "Otogar": (41.0270, 28.8890),
        "Terazidere": (41.0180, 28.8850), "Davutpaşa": (41.0130, 28.8800),
        "Merter": (41.0000, 28.8850), "Zeytinburnu": (40.9930, 28.9050),
        "Bakırköy-İncirli": (40.9870, 28.8650), "Bahçelievler": (40.9950, 28.8550),
        "Ataköy-Şirinevler": (40.9850, 28.8350), "Yenibosna": (40.9930, 28.8450),
        "DTM-İstanbul Fuar Merkezi": (40.9820, 28.8250), "Atatürk Havalimanı": (40.9770, 28.8150),
    })

hat_ekle("istanbul", "M2",
    "Yenikapı, Vezneciler, Haliç, Şişhane, Taksim, Osmanbey, Şişli-Mecidiyeköy, Gayrettepe, Levent, 4. Levent, Sanayi Mahallesi, İTÜ-Ayazağa, Atatürk Oto Sanayi, Darüşşafaka, Hacıosman",
    32,
    coords={
        "Vezneciler": (41.0110, 28.9600), "Haliç": (41.0250, 28.9650),
        "Şişhane": (41.0280, 28.9740), "Taksim": (41.0370, 28.9850),
        "Osmanbey": (41.0480, 28.9870), "Şişli-Mecidiyeköy": (41.0630, 28.9950),
        "Gayrettepe": (41.0680, 29.0080), "Levent": (41.0820, 29.0130),
        "4. Levent": (41.0880, 29.0180), "Sanayi Mahallesi": (41.0980, 29.0250),
        "İTÜ-Ayazağa": (41.1050, 29.0230), "Atatürk Oto Sanayi": (41.1080, 29.0300),
        "Darüşşafaka": (41.1150, 29.0380), "Hacıosman": (41.1200, 29.0400),
    })

hat_ekle("istanbul", "Marmaray",
    "Halkalı, Florya, Bakırköy, Kazlıçeşme, Yenikapı, Sirkeci, Üsküdar, Ayrılık Çeşmesi, Söğütlüçeşme, Bostancı, Kartal, Pendik, Gebze",
    108,
    coords={
        "Halkalı": (41.0350, 28.7850), "Florya": (40.9800, 28.7850),
        "Bakırköy": (40.9770, 28.8720), "Kazlıçeşme": (41.0010, 28.9150),
        "Sirkeci": (41.0130, 28.9770), "Üsküdar": (41.0230, 29.0150),
        "Ayrılık Çeşmesi": (41.0000, 29.0280), "Söğütlüçeşme": (40.9900, 29.0330),
        "Bostancı": (40.9550, 29.0930), "Kartal": (40.9050, 29.1900),
        "Pendik": (40.8780, 29.2350), "Gebze": (40.8020, 29.4300),
    })

hat_ekle("istanbul", "M4",
    "Kadıköy, Ayrılık Çeşmesi, Acıbadem, Ünalan, Göztepe, Yenisahra, Kozyatağı, Bostancı, Küçükyalı, Maltepe, Huzurevi, Gülsuyu, Esenkent, Hospital-Adliye, Soğanlık, Kartal, Yakacık-Adnan Kahveci, Pendik, Tavşantepe, Fevzi Çakmak-Hastane, Yayalar-Şeyhli, Kurtköy, Sabiha Gökçen Havalimanı",
    50,
    coords={
        "Kadıköy": (40.9910, 29.0270), "Acıbadem": (41.0050, 29.0400),
        "Ünalan": (41.0000, 29.0550), "Göztepe": (40.9800, 29.0600),
        "Yenisahra": (40.9750, 29.0900), "Kozyatağı": (40.9700, 29.1000),
        "Küçükyalı": (40.9450, 29.1150), "Maltepe": (40.9350, 29.1300),
        "Huzurevi": (40.9300, 29.1450), "Gülsuyu": (40.9250, 29.1550),
        "Esenkent": (40.9200, 29.1650), "Hospital-Adliye": (40.9150, 29.1800),
        "Soğanlık": (40.9050, 29.1900), "Yakacık-Adnan Kahveci": (40.8900, 29.2000),
        "Tavşantepe": (40.8700, 29.2500), "Fevzi Çakmak-Hastane": (40.8850, 29.2700),
        "Yayalar-Şeyhli": (40.8950, 29.2900), "Kurtköy": (40.9050, 29.3200),
        "Sabiha Gökçen Havalimanı": (40.8986, 29.3092),
    })

# ======================================================================
# ANKARA HAT VERİLERİ (M1, M2, M3, M4, A1 Ankaray)
# Durak isimleri ve sıralaması güncel EGO/Ankara Metrosu hat bilgilerine
# dayanmaktadır. Koordinatlar, hattın gerçek güzergahını takip edecek
# şekilde yaklaşık olarak girilmiştir.
# ======================================================================

# M1: Batıkent -> Kızılay
hat_ekle("ankara", "M1",
    "Batıkent, OSTİM, Macunköy, Hastane, Demetevler, Yenimahalle, İvedik, Akköprü, Atatürk Kültür Merkezi, Ulus, Sıhhiye, Kızılay",
    25,
    coords={
        "Batıkent": (39.9950, 32.7495), "OSTİM": (39.9870, 32.7550),
        "Macunköy": (39.9800, 32.7650), "Hastane": (39.9720, 32.7750),
        "Demetevler": (39.9650, 32.7850), "Yenimahalle": (39.9700, 32.7970),
        "İvedik": (39.9610, 32.8000), "Akköprü": (39.9550, 32.8120),
        "Atatürk Kültür Merkezi": (39.9480, 32.8390), "Ulus": (39.9400, 32.8547),
        "Sıhhiye": (39.9280, 32.8558), "Kızılay": (39.9208, 32.8541),
    })

# M2: Kızılay -> Koru
hat_ekle("ankara", "M2",
    "Kızılay, Necatibey, Milli Kütüphane, Söğütözü, MTA, ODTÜ, Bilkent, Tarım Bakanlığı, Beytepe, Ümitköy, Çayyolu, Koru",
    24,
    coords={
        "Necatibey": (39.9150, 32.8460), "Milli Kütüphane": (39.9100, 32.8350),
        "Söğütözü": (39.9080, 32.8100), "MTA": (39.9020, 32.7850),
        "ODTÜ": (39.8950, 32.7600), "Bilkent": (39.8850, 32.7350),
        "Tarım Bakanlığı": (39.8950, 32.7150), "Beytepe": (39.8650, 32.7350),
        "Ümitköy": (39.8950, 32.6950), "Çayyolu": (39.8850, 32.6700),
        "Koru": (39.8800, 32.6550),
    })

# M3: Batıkent -> OSB-Törekent
hat_ekle("ankara", "M3",
    "Batıkent, Batı Merkez, MESA, Botanik, İstanbul Yolu, Eryaman 1-2, Eryaman 5, Devlet Mahallesi, Harikalar Diyarı, Fatih, GOP, OSB-Törekent",
    22,
    coords={
        "Batı Merkez": (39.9970, 32.7350), "MESA": (39.9990, 32.7200),
        "Botanik": (40.0010, 32.7050), "İstanbul Yolu": (40.0030, 32.6900),
        "Eryaman 1-2": (40.0050, 32.6700), "Eryaman 5": (40.0070, 32.6550),
        "Devlet Mahallesi": (40.0000, 32.6400), "Harikalar Diyarı": (39.9950, 32.6250),
        "Fatih": (39.9900, 32.6100), "GOP": (39.9850, 32.5950),
        "OSB-Törekent": (39.9800, 32.5800),
    })

# M4: Kızılay -> Şehitler (Keçiören)
hat_ekle("ankara", "M4",
    "Kızılay, Adliye, Gar, Atatürk Kültür Merkezi, ASKİ, Dışkapı, Meteoroloji, Belediye, Mecidiye, Kuyubaşı, Dutluk, Şehitler",
    21,
    coords={
        "Adliye": (39.9300, 32.8560), "Gar": (39.9430, 32.8480),
        "ASKİ": (39.9550, 32.8420), "Dışkapı": (39.9620, 32.8450),
        "Meteoroloji": (39.9700, 32.8480), "Belediye": (39.9780, 32.8510),
        "Mecidiye": (39.9850, 32.8540), "Kuyubaşı": (39.9920, 32.8570),
        "Dutluk": (39.9990, 32.8600), "Şehitler": (40.0060, 32.8630),
    })

# A1 Ankaray: AŞTİ -> Dikimevi
hat_ekle("ankara", "A1",
    "AŞTİ, Emek, Bahçelievler, Beşevler, Tandoğan, Maltepe, Demirtepe, Kızılay, Kolej, Kurtuluş, Dikimevi",
    14,
    coords={
        "AŞTİ": (39.9282, 32.7986), "Emek": (39.9250, 32.8100),
        "Bahçelievler": (39.9230, 32.8220), "Beşevler": (39.9240, 32.8340),
        "Tandoğan": (39.9230, 32.8420), "Maltepe": (39.9250, 32.8480),
        "Demirtepe": (39.9220, 32.8510), "Kolej": (39.9230, 32.8650),
        "Kurtuluş": (39.9250, 32.8750), "Dikimevi": (39.9280, 32.8850),
    })


def get_city_key(request_obj, source='args'):
    """İstek içinden geçerli şehir anahtarını okur, yoksa istanbul'a düşer."""
    getter = request_obj.args.get if source == 'args' else request_obj.form.get
    city = getter('city', 'istanbul')
    return city if city in CITIES else 'istanbul'


def city_names_for(lang):
    """Şehir seçim sekmesi için {key: görünen_ad} sözlüğü üretir."""
    field = 'name_tr' if lang == 'tr' else 'name_en'
    return {key: CITIES[key][field] for key in CITY_ORDER}


#5. ROUTE'LAR
@app.route('/')
def index():
    lang = request.args.get('lang', 'tr')
    texts = LANGUAGES.get(lang, LANGUAGES['tr'])
    city = get_city_key(request, source='args')
    G = CITIES[city]['graph']
    durak_listesi = sorted(list(G.nodes()))
    announcement = get_announcement(lang)

    return render_template('index.html',
                           duraklar=durak_listesi,
                           texts=texts,
                           current_lang=lang,
                           current_city=city,
                           cities=city_names_for(lang),
                           announcement=announcement)


@app.route('/arama', methods=['POST'])
def arama():
    lang = request.form.get('lang', 'tr')
    texts = LANGUAGES.get(lang, LANGUAGES['tr'])
    city = get_city_key(request, source='form')
    G = CITIES[city]['graph']
    coords = CITIES[city]['coords']

    try:
        bas = request.form.get('baslangic', '').strip()
        hed = request.form.get('hedef', '').strip()
        print(f"Arama yapılıyor [{city}]: {bas} -> {hed}")

        if not bas or not hed:
            return render_template('index.html', duraklar=sorted(list(G.nodes())),
                                    texts=texts, current_lang=lang, current_city=city,
                                    cities=city_names_for(lang))

        if bas not in G or hed not in G:
            missing = []
            if bas not in G: missing.append(f"'{bas}'")
            if hed not in G: missing.append(f"'{hed}'")
            print(f"Hata: Durak bulunamadı -> {missing}")
            return render_template('hata.html', message=texts['error_path'], texts=texts,
                                    current_lang=lang, current_city=city)

        if bas == hed:
            return render_template('hata.html', message=texts['error_same'], texts=texts,
                                    current_lang=lang, current_city=city)

        yol = nx.shortest_path(G, source=bas, target=hed, weight='weight')
        sure = nx.shortest_path_length(G, source=bas, target=hed, weight='weight')

        rota_detay = []
        onceki_hat = None

        for i in range(len(yol)):
            durak = yol[i]
            su_anki_hat = ""
            if i < len(yol) - 1:
                su_anki_hat = G[yol[i]][yol[i + 1]]['hat']

            if onceki_hat and su_anki_hat and onceki_hat != su_anki_hat:
                sure += 5
                lat, lon = coords.get(durak, (None, None))
                rota_detay.append({'durak': durak, 'hat': 'Aktarma', 'lat': lat, 'lon': lon})

            lat, lon = coords.get(durak, (None, None))
            rota_detay.append({'durak': durak, 'hat': su_anki_hat, 'lat': lat, 'lon': lon})
            onceki_hat = su_anki_hat

        res = {
            'toplam_sure': round(sure),
            'rota': rota_detay
        }

        live_info = get_live_info(bas)
        announcement = get_announcement(lang)

        return render_template('sonuc.html',
                               rota_sonucu=res,
                               baslangic=bas,
                               hedef=hed,
                               texts=texts,
                               current_lang=lang,
                               current_city=city,
                               live_info=live_info,
                               announcement=announcement)

    except Exception as e:
        print(f"Hata oluştu: {e}")
        return render_template('hata.html', texts=texts, current_lang=lang, current_city=city)


if __name__ == "__main__":
    app.run(debug=True)
