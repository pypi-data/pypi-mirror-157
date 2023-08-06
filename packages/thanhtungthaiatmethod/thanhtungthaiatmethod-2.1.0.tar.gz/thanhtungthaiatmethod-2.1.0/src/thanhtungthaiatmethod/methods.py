import math


from numpy import double
DanhSach60CanChi = ["GIÁP TÝ",
                    "ẤT SỬU",
                    "BÍNH DẦN",
                    "ĐINH MÃO",
                    "MẬU THÌN",
                    "KỶ TỊ",
                    "CANH NGỌ",
                    "TÂN MÙI",
                    "NHÂM THÂN",
                    "QUÝ DẬU",
                    "GIÁP TUẤT",
                    "ẤT HỢI",
                    "BÍNH TÝ",
                    "ĐINH SỬU",
                    "MẬU DẦN",
                    "KỶ MÃO",
                    "CANH THÌN",
                    "TÂN TỊ",
                    "NHÂM NGỌ",
                    "QUÝ MÙI",
                    "GIÁP THÂN",
                    "ẤT DẬU",
                    "BÍNH TUẤT",
                    "ĐINH HỢI",
                    "MẬU TÝ",
                    "KỶ SỬU",
                    "CANH DẦN",
                    "TÂN MÃO",
                    "NHÂM THÌN",
                    "QUÝ TỊ",
                    "GIÁP NGỌ",
                    "ẤT MÙI",
                    "BÍNH THÂN",
                    "ĐINH DẬU",
                    "MẬU TUẤT",
                    "KỶ HỢI",
                    "CANH TÝ",
                    "TÂN SỬU",
                    "NHÂM DẦN",
                    "QUÝ MÃO",
                    "GIÁP THÌN",
                    "ẤT TỊ",
                    "BÍNH NGỌ",
                    "ĐINH MÙI",
                    "MẬU THÂN",
                    "KỶ DẬU",
                    "CANH TUẤT",
                    "TÂN HỢI",
                    "NHÂM TÝ",
                    "QUÝ SỬU",
                    "GIÁP DẦN",
                    "ẤT MÃO",
                    "BÍNH THÌN",
                    "ĐINH TỊ",
                    "MẬU NGỌ",
                    "KỶ MÙI",
                    "CANH THÂN",
                    "TÂN DẬU",
                    "NHÂM TUẤT",
                    "QUÝ HỢI"]

canGoc = ["GIÁP", "ẤT", "BÍNH", "ĐINH",
          "MẬU", "KỶ", "CANH", "TÂN", "NHÂM", "QUÝ"]
chiGoc = ["TÝ", "SỬU", "DẦN", "MÃO", "THÌN", "TỊ",
          "NGỌ", "MÙI", "THÂN", "DẬU", "TUẤT", "HỢI"]
ttcung = ["CÀN", "HỢI", "TÝ", "SỬU", "CẤN", "DẦN", "MÃO", "THÌN",
          "TỐN", "TỊ", "NGỌ", "MÙI", "KHÔN", "THÂN", "DẬU", "TUẤT", "TRUNG"]
bangsotoan = [[1, 25, 9,  12, 34, 27, 1,  16],
              [40, 25, 9, 12, 34, 27, 1, 16],
              [39, 24, 8, 11, 33, 26, 8,  15],
              [32, 17, 1, 4,  26, 19, 33, 8],
              [31, 16, 3, 3,  25, 18, 32, 7],
              [29, 14, 38, 1,  23, 16, 30, 5],
              [28, 13, 37, 4,  22, 15, 29, 4],
              [25, 10, 34, 37, 19, 12, 26, 1],
              [24, 9,  33, 36, 18, 11, 25, 9],
              [16, 1,  25, 28, 10, 3,  17, 32],
              [15, 2,  24, 27, 9,  2,  16, 31],
              [14, 39, 23, 26, 8,  1,  15, 30],
              [13, 38, 22, 25, 7,  7,  14, 29],
              [7, 32, 16, 19, 1,  34, 8,  23],
              [6, 31, 15, 18, 6,  33, 7,  22],
              [1, 26, 10, 13, 35, 28, 2,  17]]
col = ["CÀN", "NGỌ", "CẤN", "MÃO", "DẬU", "KHÔN", "TÝ", "TỐN"]
bang4tuong = ["CÀN", "NGỌ", "CẤN", "MÃO", "TRUNG", "DẬU", "KHÔN", "TÝ", "TỐN"]
cantuangoc = ["MẬU", "KỶ", "CANH", "TÂN", "NHÂM", "QUÝ", "ĐINH", "BÍNH", "ẤT"]
cungtuongungcan = [1, 2, 3, 4, 5, 6, 7, 8, 9]
quaidon = ["KHÔN", "KHẢM", "TỐN", "CÀN", "LY", "CẤN", "CHẤN", "ĐOÀI"]


def CanChiNamThaiAt(tichNam):
    tcan = (tichNam-1) % 10
    tchi = (tichNam-1) % 12
    return [canGoc[tcan], chiGoc[tchi]]


