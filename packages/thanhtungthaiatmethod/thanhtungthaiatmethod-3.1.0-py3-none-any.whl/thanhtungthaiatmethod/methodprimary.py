import methods as m
import math
ttcung = ["CÀN", "HỢI", "TÝ", "SỬU", "CẤN", "DẦN", "MÃO", "THÌN",
          "TỐN", "TỊ", "NGỌ", "MÙI", "KHÔN", "THÂN", "DẬU", "TUẤT", "TRUNG"]


def AnNguPhuc(tichso):
    so = m.AnChungCacSao(tichso, 115, 225, 45)
    ten = ["CÀN", "CẤN", "TỐN", "KHÔN", "TRUNG"]
    tencung = ten[(math.floor(so - 1))]
    return ttcung.index(tencung) + 1


def AnDaiDu(tichso):
    so = m.AnChungCacSao(tichso, 34, 288, 36)
    ten = ["KHÔN", "TÝ", "TỐN", "CÀN", "NGỌ", "CẤN", "MÃO", "DẬU"]
    tencung = ten[(math.floor(so - 1))]
    return ttcung.index(tencung) + 1


def AnQuanCo(tichso):
    so = m.AnChungCacSao(tichso, 250, 360, 30)
    ten = ["NGỌ", "MÙI", "THÂN", "DẬU", "TUẤT", "HỢI",
           "TÝ", "SỬU", "DẦN", "MÃO", "THÌN", "TỊ"]
    tencung = ten[(math.floor(so - 1))]
    return ttcung.index(tencung) + 1


def AnThanCo(tichso):
    so = m.AnChungCacSao(tichso, 250, 36, 3)
    ten = ["NGỌ", "MÙI", "THÂN", "DẬU", "TUẤT", "HỢI",
           "TÝ", "SỬU", "DẦN", "MÃO", "THÌN", "TỊ"]
    tencung = ten[(math.floor(so - 1))]
    return ttcung.index(tencung) + 1


def AnDanCo(tichso):
    so = m.AnChungCacSao(tichso, 250, 12, 1)
    ten = ["TUẤT", "HỢI", "TÝ", "SỬU", "DẦN", "MÃO",
           "THÌN", "TỊ", "NGỌ", "MÙI", "THÂN", "DẬU"]
    tencung = ten[(math.floor(so - 1))]
    return ttcung.index(tencung) + 1


def AnTuThan(tichso):
    so = m.AnChungCacSao(tichso, 0, 36, 3)
    ten = ["CÀN", "NGỌ", "CẤN", "MÃO", "TRUNG", "DẬU",
           "KHÔN", "TÝ", "TỐN", "TỊ", "THÂN", "DẦN"]
    tencung = ten[(math.floor(so - 1))]
    return ttcung.index(tencung) + 1


def AnThienAt(tichso):
    so = m.AnChungCacSao(tichso, 0, 36, 3)
    ten = ["DẬU", "KHÔN", "TÝ", "TỐN", "TỊ", "THÂN",
           "DẦN", "CÀN", "NGỌ", "CẤN", "MÃO", "TRUNG"]
    tencung = ten[(math.floor(so - 1))]
    return ttcung.index(tencung) + 1


def AnDiaAt(tichso):
    so = m.AnChungCacSao(tichso, 0, 36, 3)
    ten = ["TỐN", "TỊ", "THÂN", "DẦN", "CÀN", "NGỌ",
           "CẤN", "MÃO", "TRUNG", "DẬU", "KHÔN", "TÝ"]
    tencung = ten[(math.floor(so - 1))]
    return ttcung.index(tencung) + 1


def AnTrucPhu(tichso):
    so = m.AnChungCacSao(tichso, 0, 36, 3)
    ten = ["TRUNG", "DẬU", "KHÔN", "TÝ", "TỐN", "TỊ",
           "THÂN", "DẦN", "CÀN", "NGỌ", "CẤN", "MÃO"]
    tencung = ten[(math.floor(so - 1))]
    return ttcung.index(tencung) + 1


