from core.domain.interfaces import RegionRepository, Province, Regency, District


class EmbeddedRegionRepository(RegionRepository):
    """
    Embedded region data repository.
    Data sourced from: https://github.com/yusufsyaifudin/wilayah-indonesia
    """

    # Embedded province data
    _PROVINCES = {
        "11": Province("11", "Aceh"),
        "12": Province("12", "Sumatera Utara"),
        "13": Province("13", "Sumatera Barat"),
        "14": Province("14", "Riau"),
        "15": Province("15", "Jambi"),
        "16": Province("16", "Sumatera Selatan"),
        "17": Province("17", "Bengkulu"),
        "18": Province("18", "Lampung"),
        "19": Province("19", "Kepulauan Bangka Belitung"),
        "21": Province("21", "Kepulauan Riau"),
        "31": Province("31", "DKI Jakarta"),
        "32": Province("32", "Jawa Barat"),
        "33": Province("33", "Jawa Tengah"),
        "34": Province("34", "DI Yogyakarta"),
        "35": Province("35", "Jawa Timur"),
        "36": Province("36", "Banten"),
        "51": Province("51", "Bali"),
        "52": Province("52", "Nusa Tenggara Barat"),
        "53": Province("53", "Nusa Tenggara Timur"),
        "61": Province("61", "Kalimantan Barat"),
        "62": Province("62", "Kalimantan Tengah"),
        "63": Province("63", "Kalimantan Selatan"),
        "64": Province("64", "Kalimantan Timur"),
        "65": Province("65", "Kalimantan Utara"),
        "71": Province("71", "Sulawesi Utara"),
        "72": Province("72", "Sulawesi Tengah"),
        "73": Province("73", "Sulawesi Selatan"),
        "74": Province("74", "Sulawesi Tenggara"),
        "75": Province("75", "Gorontalo"),
        "76": Province("76", "Sulawesi Barat"),
        "81": Province("81", "Maluku"),
        "82": Province("82", "Maluku Utara"),
        "91": Province("91", "Papua"),
        "92": Province("92", "Papua Barat"),
        "93": Province("93", "Papua Selatan"),
        "94": Province("94", "Papua Tengah"),
        "95": Province("95", "Papua Pegunungan"),
        "96": Province("96", "Papua Barat Daya"),
    }

    # Embedded regency data (sample - would be complete in production)
    _REGENCIES = {
        # Jawa Barat (32)
        "3201": Regency("3201", "KABUPATEN BOGOR", "32", "Kabupaten"),
        "3202": Regency("3202", "KABUPATEN SUKABUMI", "32", "Kabupaten"),
        "3203": Regency("3203", "KABUPATEN CIANJUR", "32", "Kabupaten"),
        "3204": Regency("3204", "KABUPATEN BANDUNG", "32", "Kabupaten"),
        "3205": Regency("3205", "KABUPATEN GARUT", "32", "Kabupaten"),
        "3206": Regency("3206", "KABUPATEN TASIKMALAYA", "32", "Kabupaten"),
        "3207": Regency("3207", "KABUPATEN CIAMIS", "32", "Kabupaten"),
        "3208": Regency("3208", "KABUPATEN KUNINGAN", "32", "Kabupaten"),
        "3209": Regency("3209", "KABUPATEN CIREBON", "32", "Kabupaten"),
        "3210": Regency("3210", "KABUPATEN MAJALENGKA", "32", "Kabupaten"),
        "3211": Regency("3211", "KABUPATEN SUMEDANG", "32", "Kabupaten"),
        "3212": Regency("3212", "KABUPATEN INDRAMAYU", "32", "Kabupaten"),
        "3213": Regency("3213", "KABUPATEN SUBANG", "32", "Kabupaten"),
        "3214": Regency("3214", "KABUPATEN PURWAKARTA", "32", "Kabupaten"),
        "3215": Regency("3215", "KABUPATEN KARAWANG", "32", "Kabupaten"),
        "3216": Regency("3216", "KABUPATEN BEKASI", "32", "Kabupaten"),
        "3271": Regency("3271", "KOTA BOGOR", "32", "Kota"),
        "3272": Regency("3272", "KOTA SUKABUMI", "32", "Kota"),
        "3273": Regency("3273", "KOTA BANDUNG", "32", "Kota"),
        "3274": Regency("3274", "KOTA CIREBON", "32", "Kota"),
        "3275": Regency("3275", "KOTA BEKASI", "32", "Kota"),
        "3276": Regency("3276", "KOTA DEPOK", "32", "Kota"),
        "3277": Regency("3277", "KOTA CIMAHI", "32", "Kota"),
        "3278": Regency("3278", "KOTA TASIKMALAYA", "32", "Kota"),
        "3279": Regency("3279", "KOTA BANJAR", "32", "Kota"),
        # DKI Jakarta (31)
        "3171": Regency("3171", "KOTA JAKARTA PUSAT", "31", "Kota"),
        "3172": Regency("3172", "KOTA JAKARTA UTARA", "31", "Kota"),
        "3173": Regency("3173", "KOTA JAKARTA BARAT", "31", "Kota"),
        "3174": Regency("3174", "KOTA JAKARTA SELATAN", "31", "Kota"),
        "3175": Regency("3175", "KOTA JAKARTA TIMUR", "31", "Kota"),
    }

    # Embedded district data (sample)
    _DISTRICTS = {
        # Kabupaten Bogor
        "320101": District("320101", "CIBINONG", "3201"),
        "320102": District("320102", "CITEUREUP", "3201"),
        "320103": District("320103", "SUKARAJA", "3201"),
        "320104": District("320104", "BABAKAN MADANG", "3201"),
        "320105": District("320105", "CIJERUK", "3201"),
        "320106": District("320106", "LEUWILIANG", "3201"),
        "320107": District("320107", "CIAMPEA", "3201"),
        "320108": District("320108", "CIBUNG BULANG", "3201"),
        "320109": District("320109", "PAMIJAHAN", "3201"),
        "320110": District("320110", "RUMPIN", "3201"),
        # Kota Bogor
        "327101": District("327101", "BOGOR SELATAN - KOTA", "3271"),
        "327102": District("327102", "BOGOR TIMUR - KOTA", "3271"),
        "327103": District("327103", "BOGOR UTARA - KOTA", "3271"),
        "327104": District("327104", "BOGOR BARAT - KOTA", "3271"),
        "327105": District("327105", "BOGOR TENGAH - KOTA", "3271"),
        # DKI Jakarta
        "317101": District("317101", "GAMBIR", "3171"),
        "317102": District("317102", "SAWAH BESAR", "3171"),
        "317103": District("317103", "KEMAYORAN", "3171"),
        "317104": District("317104", "SENEN", "3171"),
        "317105": District("317105", "CEMPAKA PUTIH", "3171"),
        "317106": District("317106", "MENTENG", "3171"),
        "317107": District("317107", "JOHAR BARU", "3171"),
        "317401": District("317401", "TEBET", "3174"),
        "317402": District("317402", "SETIABUDI", "3174"),
        "317403": District("317403", "MAMPANG PRAPATAN", "3174"),
        "317404": District("317404", "PASAR MINGGU", "3174"),
        "317405": District("317405", "KEBAYORAN LAMA", "3174"),
        "317406": District("317406", "KEBAYORAN BARU", "3174"),
        "317407": District("317407", "PESANGGRAHAN", "3174"),
        "317408": District("317408", "CILANDAK", "3174"),
        "317409": District("317409", "JAGAKARSA", "3174"),
        "317410": District("317410", "LUBANG BUAYA", "3174"),
    }

    def find_province(self, code: str):
        return self._PROVINCES.get(code)

    def find_regency(self, code: str):
        return self._REGENCIES.get(code)

    def find_district(self, code: str):
        return self._DISTRICTS.get(code)