def CuuTinhLacThuQuyThan(tichSo):
    # Qúy thần mỗi năm 1 sao rút vào cung giữa làm chủ sự (Trực sự)
    # Sao ngay sau nó bay ra Càn
    # Thứ tự an các sao còn lại là Càn Đoài Cấn Ly Khảm Khôn Chấn Tốn => Trung
    # Theo số Lạc thư là 5, 6, 7, 8, 9, 1, 2, 3, 4
    # Theo số Thái ất là 5, 1, 6, 3, 2, 8, 7, 4, 9

    # Đầu tiên tìm quý thần trực sự:
    tichSo += 3
    a = ["Thái nhất", "Thiên hoàng", "Thái âm", "Hàm trì",
         "Thanh long", "Thiên phù", "Chiêu dao", "Hiên viên", "Nhiếp đề"]
    s = tichSo % 9
    trucSu = a[s]

    # Sort các sao còn lại trong vòng vào list:
    x = ["Thái nhất", "Nhiếp đề", "Hiên viên", "Chiêu dao",
         "Thiên phù", "Thanh long", "Hàm trì", "Thái âm", "Thiên hoàng"]
    lst = [trucSu]
    for i in range(1, len(x)):
        lst.append(x[(x.index(trucSu)+i) % 9])

    # Danh sách các cung theo số thống nhất của bàn Thái ất, phù hợp cho ứng dụng,
    # giảm đi 1 phù hợp với index
    rutCung = [4, 0, 5, 2, 1, 7, 6, 3, 8]

    # Tạo lst ketQua để Sort tên các sao theo thứ tự cung từ 0 đến 8:
    ketQua = []
    for i in range(9):
        ketQua.append(lst[rutCung.index(i)])
    # Thêm kết quả sao trực sự vào cuối cùng
    ketQua.append([trucSu])
    # Như vậy, kết quả là sao index[0] an tại Càn, index[1] an tại Ly (2) ..., kết thúc là sao Trực sự quý thần ở index[9]
    return ketQua


def BatMonTrucSu(tichSo, donAmDuong, tuKe):
    # Bát môn thuộc về phép dùng, nên chỉ tính ra Cửa Trực
    # Từ đó, tùy đối tượng mà xem, Văn Kích động thì lấy Ất chủ khí,
    # Tướng động thì lấy Văn Kích chủ khí, động đều xét đạo tiểu nhân - âm
    # Cửa gia chủ khí, tướng cần không gặp cửa lành mới thắng, cần hung sát, chủ thắng bại giết chóc
    # Ất chủ khí, duy vương đạo xét đạo quân tử - dương, lấy Tuế Cả làm tướng, cần lành, chủ yên bình
    n = 0
    stt = 0
    ten = ["KHAI", "HƯU", "SINH", "THƯƠNG", "ĐỖ", "CẢNH", "TỬ", "KINH"]
    trucSu = ""
    soNam = 0
    if "giờ" in tuKe:
        n = tichSo % 120
        if donAmDuong == "Dương độn":
            stt = math.floor(n/30)
            trucSu = ten[stt]

        else:
            stt = math.floor(n/30) + 4
            trucSu = ten[stt]
    else:
        n = tichSo % 240
        stt = math.floor(n/30)
        trucSu = ten[stt]
    soNam = n % 30
    return [trucSu, str(soNam)]


def TuanGiapVaCanTuan(can, chi):
    ketQua = ['', '']
    stt = DanhSach60CanChi.index(can + " " + chi)
    if(stt < 10):
        ketQua = ['TÝ', 'MẬU']
    elif ((stt >= 10) and (stt < 20)):
        ketQua = ['TUẤT', 'KỶ']
    elif ((stt >= 20) and (stt < 30)):
        ketQua = ['THÂN', 'CANH']
    elif ((stt >= 30) and (stt < 40)):
        ketQua = ['NGỌ', 'TÂN']
    elif ((stt >= 40) and (stt < 50)):
        ketQua = ['THÌN', 'NHÂM']
    elif ((stt >= 50) and (stt < 60)):
        ketQua = ['DẦN', 'QUÝ']
    return ketQua


def CuuTinhVanXuongTrucSu(tichSo, can, chi):
    x = ["Văn xương", "Huyền phượng", "Minh duy", "Âm đức",
         "Chiêu dao", "Thừa minh", "Huyền vũ", "Huyền minh", "Hùng minh"]
    cungCan = [0, 8, 7, 6, 0, 1, 2, 3, 4, 5]
    tp1 = ["", "", "", "", "", "", "", "", ""]
    tp2 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ketQua = ["", "", "", "", "", "", "", "", ""]
    # Theo Huyền phạm tiết yếu, với Trực sự, lấy Giáp Mậu chung nhau cung 1 Càn
    # Cách khác có thể lấy Can của tuần và thay vào giống như Cửu Tinh Thái ất trực phù
    # Thuật toán ở đây theo Huyền phạm tiết yếu, số 0 là can giáp, các số cung trừ đi 1 để phù hợp index của array
    # Tuy nhiên, trong kết quả có lồng thêm một tham số tuần giáp của Can Chi hiện tại,
    # để có thể tùy chọn và tự xem xét lại nếu như gặp năm có can Giáp

    s = tichSo % 270
    t = math.floor(s/30)
    trucSu = x[t]
    namQua = s % 30
    tuanGiap = TuanGiapVaCanTuan(can, chi)
    tp1[0] = trucSu
    for i in range(1, 9):
        tp1[i] = x[(x.index(tp1[0])+i) % 9]

    tp2[0] = cungCan[canGoc.index(can)]
    for i in range(1, 9):
        tp2[i] = (tp2[0]+i) % 9
    # Trả kết quả về, Sort sao an cung 1, 2,...(index = 0,1,2,...)
    for i in range(9):
        ketQua[i] = tp1[tp2.index(i)]
    ketQua.append([trucSu, str(namQua)])
    ketQua.append(tuanGiap)

    return ketQua