def AnThanhKy(tichso, chithaiat):
    so = m.AnChungCacSao(tichso, 0, 12, 1)
    ten = ["HỢI", "TÝ", "SỬU", "DẦN", "MÃO", "THÌN",
           "TỊ", "NGỌ", "MÙI", "THÂN", "DẬU", "TUẤT"]
    tencung = ten[(math.floor(so - 1))]
    ketqua = ttcung.index(tencung) + 1
    if ((chithaiat == "TỊ") or (chithaiat == "HỢI")):
        ketqua = 15
    return ketqua


def AnXichKy(tichso, chithaiat):
    so = m.AnChungCacSao(tichso, 1, 4, 1)
    ten = ["HỢI", "THÂN", "TỊ", "DẦN"]
    tencung = ten[(math.floor(so - 1))]
    ketqua = ttcung.index(tencung) + 1
    if ((chithaiat == "TỊ") or (chithaiat == "HỢI")):
        ketqua = 13
    return ketqua


def AnHacKy(tichso, chithaiat):
    so = m.AnChungCacSao(tichso, 25, 36, 3)
    ten = ["HỢI", "TUẤT", "DẬU", "THÂN", "MÙI", "NGỌ",
           "TỊ", "THÌN", "MÃO", "DẦN", "SỬU", "TÝ"]
    tencung = ten[(math.floor(so - 1))]
    ketqua = ttcung.index(tencung) + 1
    if ((chithaiat == "TỊ") or (chithaiat == "HỢI")):
        ketqua = 11
    return ketqua


def AnThienTon(tichso, amduongcuc):
    so = m.AnChungCacSao(tichso, 0, 4, 1)
    tenduong = ["TÝ", "DẬU", "NGỌ", "MÃO"]
    tenam = ["MÃO", "NGỌ", "DẬU", "TÝ"]
    tencung = ""
    if (amduongcuc == 1):
        tencung = tenduong[(math.floor(so - 1))]
    else:
        tencung = tenam[(math.floor(so - 1))]
    return ttcung.index(tencung) + 1


def AnThienHoang(tichso, amduongcuc):
    so = m.AnChungCacSao(tichso, 0, 20, 1)
    tenduong = ["THÂN", "DẬU", "TUẤT", "CÀN", "CÀN", "HỢI", "TÝ", "SỬU", "CẤN",
                "CẤN", "DẦN", "MÃO", "THÌN", "TỐN", "TỐN", "TỊ", "NGỌ", "MÙI", "KHÔN", "KHÔN"]
    tenam = ["DẦN", "CẤN", "CẤN", "SỬU", "TÝ", "HỢI", "CÀN", "CÀN", "TUẤT", "DẬU",
             "THÂN", "KHÔN", "KHÔN", "MÙI", "NGỌ", "TỊ", "TỐN", "TỐN", "THÌN", "MÃO"]
    tencung = ""
    if (amduongcuc == 1):
        tencung = tenduong[(math.floor(so - 1))]
    else:
        tencung = tenam[(math.floor(so - 1))]
    return ttcung.index(tencung) + 1


def AnThienThoi(tichso, amduongcuc):
    so = m.AnChungCacSao(tichso, 0, 12, 1)
    tenduong = ["DẦN", "MÃO", "THÌN", "TỊ", "NGỌ",
                "MÙI", "THÂN", "DẬU", "TUẤT", "HỢI", "TÝ", "SỬU"]
    tenam = ["THÂN", "MÙI", "NGỌ", "TỊ", "THÌN", "MÃO",
             "DẦN", "SỬU", "TÝ", "HỢI", "TUẤT", "DẬU"]
    tencung = ""
    if (amduongcuc == 1):
        tencung = tenduong[(math.floor(so - 1))]
    else:
        tencung = tenam[(math.floor(so - 1))]
    return ttcung.index(tencung) + 1