def CuuTinhThaiAtTrucPhu(tichSo, can, chi, donAmDuong):
    d = ["Thiên bồng", "Thiên nhuế", "Thiên xung", "Thiên phụ",
         "Thiên cầm", "Thiên tâm", "Thiên trụ", "Thiên nhậm", "Thiên ương"]
    a = ["Thiên ương", "Thiên nhậm", "Thiên trụ", "Thiên tâm",
         "Thiên cầm", "Thiên phụ", "Thiên xung", "Thiên nhuế", "Thiên bồng"]
    # Gốc cung từ 1 đến 9, đưa về array thì thành từ 0 đến 8 (tested)
    cungCan = [0, 8, 7, 6, 0, 1, 2, 3, 4, 5]
    temp1 = ["", "", "", "", "", "", "", "", ""]
    temp2 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ketQua = ["", "", "", "", "", "", "", "", ""]
    trucPhu = ""

    # Sao Thái ất trực phù:
    # Tích số, mỗi sao 10 năm, khởi từ Thiên bồng đi thuận 9 cung, đến cung nào thì sao ấy Trực phù.
    # Số cung theo Thái ất, cung Càn 1 Mậu, Ly 2 Kỷ,..., gặp năm Mậu, an Trực phù vào cung Càn, tiếp đó an xuôi
    # Tuần giáp: mỗi sao trực 10 số, thành ra trực 1 tuần giáp, biết vậy nhưng không cần tính vào.
    # Âm độn đi ngược (chỉ kể giờ), dương khởi Thiên bồng, âm khởi Thiên ương mà tính, cung Can + chiều xoay của sao (Bồng Nhuế Xung...) vẫn thế
    # Trực phù tức là sao nào trực
    # Trực sự là vị trí sao trực phù đóng (ở đây chính là cung Can ngày)
    # Riêng với an can giáp: vì giáp ẩn, gặp ngày Giáp, xem tuần đó là tuần nào,
    # ví dụ, tuần giáp Ngọ can đại diện là Tân, đem an sao trực phù của ngày giáp đó vào cung Tân 4

    s = tichSo % 90
    t = math.floor(s/10)
    # Đem can giáp ẩn vào can tuần, nạp vào index = 0
    cungCan[0] = cungCan[canGoc.index(TuanGiapVaCanTuan(can, chi)[1])]

    if donAmDuong == 1:
        trucPhu = d[t]
    else:
        trucPhu = a[t]
    namQua = s % 10
    # Sort 9 sao trực phù vào list, [0] là sao trực phù
    temp1[0] = trucPhu
    for i in range(1, 9):
        if (donAmDuong == 1):
            temp1[i] = d[(d.index(temp1[0])+i) % 9]
        else:
            temp1[i] = a[(a.index(temp1[0])+i) % 9]
    # Sort số thứ tự cung an sao trực phù vào list, [0] là cung an trực phù
    temp2[0] = cungCan[canGoc.index(can)]
    for i in range(1, 9):
        temp2[i] = (temp2[i-1]+1) % 9
    # Trả kết quả về, Sort sao an cung 1, 2,...(index = 0,1,2,...)
    for i in range(9):
        ketQua[i] = temp1[temp2.index(i)]
    ketQua.append([trucPhu, str(namQua)])

    return ketQua


def Gom(ansao, sttcung):
    a = []
    t = 0
    for i in range(len(ansao)):
        if ansao[i] == sttcung:
            a.append(i)
        else:
            a.append(99)
    for i in range(len(ansao)+2):
        for j in range(len(ansao)-1):
            if a[j] > a[j+1]:
                t = a[j+1]
                a[j+1] = a[j]
                a[j] = t
    return a


def SortSaoChinh(mang):
    tinhdau = ["Thái ất", "Văn xương", "Thủy kích", "Đại chủ",
               "Đại khách", "Tham chủ", "Tham khách", "Kể thần", "Kể định"]
    a = []
    for i in range(5):
        if mang[i] <= 9:
            a.append(tinhdau[mang[i]])
        else:
            a.append("")
    return a


def SaoChinh(kydu, amduongcuc):
    tinhdau = ["Thái ất", "Văn xương", "Thủy kích", "Đại chủ",
               "Đại khách", "Tham chủ", "Tham khách", "Kể thần", "Kể định"]
    ansao = []
    ansao.append(ThaiAt(kydu, amduongcuc))
    ansao.append(VanXuong(kydu, amduongcuc))
    ansao.append(ThuyKich(kydu, amduongcuc))
    ansao.append(DaiChu(kydu, amduongcuc))
    ansao.append(DaiKhach(kydu, amduongcuc))
    ansao.append(ThamChu(kydu, amduongcuc))
    ansao.append(ThamKhach(kydu, amduongcuc))
    ansao.append(KeThan(kydu, amduongcuc))
    ansao.append(KeDinh(kydu, amduongcuc))
    ketQua = []
    for i in range(17):
        ketQua.append(SortSaoChinh(Gom(ansao, i+1)))

    return ketQua
    # Cung 1 Can, 2 Hoi, 3 Ty ..., 16 Tuat, 17 Trung


def ThaiAt(kydu, amduongcuc):
    duong = ["CÀN", "NGỌ", "CẤN", "MÃO", "DẬU", "KHÔN", "TÝ", "TỐN"]
    am = ["TỐN", "TÝ", "KHÔN", "DẬU", "MÃO", "CẤN", "NGỌ", "CÀN"]
    a = math.floor(((kydu - 1) % 24) / 3)
    cung = ""
    if (amduongcuc == 1):
        cung = duong[a]
    else:
        cung = am[a]
    return ttcung.index(cung) + 1


def VanXuong(kydu, amduongcuc):
    duong = ["THÂN", "DẬU", "TUẤT", "CÀN", "CÀN", "HỢI", "TÝ", "SỬU",
             "CẤN", "DẦN", "MÃO", "THÌN", "TỐN", "TỊ", "NGỌ", "MÙI", "KHÔN", "KHÔN"]
    am = ["DẦN", "MÃO", "THÌN", "TỐN", "TỐN", "TỊ", "NGỌ", "MÙI",
          "KHÔN", "THÂN", "DẬU", "TUẤT", "CÀN", "HỢI", "TÝ", "SỬU", "CẤN", "CẤN"]
    a = (kydu - 1) % 18
    ten = ""
    if (amduongcuc == 1):
        ten = duong[a]
    else:
        ten = am[a]
    return ttcung.index(ten) + 1


def KeThan(kydu, amduongcuc):
    duongcuc = ["DẦN", "SỬU", "TÝ", "HỢI", "TUẤT",
                "DẬU", "THÂN", "MÙI", "NGỌ", "TỊ", "THÌN", "MÃO"]
    amcuc = ["THÂN", "MÙI", "NGỌ", "TỊ", "THÌN", "MÃO",
             "DẦN", "SỬU", "TÝ", "HỢI", "TUẤT", "DẬU"]
    a = (kydu - 1) % 12
    tencung = ""
    if (amduongcuc == 1):
        tencung = duongcuc[a]
    else:
        tencung = amcuc[a]
    return ttcung.index(tencung) + 1


def ThuyKich(kydu, amduongcuc):
    tk = ["CẤN", "DẦN", "MÃO", "THÌN", "TỐN", "TỊ", "NGỌ",
          "MÙI", "KHÔN", "THÂN", "DẬU", "TUẤT", "CÀN", "HỢI", "TÝ", "SỬU"]
    vanxuong = ttcung[VanXuong(kydu, amduongcuc) - 1]
    kethan = ttcung[KeThan(kydu, amduongcuc) - 1]
    cungvx = tk.index(vanxuong)
    cungkt = tk.index(kethan)
    so = (16 - cungkt + cungvx) % 16
    tencung = tk[so]
    return ttcung.index(tencung) + 1


def ToanChu(kydu, amduongcuc):
    cungTA = ttcung[ThaiAt(kydu, amduongcuc) - 1]
    cungVX = ttcung[VanXuong(kydu, amduongcuc) - 1]
    a = col.index(cungTA)
    b = ttcung.index(cungVX)
    return bangsotoan[b][a]


def ToanKhach(kydu, amduongcuc):
    tencungthaiat = ttcung[ThaiAt(kydu, amduongcuc) - 1]
    tencungthuykich = ttcung[ThuyKich(kydu, amduongcuc) - 1]
    a = col.index(tencungthaiat)
    b = ttcung.index(tencungthuykich)
    return bangsotoan[b], [a]


def ToanDinh(kydu, amduongcuc, chithaiat):
    tencungthaiat = ttcung[ThaiAt(kydu, amduongcuc) - 1]
    tencungkedinh = ttcung[KeDinh(kydu, amduongcuc, chithaiat) - 1]
    a = col.index(tencungthaiat)
    b = ttcung.index(tencungkedinh)
    return bangsotoan[b][a]


def KeDinh(kydu, amduongcuc, chithaiat):
    bangkedinh = ["CẤN", "DẦN", "MÃO", "THÌN", "TỐN", "TỊ", "NGỌ",
                  "MÙI", "KHÔN", "THÂN", "DẬU", "TUẤT", "CÀN", "HỢI", "TÝ", "SỬU"]
    hopthan = ["SỬU", "TÝ", "HỢI", "TUẤT", "DẬU",
               "THÂN", "MÙI", "NGỌ", "TỊ", "THÌN", "MÃO", "DẦN"]
    sochitue = bangkedinh.index(chithaiat) + 1
    a = chiGoc.index(chithaiat)
    thanhop = hopthan[a]
    sohopthan = bangkedinh.index(thanhop) + 1
    tencungvanxuong = ttcung[VanXuong(kydu, amduongcuc) - 1]
    sovanxuong = bangkedinh.index(tencungvanxuong) + 1
    nambo = 16 - sohopthan + sovanxuong
    sokedinh = 0
    if (sochitue + nambo > 16):
        sokedinh = (sochitue + nambo - 1) % 16 + 1
    else:
        sokedinh = sochitue + nambo
    tencungkedinh = bangkedinh[sokedinh - 1]

    return ttcung.index(tencungkedinh) + 1


def DaiChu(kydu, amduongcuc):

    toanchu = ToanChu(kydu, amduongcuc)
    sodaichu = 0
    if (toanchu % 10 != 0):
        sodaichu = toanchu % 10
    else:
        sodaichu = toanchu / 10
    cungan = bang4tuong[sodaichu - 1]
    return ttcung.index(cungan) + 1


def ThamChu(kydu, amduongcuc):

    toanchu = ToanChu(kydu, amduongcuc)
    sodaichu = 0
    if (toanchu % 10) != 0:
        sodaichu = toanchu % 10
    else:
        sodaichu = toanchu / 10
    sothamchu = (sodaichu * 3) % 10
    cungan = bang4tuong[sothamchu - 1]
    return ttcung.index(cungan) + 1


def DaiKhach(kydu, amduongcuc):
    toanchu = ToanKhach(kydu, amduongcuc)
    sodaichu = 0
    if (toanchu % 10) != 0:
        sodaichu = toanchu % 10
    else:
        sodaichu = toanchu / 10
    cungan = bang4tuong[sodaichu - 1]
    return ttcung.index(cungan) + 1


def ThamKhach(kydu, amduongcuc):
    toanchu = ToanKhach(kydu, amduongcuc)
    sodaichu = 0
    if (toanchu % 10) != 0:
        sodaichu = toanchu % 10
    else:
        sodaichu = toanchu / 10
    sothamchu = (sodaichu * 3) % 10
    cungan = bang4tuong[sothamchu - 1]
    return ttcung.index(cungan) + 1


def LyTamTai(kydu):
    nu = kydu % 3
    ketqua = ""
    if (nu == 1):
        ketqua = "THIÊN"
    elif (nu == 2):
        ketqua = "ĐỊA"
    else:
        ketqua = "NHÂN"
    return ketqua


def SoNguyen(kydu):
    return math.floor((kydu - 1) / 72) + 1


def SoCuc(kydu):
    return math.floor((kydu - 1) % 72) + 1


def KyDu(sotich):
    kydu = 0
    if (sotich % 360 == 0):
        kydu = 360
    else:
        kydu = sotich % 360
    return kydu


def HanAmLuc(tichso):
    tichso += 2050
    thieulon = 4320 - (tichso - (math.floor(tichso / 4320)) * 4320)
    thieunho = 288 - (tichso - (math.floor(tichso / 288)) * 288)
    return [str(thieulon), str(thieunho)]


def HanDuongCuu_HanHoiAchAmDuong(tichso):
    tichso += 130
    songuyenlondaqua = math.floor(tichso / 4560)
    sonamdaqualon = tichso % 4560
    thieulon = 4560 - sonamdaqualon
    thieunho = 456 - (tichso - math.floor(tichso / 456) * 456)
    sonamhoiach = [106, 374, 480, 720, 720, 600, 600, 480, 480]
    tenhoiach = ["9 nắng hạn", "9 nước lớn", "9 nắng hạn", "7 nước lớn",
                 "7 nắng hạn", "5 nước lớn", "5 nắng hạn", "3 nước lớn", "3 nắng hạn"]
    sonamluytien = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    sonamluytien[0] = sonamhoiach[0]
    stt = 0
    for i in range(len(sonamluytien)):
        sonamluytien[i] = sonamluytien[i - 1] + sonamhoiach[i]

    amduong = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    for j in range(len(sonamluytien)):
        amduong[j] = sonamluytien[j] - sonamdaqualon
    if (amduong[0] > 0):
        stt = 1
    for k in range(len(amduong)):
        if ((amduong[k] <= 0) and (amduong[k + 1] > 0)):
            stt = k + 2
    hanhoiachthu = stt
    tenhanhoiachsaptoi = tenhoiach[stt - 1]
    thieusohoiach = amduong[stt - 1]
    return [str(thieulon), str(thieunho), str(hanhoiachthu), str(tenhanhoiachsaptoi), str(thieusohoiach), ]


def DaiDuThuongHaSoNamvaDongHao(tichso):

    sothuong = math.floor(math.floor((tichso + 34) % 80) / 10)
    soha = math.floor(math.floor((tichso + 34) % 288) / 36)
    namthuong = math.floor(math.floor((tichso + 34) % 80) % 10) + 1
    namha = math.floor(math.floor((tichso + 34) % 288) % 36) + 1
    haodong = math.floor((namha - 1) / 6) + 1
    thuongquai = quaidon[sothuong]
    haquai = quaidon[soha]
    return [thuongquai, haquai, str(namthuong), str(namha), str(haodong)]


def TieuDuThuongHaSoNamvaDongHao(tichso):

    sothuong = math.floor(math.floor((tichso - 1) % 24) / 3)
    soha = math.floor(math.floor((tichso - 1) % 192) / 24)
    namthuong = math.floor(math.floor(tichso % 24) % 3) + 1
    namha = math.floor(math.floor(tichso % 192) % 24) + 1
    haodong = math.floor((namha - 1) / 4) + 1
    thuongquai = quaidon[sothuong]
    haquai = quaidon[soha]
    return [thuongquai, haquai, str(namthuong), str(namha), str(haodong)]


def TenQueDichTheoThuTu(thutu):
    quedich = ["THUẦN CÀN", "THUẦN KHÔN", "THỦY LÔI TRUÂN", "SƠN THỦY MÔNG", "THỦY THIÊN NHU", "THIÊN THỦY TỤNG", "ĐỊA THỦY SƯ", "THỦY ĐỊA TỶ", "PHONG THIÊN TIỂU SÚC", "THIÊN TRẠCH LÝ", "ĐỊA THIÊN THÁI", "THIÊN ĐỊA BĨ", "THIÊN HỎA ĐỒNG NHÂN", "HỎA THIÊN ĐẠI HỮU", "ĐỊA SƠN KHIÊM", "LÔI ĐỊA DỰ", "TRẠCH LÔI TÙY", "SƠN PHONG CỔ", "ĐỊA TRẠCH LÂM", "PHONG ĐỊA QUAN", "HỎA LÔI PHỆ HẠP", "SƠN HỎA BÍ", "SƠN ĐỊA BÁC", "ĐỊA LÔI PHỤC", "THIÊN LÔI VÔ VỌNG", "SƠN THIÊN ĐẠI SÚC", "SƠN LÔI DI", "TRẠCH PHONG ĐẠI QUÁ", "THUẦN KHẢM", "THUẦN LY", "TRẠCH SƠN HÀM""LÔI PHONG HẰNG",
               "THIÊN SƠN ĐỘN", "LÔI THIÊN ĐẠI TRÁNG", "HỎA ĐỊA TẤN", "ĐỊA HỎA MINH DI", "PHONG HỎA GIA NHÂN", "HỎA TRẠCH KHUÊ", "THỦY SƠN KIỂN", "LÔI THỦY GIẢI", "SƠN TRẠCH TỔN", "PHONG LÔI ÍCH", "TRẠCH THIÊN QUẢI", "THIÊN PHONG CẤU", "TRẠCH ĐỊA TỤY", "ĐỊA PHONG THĂNG", "TRẠCH THỦY KHỐN", "THỦY PHONG TỈNH", "TRẠCH HỎA CÁCH", "HỎA PHONG ĐỈNH", "THUẦN CHẤN", "THUẦN CẤN", "PHONG SƠN TIỆM", "LÔI TRẠCH QUY MUỘI", "LÔI HỎA PHONG", "HỎA SƠN LỮ", "THUẦN TỐN", "THUẦN ĐOÀI", "PHONG THỦY HOÁN", "THỦY TRẠCH TIẾT", "PHONG TRẠCH TRUNG PHU", "LÔI SƠN TIỂU QUÁ", "THỦY HỎA KÝ TẾ", "HỎA THỦY VỊ TẾ"]
    return quedich[thutu]


def AnThaiTueThaiAmHopThan(chithaiat):
    ketqua = [0, 0, 0]
    ketqua[0] = ttcung.index(chithaiat) + 1
    thaiam = ["TUẤT", "HỢI", "TÝ", "SỬU", "DẦN", "MÃO",
              "THÌN", "TỊ", "NGỌ", "MÙI", "THÂN", "DẬU"]
    hopthan = ["SỬU", "TÝ", "HỢI", "TUẤT", "DẬU",
               "THÂN", "MÙI", "NGỌ", "TỊ", "THÌN", "MÃO", "DẦN"]
    a = chiGoc.index(chithaiat)
    ketqua[1] = ttcung.index(thaiam[a]) + 1
    ketqua[2] = ttcung.index(hopthan[a]) + 1
    return ketqua


# Ngũ phúc, Đại du, Tam cơ, Tứ thần, Thiên ất, Địa ất, Trực phù
def NguPhucDaiDuTamCoTuThanDaiTieumuc(tichso):
    ren = ['nguPhuc', 'daiDu', 'quanCo', 'thanCo',
           'danCo', 'tuThan', 'thienAt', 'diaAt', 'trucPhu', 'daiMuc', 'tieuMuc']
    ren_name = [["CÀN", "CẤN", "TỐN", "KHÔN", "TRUNG"],
                ["KHÔN", "TÝ", "TỐN", "CÀN", "NGỌ", "CẤN", "MÃO", "DẬU"],
                ["NGỌ", "MÙI", "THÂN", "DẬU", "TUẤT", "HỢI",
                 "TÝ", "SỬU", "DẦN", "MÃO", "THÌN", "TỊ"],
                ["NGỌ", "MÙI", "THÂN", "DẬU", "TUẤT", "HỢI",
                 "TÝ", "SỬU", "DẦN", "MÃO", "THÌN", "TỊ"],
                ["TUẤT", "HỢI", "TÝ", "SỬU", "DẦN", "MÃO",
                 "THÌN", "TỊ", "NGỌ", "MÙI", "THÂN", "DẬU"],
                ["CÀN", "NGỌ", "CẤN", "MÃO", "TRUNG", "DẬU",
                 "KHÔN", "TÝ", "TỐN", "TỊ", "THÂN", "DẦN"],
                ["DẬU", "KHÔN", "TÝ", "TỐN", "TỊ", "THÂN",
                    "DẦN", "CÀN", "NGỌ", "CẤN", "MÃO", "TRUNG"],
                ["TỐN", "TỊ", "THÂN", "DẦN", "CÀN", "NGỌ",
                    "CẤN", "MÃO", "TRUNG", "DẬU", "KHÔN", "TÝ"],
                ["TRUNG", "DẬU", "KHÔN", "TÝ", "TỐN", "TỊ",
                 "THÂN", "DẦN", "CÀN", "NGỌ", "CẤN", "MÃO"],
                ["MÙI", "KHÔN", "KHÔN", "THÂN", "DẬU", "TUẤT", "CÀN", "CÀN", "HỢI",
                    "TÝ", "SỬU", "CẤN", "DẦN", "MÃO", "THÌN", "TỐN", "TỊ", "NGỌ"],
                ["KHÔN", "KHÔN", "THÂN", "DẬU", "TUẤT", "CÀN", "CÀN", "HỢI", "TÝ", "SỬU", "CẤN", "DẦN", "MÃO", "THÌN", "TỐN", "TỊ", "NGỌ", "MÙI"]]
    ren_number = [[115, 225, 45], [34, 288, 36], [
        250, 360, 30], [250, 36, 3], [250, 12, 1], [0, 36, 3], [0, 36, 3], [0, 36, 3], [0, 36, 3], [216, 216, 12], [0, 18, 1]]
    ketQua = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    b = 0
    c = 0
    for i in range(len(ren)):
        b = ren_name[i]
        c = ren_number[i]
        so = AnChungCacSao(tichso, c[0], c[1], c[2])
        tencung = b[(math.floor(so - 1))]
        ketQua[i] = ttcung.index(tencung)+1
    return ketQua


def TamKy(tichso, chithaiat):
    ren = ['thanhKy', 'xichKy', 'hacKy']
    ren_name = [["HỢI", "TÝ", "SỬU", "DẦN", "MÃO", "THÌN",
                 "TỊ", "NGỌ", "MÙI", "THÂN", "DẬU", "TUẤT"],
                ["HỢI", "THÂN", "TỊ", "DẦN"],
                ["HỢI", "TUẤT", "DẬU", "THÂN", "MÙI", "NGỌ", "TỊ", "THÌN", "MÃO", "DẦN", "SỬU", "TÝ"]]
    ren_number = [[0, 12, 1], [1, 4, 1], [25, 36, 3]]
    exc = [15, 13, 11]
    b = 0
    c = 0
    ketQua = [0, 0, 0]
    for i in range(len(ren)):
        b = ren_name[i]
        c = ren_number[i]
        so = AnChungCacSao(tichso, c[0], c[1], c[2])
        tencung = b[(math.floor(so - 1))]
        ketQua[i] = ttcung.index(tencung) + 1
        if ((chithaiat == "TỊ") or (chithaiat == "HỢI")):
            ketQua[i] = exc[i]
    return ketQua


def TonHoangThoiDePhiNgu358(tichso, amduongcuc):
    ren = ['thienTon', 'thienHoang', 'thienThoi', 'dePhu',
           'phiDieu', 'nguHanh', 'tamPhong', 'nguPhong', 'batPhong']
    duong_name = [["TÝ", "DẬU", "NGỌ", "MÃO"],
                  ["THÂN", "DẬU", "TUẤT", "CÀN", "CÀN", "HỢI", "TÝ", "SỬU", "CẤN",
                   "CẤN", "DẦN", "MÃO", "THÌN", "TỐN", "TỐN", "TỊ", "NGỌ", "MÙI", "KHÔN", "KHÔN"],
                  ["DẦN", "MÃO", "THÌN", "TỊ", "NGỌ", "MÙI",
                      "THÂN", "DẬU", "TUẤT", "HỢI", "TÝ", "SỬU"],
                  ["TUẤT", "CÀN", "HỢI", "TÝ", "TÝ", "SỬU", "CẤN", "DẦN", "MÃO", "MÃO",
                      "THÌN", "TỐN", "TỊ", "NGỌ", "NGỌ", "MÙI", "KHÔN", "THÂN", "DẬU", "DẬU"],
                  ["CÀN", "NGỌ", "CẤN", "MÃO", "TRUNG", "DẬU", "KHÔN", "TÝ", "TỐN"],
                  ["CÀN", "TÝ", "CẤN", "TỐN", "KHÔN"],
                  ["CẤN", "KHÔN", "NGỌ", "DẬU", "CÀN",
                      "TRUNG", "TỐN", "MÃO", "TÝ"],
                  ["CÀN", "CẤN", "TRUNG", "KHÔN", "TỐN", "NGỌ", "MÃO", "DẬU", "TÝ"],
                  ["NGỌ", "CẤN", "MÃO", "TRUNG", "DẬU", "KHÔN", "TÝ", "TỐN", "CÀN"]]
    am_name = [["MÃO", "NGỌ", "DẬU", "TÝ"],
               ["DẦN", "CẤN", "CẤN", "SỬU", "TÝ", "HỢI", "CÀN", "CÀN", "TUẤT", "DẬU",
                "THÂN", "KHÔN", "KHÔN", "MÙI", "NGỌ", "TỊ", "TỐN", "TỐN", "THÌN", "MÃO"],
               ["THÂN", "MÙI", "NGỌ", "TỊ", "THÌN", "MÃO",
                   "DẦN", "SỬU", "TÝ", "HỢI", "TUẤT", "DẬU"],
               ["THÌN", "MÃO", "MÃO", "DẦN", "CẤN", "SỬU", "TÝ", "TÝ", "HỢI", "CÀN",
                   "TUẤT", "DẬU", "DẬU", "THÂN", "KHÔN", "MÙI", "NGỌ", "NGỌ", "TỊ", "TỐN"],
               ["TỐN", "TÝ", "KHÔN", "DẬU", "TRUNG", "MÃO", "CẤN", "NGỌ", "CÀN"],
               ["TỐN", "NGỌ", "KHÔN", "CÀN", "CẤN"],
               ["KHÔN", "CẤN", "TÝ", "MÃO", "TỐN", "TRUNG", "CÀN", "DẬU", "LY"],
               ["TỐN", "KHÔN", "TRUNG", "CẤN", "CÀN", "TÝ", "DẬU", "MÃO", "NGỌ"],
               ["TÝ", "KHÔN", "DẬU", "TRUNG", "MÃO", "CẤN", "NGỌ", "CÀN", "TỐN"]]
    ren_number = [[0, 4, 1], [0, 20, 1], [0, 12, 1], [0, 20, 1],
                  [0, 9, 1], [0, 5, 1], [0, 9, 1], [0, 9, 1], [0, 9, 1]]
    tencung = ''
    ketQua = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(len(ren)):
        c = ren_number[i]
        so = AnChungCacSao(tichso, c[0], c[1], c[2])
        if (amduongcuc == 1):
            b = duong_name[i]
            tencung = b[(math.floor(so - 1))]
        else:
            b = am_name[i]
            tencung = b[(math.floor(so - 1))]
        ketQua[i] = ttcung.index(tencung) + 1
    return ketQua


def AnChungCacSao(tichso, doanhsai, vonglon, vongnho):
    tich = tichso + doanhsai
    a = math.floor((tich - 1) % vonglon)
    b = math.floor(a / vongnho)
    sttcungan = b + 1
    sonamdaqua = math.floor(a % vongnho) + 1
    return sttcungan


def Sort(ansao, sttCung):
    mang = []
    for i in range(len(ansao)):
        if ansao[i] == sttCung:
            mang.append(i)
        else:
            mang.append(99)
    t = 0
    for i in range(len(ansao)+2):
        for j in range(len(ansao)-1):
            if mang[j] > mang[j+1]:
                t = mang[j+1]
                mang[j+1] = mang[j]
                mang[j] = t
    return mang


def Assign(mang, tinhdau):
    cung = []
    for i in range(len(mang)):
        if mang[i] < 99:
            cung.append(tinhdau[mang[i]])
        else:
            cung.append("")
    return cung


def AnSao(chithaiat, tichso, amduongcuc, tuke):
    tinhdau = ["Ngũ phúc", "Đại du", "Quân cơ", "Thần cơ", "Dân cơ", "Tứ thần", "Thiên ất", "Địa ất", "Trực phù", "Thanh kỳ", "Xích kỳ", "Hắc kỳ", "Thiên tôn",
               "Thiên hoàng", "Thiên thời", "Đế phù", "Phi điểu",  "Ngũ hành",  "Tam phong", "Ngũ phong", "Bát phong", "Đại mục", "Tiểu mục", "Thái tuế", "Thái âm", "Hợp thần"]
    tuke_arr = ['Kể năm', 'Kể tháng', 'Kể ngày', 'Kể giờ',
                'Kể ngày tích đông chí', ' Kể giờ tích đông chí']
    t = ['Thái tuế', 'Nguyệt kiến', 'Nhật thần',
         'Thời thần', 'Nhật thần', 'Thời thần']
    tinhdau[23] = t[tuke_arr.index(tuke)]
    a = NguPhucDaiDuTamCoTuThanDaiTieumuc(tichso)
    b = TamKy(tichso, chithaiat)
    c = TonHoangThoiDePhiNgu358(tichso, amduongcuc)
    d = AnThaiTueThaiAmHopThan(chithaiat)
    ansao = [a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], b[0], b[1],
             b[2], c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], a[9], a[10]]
    ketQua = []
    for i in range(17):
        ketQua.append(Assign(Sort(ansao, i+1), tinhdau))
    return ketQua
