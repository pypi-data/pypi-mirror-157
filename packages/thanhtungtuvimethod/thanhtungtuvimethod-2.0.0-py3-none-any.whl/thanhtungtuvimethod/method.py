import math

canGoc = ["GIÁP", "ẤT", "BÍNH", "ĐINH",
          "MẬU", "KỶ", "CANH", "TÂN", "NHÂM", "QUÝ"]
chiGoc = ["TÝ", "SỬU", "DẦN", "MÃO", "THÌN",
          "TỊ", "NGỌ", "MÙI", "THÂN", "DẬU", "TUẤT", "HỢI"]
listCanChi = ["GIÁP TÝ",
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


def ChiTangCan(chi):
    tang = ['Quý', 'Kỷ Quý Tân', 'Giáp Bính Mậu', 'Ất', 'Mậu Ất Quý', 'Bính Mậu Canh',
            'Đinh Kỷ', 'Kỷ Đinh Ất', 'Canh Nhâm Mậu', 'Tân', 'Mậu Tân Đinh', 'Nhâm Giáp']
    return tang[chiGoc.index(chi)]


def ThapThanTuTru(canNgay, canTinh):
    thapThan = [["Tỷ kiên", "Kiếp tài", "Thực thần", "Thương quan", "Thiên tài", "Chính tài", "Thất sát", "Chính quan", "Kiêu thần", "Chính ấn"],
                ["Kiếp tài", "Tỷ kiên", "Thương quan", "Thực thần", "Chính tài",
                 "Thiên tài", "Chính quan", "Thất sát", "Chính ấn",  "Kiêu thần"],
                ["Kiêu thần", "Chính ấn", "Tỷ kiên", "Kiếp tài", "Thực thần",
                 "Thương quan", "Thiên tài", "Chính tài", "Thất sát", "Chính quan"],
                ["Chính ấn", "Kiêu thần", "Kiếp tài", "Tỷ kiên",  "Thương quan",
                 "Thực thần",  "Chính tài", "Thiên tài", "Chính quan", "Thất sát"],
                ["Thất sát", "Chính quan", "Kiêu thần", "Chính ấn", "Tỷ kiên",
                 "Kiếp tài", "Thực thần", "Thương quan", "Thiên tài", "Chính tài"],
                ["Chính quan", "Thất sát", "Chính ấn", "Kiêu thần", "Kiếp tài",
                 "Tỷ kiên", "Thương quan", "Thực thần", "Chính tài",  "Thiên tài"],
                ["Thiên tài", "Chính tài", "Thất sát", "Chính quan", "Kiêu thần",
                 "Chính ấn", "Tỷ kiên", "Kiếp tài", "Thực thần", "Thương quan"],
                ["Chính tài", "Thiên tài", "Chính quan", "Thất sát", "Chính ấn",
                 "Kiêu thần", "Kiếp tài", "Tỷ kiên", "Thương quan", "Thực thần"],
                ["Thực thần", "Thương quan", "Thiên tài", "Chính tài", "Thất sát",
                 "Chính quan", "Kiêu thần", "Chính ấn", "Tỷ kiên", "Kiếp tài"],
                ["Thương quan", "Thực thần", "Chính tài", "Thiên tài", "Chính quan",
                 "Thất sát", "Chính ấn", "Kiêu thần", "Kiếp tài", "Tỷ kiên"],
                ]
    return thapThan[canGoc.index(canNgay)][canGoc.index(canTinh)]


def ThuanNghich(canNam, namNu):
    ketqua = 0
    a = canGoc.index(canNam)
    if ((a % 2 == 0) and (namNu == 1)) or ((a % 2 != 0) and (namNu == 0)):
        ketqua = 1
    else:
        ketqua = 0
    return ketqua


def AmNamDuongNu(canNam, namNu):
    ad = ['Dương', 'Âm']
    nn = ['Nữ', 'Nam']
    return ad[canGoc.index(canNam) % 2] + " " + nn[namNu]


def ListSoDaiVanTuTru(soNgayQua):
    ketqua = ["0", "", "", "", "", "", "", "", "", "", "", ""]
    s = math.floor(soNgayQua / 3 + 1)
    for i in range(len(ketqua)-1):
        ketqua[i+1] = (s + 10 * i)
    return ketqua


def ListCanChiDaiVanTuTru(canChiThang, thuanNghich):

    a = listCanChi.index(canChiThang)
    ketqua = [canChiThang, "", "", "", "", "", "", "", "", "", "", ""]
    for i in range(len(ketqua)):
        if thuanNghich == 1:
            ketqua[i] = listCanChi[(a + i) % 60]
        else:
            ketqua[i] = listCanChi[(a + 60 - i) % 60]
    return ketqua


def SttCanChi(canORchi):
    ketqua = 0
    try:
        ketqua = canGoc.index(canORchi)+1
    except:
        ketqua = chiGoc.index(canORchi)+1
    return ketqua


def NguHanhNapAm(can, chi):
    napam = [["Hải trung Kim", "", "Giản hạ Thủy", "", "Tích lịch Hỏa", "", "Ốc thượng Thổ", "", "Tang đố Mộc", ""],
             ["", "Hải trung Kim", "", "Giản hạ Thủy", "",
              "Tích lịch Hỏa", "", "Ốc thượng Thổ", "", "Tang đố Mộc"],
             ["Đại khê Thủy", "", "Lư trung Hỏa", "", "Thành đầu Thổ",
              "", "Tùng bách Mộc", "", "Kim bạc Kim", ""],
             ["", "Đại khê Thủy", "", "Lư trung Hỏa", "",
              "Thành đầu Thổ", "", "Tùng bách Mộc", "", "Kim bạc Kim"],
             ["Phúc đăng Hỏa", "", "Sa trung Thổ", "", "Đại lâm Mộc",
              "", "Bạch lạp Kim", "", "Trường lưu Thủy", ""],
             ["", "Phúc đăng Hỏa", "", "Sa trung Thổ", "", "Đại lâm Mộc",
              "", "Bạch lạp Kim", "", "Trường lưu Thủy"],
             ["Sa trung Kim", "", "Thiên hà Thủy", "", "Thiên thượng Hỏa",
              "", "Lộ bàng Thổ", "", "Dương liễu Mộc", ""],
             ["", "Sa trung Kim", "", "Thiên hà Thủy", "",
              "Thiên thượng Hỏa", "", "Lộ bàng Thổ", "", "Dương liễu Mộc"],
             ["Tuyền trung Thủy", "", "Sơn hạ Hỏa", "", "Đại trạch Thổ",
              "", "Thạch lựu Mộc", "", "Kiếm phong Kim", ""],
             ["", "Tuyền trung Thủy", "", "Sơn hạ Hỏa", "",
              "Đại trạch Thổ", "", "Thạch lựu Mộc", "", "Kiếm phong Kim"],
             ["Sơn đầu Hỏa", "", "Ốc thượng Thổ", "", "Bình địa Mộc",
              "", "Thoa xuyến Kim", "", "Đại hải Thủy", ""],
             ["", "Sơn đầu Hỏa", "", "Ốc thượng Thổ", "", "Bình địa Mộc",
              "", "Thoa xuyến Kim", "", "Đại hải Thủy"]
             ]
    return napam[chiGoc.index(chi)][canGoc.index(can)]


def SoCungAnMenh(soChiThang, soChiGio):
    return (soChiThang - soChiGio + 12) % 12


def LyAmDuongThuanNghich(chiThang, chiGio, canNam):
    ketqua = ""
    soChiThang = chiGoc.index(chiThang)
    soChiGio = chiGoc.index(chiGio)
    menhCung = SoCungAnMenh(soChiThang, soChiGio)
    menhCung = menhCung % 2
    a = canGoc.index(canNam)
    if menhCung == a:
        ketqua = "Âm Dương thuận lý"
    else:
        ketqua = "Âm Dương nghịch lý"
    return ketqua

# Trả về một array khởi đầu là Lục thân của cung Tý, an cung Thân


def ListCungMenhThan(chiThang, chiGio):
    cungLucThan = ["MỆNH", "PHỤ MẪU", "PHÚC ĐỨC", "ĐIỀN TRẠCH", "QUAN LỘC", "NÔ BỘC",
                   "THIÊN DI", "TẬT ÁCH", "TÀI BẠCH", "TỬ TỨC", "PHU THÊ", "HUYNH ĐỆ"]
    ketqua = ['', '', '', '', '', '', '', '', '', '', '', '']
    soThang = chiGoc.index(chiThang)
    soGio = chiGoc.index(chiGio)
    s = SoCungAnMenh(soThang, soGio)
    h = (12-s) % 12
    for i in range(len(cungLucThan)):
        ketqua[i] = cungLucThan[(h+i) % 12]
    cungThan = (soThang + soGio) % 12
    ketqua[cungThan] += ' (THÂN)'
    return ketqua


def SaoChuMenhThan(chiNam):

    menhChu = ["Tham lang", "Cự môn", "Lộc tồn", "Văn khúc", "Liêm trinh", "Vũ khúc",
               "Phá quân", "Vũ khúc", "Liêm trinh", "Văn khúc", "Lộc tồn", "Cự môn"]
    thanChu = ["Linh tinh", "Thiên tướng", "Thiên lương", "Thiên đồng", "Văn xương",
               "Thiên cơ", "Hỏa tinh", "Thiên tướng", "Linh tinh", "Thiên đồng", "Văn xương", "Thiên cơ"]
    a = chiGoc.index(chiNam)
    ketqua = [menhChu[a], thanChu[a]]
    return ketqua


def CucSo(canNam, chiThang, chiGio):
    cungMenh = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1]
    cungMenh2 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    canCung = [
        ["BÍNH", "MẬU", "CANH", "NHÂM", "GIÁP",
         "BÍNH", "MẬU", "CANH", "NHÂM", "GIÁP"],
        ["ĐINH", "KỶ", "TÂN", "QUÝ", "ẤT",
         "ĐINH", "KỶ", "TÂN", "QUÝ", "ẤT"],
        ["MẬU", "CANH", "NHÂM", "GIÁP", "BÍNH",
         "MẬU", "CANH", "NHÂM", "GIÁP", "BÍNH"],
        ["KỶ", "TÂN", "QUÝ", "ẤT", "ĐINH",
         "KỶ", "TÂN", "QUÝ", "ẤT", "ĐINH"],
        ["CANH", "NHÂM", "GIÁP", "BÍNH", "MẬU",
         "CANH", "NHÂM", "GIÁP", "BÍNH", "MẬU"],
        ["TÂN", "QUÝ", "ẤT", "ĐINH", "KỶ",
         "TÂN", "QUÝ", "ẤT", "ĐINH", "KỶ"],
        ["NHÂM", "GIÁP", "BÍNH", "MẬU", "CANH",
         "NHÂM", "GIÁP", "BÍNH", "MẬU", "CANH"],
        ["QUÝ", "ẤT", "ĐINH", "KỶ", "TÂN",
         "QUÝ", "ẤT", "ĐINH", "KỶ", "TÂN"],
        ["GIÁP", "BÍNH", "MẬU", "CANH", "NHÂM",
         "GIÁP", "BÍNH", "MẬU", "CANH", "NHÂM"],
        ["ẤT", "ĐINH", "KỶ", "TÂN", "QUÝ",
         "ẤT", "ĐINH", "KỶ", "TÂN", "QUÝ"],
        ["BÍNH", "MẬU", "CANH", "NHÂM", "GIÁP",
         "BÍNH", "MẬU", "CANH", "NHÂM", "GIÁP"],
        ["ĐINH", "KỶ", "TÂN", "QUÝ", "ẤT",
         "ĐINH", "KỶ", "TÂN", "QUÝ", "ẤT"]
    ]
    cucso = [
        ["Kim Tứ Cục", "", "Thủy Nhị Cục", "", "Hỏa Lục Cục",
         "", "Thổ Ngũ Cục", "", "Mộc Tam Cục", ""],
        ["", "Kim Tứ Cục", "", "Thủy Nhị Cục", "",
         "Hỏa Lục Cục", "", "Thổ Ngũ Cục", "", "Mộc Tam Cục"],
        ["Thủy Nhị Cục", "", "Hỏa Lục Cục", "", "Thổ Ngũ Cục",
         "", "Mộc Tam Cục", "", "Kim Tứ Cục", ""],
        ["", "Thủy Nhị Cục", "", "Hỏa Lục Cục", "",
         "Thổ Ngũ Cục", "", "Mộc Tam Cục", "", "Kim Tứ Cục"],
        ["Hỏa Lục Cục", "", "Thổ Ngũ Cục", "", "Mộc Tam Cục",
         "", "Kim Tứ Cục", "", "Thủy Nhị Cục", ""],
        ["", "Hỏa Lục Cục", "", "Thổ Ngũ Cục", "",
         "Mộc Tam Cục", "", "Kim Tứ Cục", "", "Thủy Nhị Cục"],
        ["Kim Tứ Cục", "", "Thủy Nhị Cục", "", "Hỏa Lục Cục",
         "", "Thổ Ngũ Cục", "", "Mộc Tam Cục", ""],
        ["", "Kim Tứ Cục", "", "Thủy Nhị Cục", "",
         "Hỏa Lục Cục", "", "Thổ Ngũ Cục", "", "Mộc Tam Cục"],
        ["Thủy Nhị Cục", "", "Hỏa Lục Cục", "", "Thổ Ngũ Cục",
         "", "Mộc Tam Cục", "", "Kim Tứ Cục", ""],
        ["", "Thủy Nhị Cục", "", "Hỏa Lục Cục", "",
         "Thổ Ngũ Cục", "", "Mộc Tam Cục", "", "Kim Tứ Cục"],
        ["Hỏa Lục Cục", "", "Thổ Ngũ Cục", "", "Mộc Tam Cục",
         "", "Kim Tứ Cục", "", "Thủy Nhị Cục", ""],
        ["", "Hỏa Lục Cục", "", "Thổ Ngũ Cục", "",
         "Mộc Tam Cục", "", "Kim Tứ Cục", "", "Thủy Nhị Cục"]
    ]
    a = SoCungAnMenh(chiGoc.index(chiThang), chiGoc.index(chiGio))
    canCungMenh = canCung[cungMenh.index(a)][canGoc.index(canNam)]
    return cucso[cungMenh2.index(a)][canGoc.index(canCungMenh)]


def SoCuc_int(canNam, chiThang, chiGio):
    cucso = CucSo(canNam, chiThang, chiGio)
    r1 = ["Thủy Nhị Cục", "Mộc Tam Cục",
          "Kim Tứ Cục", "Thổ Ngũ Cục", "Hỏa Lục Cục"]
    r2 = [2, 3, 4, 5, 6]
    return r2[r1.index(cucso)]
# DaiVan return 1 array tu cungTy di thuan


def DaiVan(canNam, chiThang, chiGio, thuanNghich):
    cucso = CucSo(canNam, chiThang, chiGio)
    cunganmenh = SoCungAnMenh(chiGoc.index(chiThang), chiGoc.index(chiGio))
    r1 = ["Thủy Nhị Cục", "Mộc Tam Cục",
          "Kim Tứ Cục", "Thổ Ngũ Cục", "Hỏa Lục Cục"]
    r2 = [2, 3, 4, 5, 6]
    soCuc = r2[r1.index(cucso)]
    sttcungan = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for i in range(len(sttcungan)):
        if thuanNghich == 1:
            sttcungan[i] = ((cunganmenh + i) % 12)
        else:
            sttcungan[i] = ((cunganmenh + 12 - i) % 12)

    cung = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(len(cung)):
        cung[i] = sttcungan.index(i)
    cungcucso = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cungcucso[0] = soCuc
    for i in range(len(cungcucso)):
        cungcucso[i] = soCuc+10*i
    ketQua = ["", "", "", "", "", "", "", "", "", "", "", ""]
    for i in range(len(ketQua)):
        ketQua[i] = cungcucso[cung[i]]

    return ketQua


def VongTuViThienPhu(soNgay, soCuc):
    soTuVi = [[2, 5, 12, 7, 10],
              [3, 2, 5, 12, 7],
              [3, 3, 2, 5, 12],
              [4, 6, 3, 2, 5],
              [4, 3, 1, 3, 2],
              [5, 4, 6, 8, 3],
              [5, 7, 3, 1, 11],
              [6, 4, 4, 6, 8],
              [6, 5, 2, 3, 1],
              [7, 8, 7, 4, 6],
              [7, 5, 4, 9, 3],
              [8, 6, 5, 2, 4],
              [8, 9, 3, 7, 12],
              [9, 6, 8, 4, 9],
              [9, 7, 5, 5, 2],
              [10, 10, 6, 10, 7],
              [10, 7, 4, 3, 4],
              [11, 8, 9, 8, 5],
              [11, 11, 6, 5, 1],
              [12, 8, 7, 6, 10],
              [12, 9, 5, 11, 3],
              [1, 12, 10, 4, 8],
              [1, 9, 7, 9, 5],
              [2, 10, 8, 6, 6],
              [2, 1, 6, 7, 2],
              [3, 10, 11, 12, 11],
              [3, 11, 8, 5, 4],
              [4, 2, 9, 10, 9],
              [4, 11, 7, 7, 6],
              [5, 12, 12, 8, 7]
              ]
    listTuVi = ["TỬ VI", "LIÊM TRINH", "THIÊN ĐỒNG",
                "VŨ KHÚC", "THÁI DƯƠNG", "THIÊN CƠ"]
    ketQua = ["", "", "", "", "", "", "", "", "", "", "",
              "", "", "", "", "", "", "", "", "", "", "", "", ""]
    list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    listThienPhu = ["THIÊN PHỦ", "THÁI ÂM", "THAM LANG",
                    "CỰ MÔN", "THIÊN TƯỚNG", "THIÊN LƯƠNG", "THẤT SÁT", "PHÁ QUÂN"]
    ssTuVi = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    ssThienPhu = [5, 4, 3, 2, 1, 12, 11, 10, 9, 8, 7, 6]
    tuVi = soTuVi[soNgay - 1][soCuc - 2]
    liemTrinh = ((tuVi + 3) % 12) + 1
    thienDong = ((tuVi + 6) % 12) + 1
    vuKhuc = ((tuVi + 7) % 12) + 1
    thaiDuong = ((tuVi + 8) % 12) + 1
    thienCo = ((tuVi + 10) % 12) + 1
    soCungTuVi = [tuVi, liemTrinh, thienDong,
                  vuKhuc, thaiDuong, thienCo]

    for i in range(12):
        for j in range(len(soCungTuVi)):
            if list[i] == soCungTuVi[j]:
                ketQua[i] = listTuVi[j]

    thienPhu = ssThienPhu[ssTuVi.index(tuVi)]
    thaiAm = ((thienPhu % 12) + 1)
    thamLang = (thienPhu + 1) % 12 + 1
    cuMon = (thienPhu + 2) % 12 + 1
    thienTuong = (thienPhu + 3) % 12 + 1
    thienLuong = (thienPhu + 4) % 12 + 1
    thatSat = (thienPhu + 5) % 12 + 1
    phaQuan = (thienPhu + 9) % 12 + 1
    soCungThienPhu = [thienPhu, thaiAm, thamLang,
                      cuMon, thienTuong, thienLuong, thatSat, phaQuan]
    for i in range(12):
        for j in range(len(soCungThienPhu)):
            if list[i] == soCungThienPhu[j]:
                ketQua[i+12] = listThienPhu[j]
    return ketQua


def VongBacSi_Ten(canNam, thuanNghich):
    ten = ["Bác sĩ", "Lực sĩ", "Thanh long", "Tiểu hao", "Tướng quân",
           "Tấu thư", "Phi liêm", "Hỷ thần", "Bệnh phù", "Đại hao", "Phục binh", "Quan phủ"]
    cungGocBS = [3, 4, 6, 7, 6, 7, 9, 10, 12, 1]
    s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cung = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ketQua = ["", "", "", "", "", "", "", "", "", "", "", ""]
    bacSi = cungGocBS[canGoc.index(canNam)]
    for i in range(len(s)):
        if thuanNghich == 1:
            s[i] = ((bacSi - 1 + i) % 12) + 1
        else:
            s[i] = ((bacSi + 11 - i) % 12) + 1

    for i in range(12):
        cung[i] = s.index(i+1)

    for i in range(12):
        ketQua[i] = ten[cung[i]]
    return ketQua


def VongBacSi_So(canNam, thuanNghichAmNamDuongNu):
    bacSi = [3, 4, 6, 7, 6, 7, 9, 10, 12, 1]
    lucSi_t = [4, 5, 7, 8, 7, 8, 10, 11, 1, 2]
    thanhLong_t = [5, 6, 8, 9, 8, 9, 11, 12, 2, 3]
    tieuHao_t = [6, 7, 9, 10, 9, 10, 12, 1, 3, 4]
    tuongQuan_t = [7, 8, 10, 11, 10, 11, 1, 2, 4, 5]
    tauThu_t = [8, 9, 11, 12, 11, 12, 2, 3, 5, 6]
    phiLiem_t = [9, 10, 12, 1, 12, 1, 3, 4, 6, 7]
    hyThan_t = [10, 11, 1, 2, 1, 2, 4, 5,  7, 8]
    benhPhu_t = [11, 12, 2, 3, 2, 3, 5, 6, 8, 9]
    daiHao_t = [12, 1, 3, 4, 3, 4, 6, 7, 9, 10]
    phucBinh_t = [1, 2, 4, 5, 4, 5, 7, 8, 10, 11]
    quanPhu_t = [2, 3, 5, 6, 5, 6, 8, 9, 11, 12]

    lucSi_n = quanPhu_t
    thanhLong_n = phucBinh_t
    tieuHao_n = daiHao_t
    tuongQuan_n = benhPhu_t
    tauThu_n = hyThan_t
    phiLiem_n = phiLiem_t
    hyThan_n = tauThu_t
    benhPhu_n = tuongQuan_t
    daiHao_n = tieuHao_t
    phucBinh_n = thanhLong_t
    quanPhu_n = lucSi_t
    a = canGoc.index(canNam)
    if(thuanNghichAmNamDuongNu == 1):
        ketQua = [bacSi[a], lucSi_t[a], thanhLong_t[a], tieuHao_t[a], tuongQuan_t[a], tauThu_t[a],
                  phiLiem_t[a], hyThan_t[a], benhPhu_t[a], daiHao_t[a], phucBinh_t[a], quanPhu_t[a]]
    else:
        ketQua = [bacSi[a], lucSi_n[a], thanhLong_n[a], tieuHao_n[a], tuongQuan_n[a], tauThu_n[a],
                  phiLiem_n[a], hyThan_n[a], benhPhu_n[a], daiHao_n[a], phucBinh_n[a], quanPhu_n[a]]
    return ketQua


def VongBacSi_SoLuuNien(canNam):
    bacSi = [3, 4, 6, 7, 6, 7, 9, 10, 12, 1]
    lucSi_t = [4, 5, 7, 8, 7, 8, 10, 11, 1, 2]
    thanhLong_t = [5, 6, 8, 9, 8, 9, 11, 12, 2, 3]
    tieuHao_t = [6, 7, 9, 10, 9, 10, 12, 1, 3, 4]
    tuongQuan_t = [7, 8, 10, 11, 10, 11, 1, 2, 4, 5]
    tauThu_t = [8, 9, 11, 12, 11, 12, 2, 3, 5, 6]
    phiLiem_t = [9, 10, 12, 1, 12, 1, 3, 4, 6, 7]
    hyThan_t = [10, 11, 1, 2, 1, 2, 4, 5,  7, 8]
    benhPhu_t = [11, 12, 2, 3, 2, 3, 5, 6, 8, 9]
    daiHao_t = [12, 1, 3, 4, 3, 4, 6, 7, 9, 10]
    phucBinh_t = [1, 2, 4, 5, 4, 5, 7, 8, 10, 11]
    quanPhu_t = [2, 3, 5, 6, 5, 6, 8, 9, 11, 12]

    lucSi_n = quanPhu_t
    thanhLong_n = phucBinh_t
    tieuHao_n = daiHao_t
    tuongQuan_n = benhPhu_t
    tauThu_n = hyThan_t
    phiLiem_n = phiLiem_t
    hyThan_n = tauThu_t
    benhPhu_n = tuongQuan_t
    daiHao_n = tieuHao_t
    phucBinh_n = thanhLong_t
    quanPhu_n = lucSi_t
    a = canGoc.index(canNam)
    if(a % 2 == 0):
        ketQua = [bacSi[a], lucSi_t[a], thanhLong_t[a], tieuHao_t[a], tuongQuan_t[a], tauThu_t[a],
                  phiLiem_t[a], hyThan_t[a], benhPhu_t[a], daiHao_t[a], phucBinh_t[a], quanPhu_t[a]]
    else:
        ketQua = [bacSi[a], lucSi_n[a], thanhLong_n[a], tieuHao_n[a], tuongQuan_n[a], tauThu_n[a],
                  phiLiem_n[a], hyThan_n[a], benhPhu_n[a], daiHao_n[a], phucBinh_n[a], quanPhu_n[a]]
    return ketQua


def VongTuongTinh_Ten(chiNam):
    ten = ["Tướng tinh", "Phan an", "Tuế dịch", "Tức thần", "Hoa cái",
           "Kiếp sát", "Tai sát", "Thiên sát", "Chỉ bối", "Đào hoa", "Nguyệt sát", "Vong thần"]
    cungGocTT = [1, 10, 7, 4, 1, 10, 7, 4, 1, 10, 7, 4]
    s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cung = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ketQua = ["", "", "", "", "", "", "", "", "", "", "", ""]

    tuongTinh = cungGocTT[chiGoc.index(chiNam)]
    for i in range(12):
        s[i] = ((tuongTinh - 1 + i) % 12) + 1
    for i in range(12):
        cung[i] = s.index(i+1)
    for i in range(12):
        ketQua[i] = ten[cung[i]]

    return ketQua


def VongTuongTinh_So(chiNam):
    tuongTinh = [1, 10, 7, 4, 1, 10, 7, 4, 1, 10, 7, 4]
    phanAn = [2, 11, 8, 5, 2, 11, 8, 5, 2, 11, 8, 5]
    tueDich = [3, 12, 9, 6, 3, 12, 9, 6, 3, 12, 9, 6]
    tucThan = [4, 1, 10, 7, 4, 1, 10, 7, 4, 1, 10, 7]
    hoaCai = [5, 2, 11, 8, 5, 2, 11, 8, 5, 2, 11, 8]
    kiepSat = [6, 3, 12, 9, 6, 3, 12, 9, 6, 3, 12, 9]
    taiSat = [7, 4, 1, 10, 7, 4, 1, 10, 7, 4, 1, 10]
    thienSat = [8, 5, 2, 11, 8, 5, 2, 11, 8, 5, 2, 11]
    chiBoi = [9, 6, 3, 12, 9, 6, 3, 12, 9, 6, 3, 12]
    daoHoa = [10, 7, 4, 1, 10, 7, 4, 1, 10, 7, 4, 1]
    nguyetSat = [11, 8, 5, 2, 11, 8, 5, 2, 11, 8, 5, 2]
    vongThan = [12, 9, 6, 3, 12, 9, 6, 3, 12, 9, 6, 3]
    a = chiGoc.index(chiNam)
    ketQua = [tuongTinh[a], phanAn[a], tueDich[a], tucThan[a], hoaCai[a], kiepSat[a],
              taiSat[a], thienSat[a], chiBoi[a], daoHoa[a], nguyetSat[a], vongThan[a]]
    return ketQua


def VongThaiTue_Ten(chiNam):
    ten = ["Thái tuế", "Thiếu dương", "Tang môn", "Thiếu âm", "Quan phù",
           "Tử phù", "Tuế phá", "Long đức", "Bạch hổ", "Phúc đức", "Điếu khách", "Trực phù"]
    cungGocThaiTue = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cung = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ketQua = ["", "", "", "", "", "", "", "", "", "", "", ""]

    thaiTue = cungGocThaiTue[chiGoc.index(chiNam)]
    for i in range(12):
        s[i] = ((thaiTue - 1 + i) % 12) + 1

    for i in range(12):
        cung[i] = s.index(i+1)

    for i in range(12):
        ketQua[i] = ten[cung[i]]

    return ketQua


def VongThaiTue_So(chiNam):
    thaiTue = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    thieuDuong = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1]
    tangMon = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2]
    thieuAm = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
    quanPhu = [5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4]
    tuPhu = [6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5]
    tuePha = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    longDuc = [8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7]
    bachHo = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8]
    phucDuc = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    dieuKhach = [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    trucPhu = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    a = chiGoc.index(chiNam)
    ketQua = [thaiTue[a], thieuDuong[a], tangMon[a], thieuAm[a], quanPhu[a], tuPhu[a],
              tuePha[a], longDuc[a], bachHo[a], phucDuc[a], dieuKhach[a], trucPhu[a]]
    return ketQua


def VongTrangSinh(soCuc, thuanNghich):
    cungGocTS = [9, 12, 6, 9, 3]
    ten = ["TRƯỜNG SINH", "MỘC DỤC", "QUAN ĐỚI", "LÂM QUAN",
           "ĐẾ VƯỢNG", "SUY", "BỆNH", "TỬ", "MỘ", "TUYỆT", "THAI", "DƯỠNG"]
    cung = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ketQua = ["", "", "", "", "", "", "", "", "", "", "", ""]

    truongSinh = cungGocTS[soCuc - 2]
    for i in range(12):
        if thuanNghich == 1:
            s[i] = ((truongSinh - 1 + i) % 12) + 1
        else:
            s[i] = ((truongSinh + 11 - i) % 12) + 1

    for i in range(12):
        cung[i] = s.index(i+1)

    for i in range(12):
        ketQua[i] = ten[cung[i]]

    return ketQua


def TuanTriet(canNam, chiNam):
    bangtriet = ["910", "78", "56", "34", "12", "910", "78", "56", "34", "12"]
    bangtuan = [
        ["1112", "", "12", "", "34", "", "56", "", "78", "", "910", ""],
        ["", "1112", "", "12", "", "34", "", "56", "", "78", "", "910"],
        ["910", "", "1112", "", "12", "", "34", "", "56", "", "78", ""],
        ["", "910", "", "1112", "", "12", "", "34", "", "56", "", "78"],
        ["78", "", "910", "", "1112", "", "12", "", "34", "", "56", ""],
        ["", "78", "", "910", "", "1112", "", "12", "", "34", "", "56"],
        ["56", "", "78", "", "910", "", "1112", "", "12", "", "34", ""],
        ["", "56", "", "78", "", "910", "", "1112", "", "12", "", "34"],
        ["34", "", "56", "", "78", "", "910", "", "1112", "", "12", ""],
        ["", "34", "", "56", "", "78", "", "910", "", "1112", "", "12"]
    ]
    tuan = bangtuan[canGoc.index(canNam)][chiGoc.index(chiNam)]
    triet = bangtriet[canGoc.index(canNam)]
    ketQua = [tuan, triet]
    return ketQua
# Tất cả các sao phụ lấy cung Tý là cung số 1, tuần tự đến Hợi là số 12


def LocTon(canNam):
    cungGocLocTon = [3, 4, 6, 7, 6, 7, 9, 10, 12, 1]
    return cungGocLocTon[canGoc.index(canNam)]


def LocKinhDa_So(canNam):
    locTon = [3, 4, 6, 7, 6, 7, 9, 10, 12, 1]
    kinhDuong = [4, 5, 7, 8, 7, 8, 10, 11, 1, 2]
    daLa = [2, 3, 5, 6, 5, 6, 8, 9, 11, 12]
    a = canGoc.index(canNam)
    ketQua = [locTon[a], kinhDuong[a], daLa[a]]
    return ketQua


def ThienKhoc_So(chiNam):
    thienKhoc = [7, 6, 5, 4, 3, 2, 1, 12, 11, 10, 9, 8]
    return thienKhoc[chiGoc.index(chiNam)]


def TaHuuHinhDieuThienDiaGiai(chiThang):
    taphu = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2]
    huubat = [1, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    thienhinh = [8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7]
    thiendieu = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    thiengiai = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    diagiai = [6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5]
    a = chiGoc.index(chiThang)
    ketQua = [taphu[a], huubat[a], thienhinh[a],
              thiendieu[a], thiengiai[a], diagiai[a]]
    return ketQua


def XuongKhucKhongKiepPhuCao(chiGio):
    vankhuc = [5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4]
    vanxuong = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 12]
    diakhong = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    diakiep = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    thaiphu = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    phongcao = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2]
    a = chiGoc.index(chiGio)
    ketQua = [vanxuong[a], vankhuc[a], diakhong[a],
              diakiep[a], thaiphu[a], phongcao[a]]
    return ketQua


def KhoiVietTruHaQuanPhuc(canNam):
    thienkhoi = [2, 1, 12, 12, 2, 1, 2, 7, 4, 4]
    thienviet = [8, 9, 10, 10, 8, 9, 8, 3, 6, 6]
    thientru = [6, 7, 1, 6, 7, 9, 3, 7, 10, 12]
    luuha = [10, 11, 8, 9, 6, 7, 4, 5, 12, 3]
    thienquan = [8, 5, 6, 3, 4, 10, 12, 10, 11, 7]
    thienphuc = [10, 9, 1, 12, 4, 3, 7, 6, 7, 6]
    a = canGoc.index(canNam)
    ketQua = [thienkhoi[a], thienviet[a], thientru[a],
              luuha[a], thienquan[a], thienphuc[a]]
    return ketQua


def MaHongHyLongPhuongThienducNguyetducCoQuaToaiKhocHuTaiThoKhong(chiNam, soChiGio, soChiThang):

    socungmenh = ((soChiThang - soChiGio + 12) % 12 + 1)
    socungthan = ((soChiThang + soChiGio + 10) % 12 + 1)
    thienma = [3, 12, 9, 6, 3, 12, 9, 6, 3, 12, 9, 6]
    hongloan = [4, 3, 2, 1, 12, 11, 10, 9, 8, 7, 6, 5]
    thienhy = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 12, 11]
    longtri = [5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4]
    phuongcac = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 12]
    thienduc = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    nguyetduc = [6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5]
    cothan = [3, 3, 6, 6, 6, 9, 9, 9, 12, 12, 12, 3]
    quatu = [11, 11, 2, 2, 2, 5, 5, 5, 8, 8, 8, 11]
    phatoai = [6, 2, 10, 6, 2, 10, 6, 2, 10, 6, 2, 10]
    thienkhoc = [7, 6, 5, 4, 3, 2, 1, 12, 11, 10, 9, 8]
    thienhu = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    thienkhong = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1]
    a = chiGoc.index(chiNam)
    thientai = (socungmenh + a - 1) % 12 + 1
    thientho = (socungthan + a - 1) % 12 + 1
    ketqua = [thienma[a], hongloan[a], thienhy[a], longtri[a], phuongcac[a], thienduc[a], nguyetduc[a],
              cothan[a], quatu[a], phatoai[a], thienkhoc[a], thienhu[a], thientai, thientho, thienkhong[a]]
    return ketqua


def HoaLinh(chiNam, thuanNghich, chiGio):
    khoihoa = [3, 4, 2, 10, 3, 4, 2, 10, 3, 4, 2, 10]
    khoilinh = [11, 11, 4, 11, 11, 11, 4, 11, 11, 11, 4, 11]
    sogio = chiGoc.index(chiGio)
    sonam = chiGoc.index(chiNam)
    hoatinh = 0
    inhtinh = 0
    if thuanNghich == 1:
        hoatinh = (khoihoa[sonam] + sogio - 1) % 12 + 1
        linhtinh = (khoilinh[sonam] + 11 - sogio) % 12 + 1
    else:
        hoatinh = (khoihoa[sonam] + 11 - sogio) % 12 + 1
        linhtinh = (khoilinh[sonam] + sogio - 1) % 12 + 1
    ketQua = [hoatinh, linhtinh]
    return ketQua


def TuHoa(canNam, soNgay, soCuc, chiThang, chiGio):
    bangantuvi = [
        [2, 5, 12, 7, 10],
        [3, 2, 5, 12, 7],
        [3, 3, 2, 5, 12],
        [4, 6, 3, 2, 5],
        [4, 3, 1, 3, 2],
        [5, 4, 6, 8, 3],
        [5, 7, 3, 1, 11],
        [6, 4, 4, 6, 8],
        [6, 5, 2, 3, 1],
        [7, 8, 7, 4, 6],
        [7, 5, 4, 9, 3],
        [8, 6, 5, 2, 4],
        [8, 9, 3, 7, 12],
        [9, 6, 8, 4, 9],
        [9, 7, 5, 5, 2],
        [10, 10, 6, 10, 7],
        [10, 7, 4, 3, 4],
        [11, 8, 9, 8, 5],
        [11, 11, 6, 5, 1],
        [12, 8, 7, 6, 10],
        [12, 9, 5, 11, 3],
        [1, 12, 10, 4, 8],
        [1, 9, 7, 9, 5],
        [2, 10, 8, 6, 6],
        [2, 1, 6, 7, 2],
        [3, 10, 11, 12, 11],
        [3, 11, 8, 5, 4],
        [4, 2, 9, 10, 9],
        [4, 11, 7, 7, 6],
        [5, 12, 12, 8, 7]
    ]
    tuvigocthienphu = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    thienphu = [5, 4, 3, 2, 1, 12, 11, 10, 9, 8, 7, 6]
    cungantuvi = bangantuvi[soNgay - 1][soCuc - 2]
    cunganliemtrinh = ((cungantuvi + 3) % 12) + 1
    cunganthiendong = ((cungantuvi + 6) % 12) + 1
    cunganvukhuc = ((cungantuvi + 7) % 12) + 1
    cunganthaiduong = ((cungantuvi + 8) % 12) + 1
    cunganthienco = ((cungantuvi + 10) % 12) + 1
    cunganthienphu = thienphu[tuvigocthienphu.index(cungantuvi)]
    cunganthaiam = ((cunganthienphu % 12) + 1)
    cunganthamlang = (cunganthienphu + 1) % 12 + 1
    cungancumon = (cunganthienphu + 2) % 12 + 1
    cunganthientuong = (cunganthienphu + 3) % 12 + 1
    cunganthienluong = (cunganthienphu + 4) % 12 + 1
    cunganthatsat = (cunganthienphu + 5) % 12 + 1
    cunganphaquan = (cunganthienphu + 9) % 12 + 1
    cungantaphu = TaHuuHinhDieuThienDiaGiai(chiThang)[0]
    cunganhuubat = TaHuuHinhDieuThienDiaGiai(chiThang)[1]
    cunganvanxuong = XuongKhucKhongKiepPhuCao(chiGio)[0]
    cunganvankhuc = XuongKhucKhongKiepPhuCao(chiGio)[1]

    can = [[cunganliemtrinh, cunganphaquan, cunganvukhuc, cunganthaiduong],
           [cunganthienco, cunganthienluong, cungantuvi, cunganthaiam],
           [cunganthiendong, cunganthienco, cunganvanxuong, cunganliemtrinh],
           [cunganthaiam, cunganthiendong, cunganthienco, cungancumon],
           [cunganthamlang, cunganthaiam, cunganhuubat, cunganthienco],
           [cunganvukhuc, cunganthamlang, cunganthienluong, cunganvankhuc],
           [cunganthaiduong, cunganvukhuc, cunganthaiam, cunganthiendong],
           [cungancumon, cunganthaiduong, cunganvankhuc, cunganvanxuong],
           [cunganthienluong, cungantuvi, cungantaphu, cunganvukhuc],
           [cunganphaquan, cungancumon, cunganthaiam, cunganthamlang]]
    a = canGoc.index(canNam)
    ketQua = can[a]

    return ketQua


def HongLoan_So(chiNam):
    hongLoan = [4, 3, 2, 1, 12, 11, 10, 9, 8, 7, 6, 5]
    return hongLoan[chiGoc.index(chiNam)]


def ThaiToaQuangQuyAnPhu(canNam, chiThang, soNgay, chiGio):
    cungantaphu = TaHuuHinhDieuThienDiaGiai(chiThang)[0]
    cunganhuubat = TaHuuHinhDieuThienDiaGiai(chiThang)[1]
    cunganvanxuong = XuongKhucKhongKiepPhuCao(chiGio)[0]
    cunganvankhuc = XuongKhucKhongKiepPhuCao(chiGio)[1]
    cunganlocton = LocTon(canNam)
    vanxuong = 0
    vankhuc = 0
    if (cunganvanxuong - 1 == 0):
        vanxuong = 12
    else:
        vanxuong = cunganvanxuong - 1
    if (cunganvankhuc + 1 == 13):
        vankhuc = 1
    else:
        vankhuc = cunganvankhuc + 1
    num = soNgay
    cungantamthai = (cungantaphu + (num - 1) % 12 - 1) % 12 + 1
    cunganbattoa = (cunganhuubat + 11 - (num - 1) % 12) % 12 + 1
    cungananquang = (vanxuong + (num - 1) % 12 - 1) % 12 + 1
    cunganthienquy = (vankhuc + 11 - (num - 1) % 12) % 12 + 1
    cunganquocan = (cunganlocton + 7) % 12 + 1
    cunganduongphu = (cunganlocton + 4) % 12 + 1
    ketqua = [cungantamthai, cunganbattoa, cungananquang,
              cunganthienquy, cunganquocan, cunganduongphu]
    return ketqua


def DauThuongSu(chiNam, chiThang, chiGio, soChiThang, soChiGio):

    sonam = chiGoc.index(chiNam) + 1
    sothang = ((chiGoc.index(chiThang) + 1) + 9) % 12 + 1
    sogio = chiGoc.index(chiGio) + 1
    dauquan = ((sonam + 11 - sothang + 1) % 12 + sogio - 1) % 12 + 1
    tencung = ["MỆNH", "PHỤ MẪU", "PHÚC ĐỨC", "ĐIỀN TRẠCH", "QUAN LỘC", "NÔ BỘC",
               "THIÊN DI", "TẬT ÁCH", "TÀI BẠCH", "TỬ TỨC", "PHU THÊ", "HUYNH ĐỆ"]
    socungmenh = (soChiThang - soChiGio + 12) % 12 + 1
    socungthienthuong_noboc = (socungmenh + 4) % 12 + 1
    socungthiensu_tatach = (socungmenh + 6) % 12 + 1
    ket = [dauquan, socungthienthuong_noboc, socungthiensu_tatach]
    return ket


def BubbleSort(arrAnSao, sttCung):
    t = 0
    arr = []
    for i in range(len(arrAnSao)):
        if arrAnSao[i] == sttCung:
            arr.append(i)
        else:
            arr.append(99)
    for i in range(len(arrAnSao)+2):
        for j in range(len(arrAnSao)-1):
            if arr[j] > arr[j+1]:
                t = arr[j+1]
                arr[j+1] = arr[j]
                arr[j] = t
    return arr


def Cung(mang):
    tinhdau = [
        "Lộc tồn",
        "Kình dương",
        "Đà la",
        "Tả phụ",
        "Hữu bật",
        "Văn xương",
        "Văn khúc",
        "Thiên khôi",
        "Thiên việt",
        "Địa không",
        "Địa kiếp",
        "Hỏa tinh",
        "Linh tinh",
        "HÓA LỘC",
        "HÓA QUYỀN",
        "HÓA KHOA",
        "HÓA KỴ",
        "Thiên mã",
        "Thiên hình",
        "Thiên diêu",
        "Cô thần",
        "Qủa tú",
        "Lưu hà",
        "Tam thai",
        "Bát tọa",
        "Ân quang",
        "Thiên quý",
        "Quốc ấn",
        "Đường phù",
        "Long trì",
        "Phượng các",
        "Thiên quan",
        "Thiên phúc",
        "Hồng loan",
        "Thiên hỷ",
        "Thiên giải",
        "Địa giải",
        "Thiên đức",
        "Nguyệt đức",
        "Thiên trù",
        "Phá toái",
        "Đẩu quân",
        "Thiên y",
        "Giải thần",
        "Thiên thương",
        "Thiên sứ",
        "Thiên khốc",
        "Thiên hư",
        "Thai phụ",
        "Phong cáo",
        "Thiên tài",
        "Thiên thọ",
        "Thiên không",


        "L.Kình dương",
        "L.Đà la",
        "L.Hồng loan",
        "L.Thiên khốc",
    ]
    cung = []
    for i in range(13):
        if mang[i] != 99:
            cung.append(tinhdau[mang[i]])

    return cung


def CanHaiBen(cung, cungr, *args):
    k = 0
    if args:
        k = args[0]
    else:
        k = 11
    try:
        cungr.append(cung[k])
    except:
        pass
    try:
        cungr.append(cung[k+1])
    except:
        pass
    if len(cung) > k:
        cung = cung[0:k]
    while len(cung) < 13:
        cung.append('')
    while len(cungr) < 13:
        cungr.append('')
    return [cung, cungr]


def rightC(a, b, c, d, e, f, s):
    return [a[s], b[s], c[s], d[s], e[s], f[s]]


def An12Cung(canNam, chiNam, chiThang, chiGio, thuanNghich, soNgay, soCuc, soChiThang, soChiGio, chiNamLuuNien, canNamLuuNien):

    ansao = []
    a = TaHuuHinhDieuThienDiaGiai(chiThang)
    b = XuongKhucKhongKiepPhuCao(chiGio)
    c = KhoiVietTruHaQuanPhuc(canNam)
    d = HoaLinh(chiNam, thuanNghich, chiGio)
    e = TuHoa(canNam, soNgay, soCuc, chiThang, chiGio)
    g = MaHongHyLongPhuongThienducNguyetducCoQuaToaiKhocHuTaiThoKhong(
        chiNam, soChiGio, soChiThang)
    h = ThaiToaQuangQuyAnPhu(canNam, chiThang, soNgay, chiGio)
    k = DauThuongSu(chiNam, chiThang, chiGio, soChiThang, soChiGio)
    fir = LocKinhDa_So(canNam)
    lKD = LocKinhDa_So(canNamLuuNien)
    lHL = HongLoan_So(chiNamLuuNien)
    lTK = ThienKhoc_So(chiNamLuuNien)

    ansao.append(fir[0])  # Lộc tồn
    ansao.append(fir[1])
    ansao.append(fir[2])
    ansao.append(a[0])  # Tả hữu
    ansao.append(a[1])
    ansao.append(b[0])  # Xương Khúc
    ansao.append(b[1])
    ansao.append(c[0])  # Khôi Việt
    ansao.append(c[1])
    ansao.append(b[2])  # Không Kiếp
    ansao.append(b[3])
    ansao.append(d[0])  # Hỏa Linh
    ansao.append(d[1])
    ansao.append(e[0])  # Tứ hóa
    ansao.append(e[1])
    ansao.append(e[2])
    ansao.append(e[3])
    ansao.append(g[0])  # Mã Hình Diêu
    ansao.append(a[2])
    ansao.append(a[3])
    ansao.append(g[7])  # Cô Qủa
    ansao.append(g[8])
    ansao.append(c[3])  # Lưu hà
    ansao.append(h[0])  # Thai Tọa
    ansao.append(h[1])
    ansao.append(h[2])  # Quang Qúy
    ansao.append(h[3])
    ansao.append(h[4])  # Quốc ấn Đường phù
    ansao.append(h[5])
    ansao.append(g[3])  # Long Phượng
    ansao.append(g[4])
    ansao.append(c[4])  # Quan Phúc
    ansao.append(c[5])
    ansao.append(g[1])  # Hồng Hỷ
    ansao.append(g[2])
    ansao.append(a[4])  # Thiên địa giải
    ansao.append(a[5])
    ansao.append(g[5])  # Thiên nguyệt đức
    ansao.append(g[6])
    ansao.append(c[2])  # Thiên trù
    ansao.append(g[9])  # Phá toái
    ansao.append(k[0])  # Đẩu quân
    ansao.append(ansao[19])  # Thiên y
    ansao.append(ansao[30])  # giải thần
    ansao.append(k[1])  # Thương sứ
    ansao.append(k[2])
    ansao.append(g[10])  # Khốc Hư
    ansao.append(g[11])
    ansao.append(b[4])  # Phụ cáo
    ansao.append(b[5])
    ansao.append(g[12])  # Tài thọ
    ansao.append(g[13])
    ansao.append(g[14])  # Thiên không
    ansao.append(lKD[1])  # Lưu Kình Đà Hồng loan Thiên khốc
    ansao.append(lKD[2])
    ansao.append(lHL)
    ansao.append(lTK)

    cung1 = Cung(BubbleSort(ansao, 1))
    cung2 = Cung(BubbleSort(ansao, 2))
    cung3 = Cung(BubbleSort(ansao, 3))
    cung4 = Cung(BubbleSort(ansao, 4))
    cung5 = Cung(BubbleSort(ansao, 5))
    cung6 = Cung(BubbleSort(ansao, 6))
    cung7 = Cung(BubbleSort(ansao, 7))
    cung8 = Cung(BubbleSort(ansao, 8))
    cung9 = Cung(BubbleSort(ansao, 9))
    cung10 = Cung(BubbleSort(ansao, 10))
    cung11 = Cung(BubbleSort(ansao, 11))
    cung12 = Cung(BubbleSort(ansao, 12))

    thaiTue = VongThaiTue_Ten(chiNam)
    bacSi = VongBacSi_Ten(canNam, thuanNghich)
    tuongTinh = VongTuongTinh_Ten(chiNam)
    luuThaiTue = VongThaiTue_Ten(chiNamLuuNien)
    thuanNghichLuuNien = (1+canGoc.index(canNamLuuNien)) % 2
    luuBacSi = VongBacSi_Ten(canNamLuuNien, thuanNghichLuuNien)
    a = luuBacSi.index("Bác sĩ")
    luuBacSi[a] = 'Lộc tồn'
    luuTuongTinh = VongTuongTinh_Ten(chiNamLuuNien)
    for i in range(len(thaiTue)):
        luuThaiTue[i] = 'L.'+luuThaiTue[i]
        luuBacSi[i] = 'L.'+luuBacSi[i]
        luuTuongTinh[i] = 'L.'+luuTuongTinh[i]
    cung1r = rightC(bacSi, tuongTinh, thaiTue, luuBacSi,
                    luuTuongTinh, luuThaiTue, 0)
    cung2r = rightC(bacSi, tuongTinh, thaiTue, luuBacSi,
                    luuTuongTinh, luuThaiTue, 1)
    cung3r = rightC(bacSi, tuongTinh, thaiTue, luuBacSi,
                    luuTuongTinh, luuThaiTue, 2)
    cung4r = rightC(bacSi, tuongTinh, thaiTue, luuBacSi,
                    luuTuongTinh, luuThaiTue, 3)
    cung5r = rightC(bacSi, tuongTinh, thaiTue, luuBacSi,
                    luuTuongTinh, luuThaiTue, 4)
    cung6r = rightC(bacSi, tuongTinh, thaiTue, luuBacSi,
                    luuTuongTinh, luuThaiTue, 5)
    cung7r = rightC(bacSi, tuongTinh, thaiTue, luuBacSi,
                    luuTuongTinh, luuThaiTue, 6)
    cung8r = rightC(bacSi, tuongTinh, thaiTue, luuBacSi,
                    luuTuongTinh, luuThaiTue, 7)
    cung9r = rightC(bacSi, tuongTinh, thaiTue, luuBacSi,
                    luuTuongTinh, luuThaiTue, 8)
    cung10r = rightC(bacSi, tuongTinh, thaiTue, luuBacSi,
                     luuTuongTinh, luuThaiTue, 9)
    cung11r = rightC(bacSi, tuongTinh, thaiTue, luuBacSi,
                     luuTuongTinh, luuThaiTue, 10)
    cung12r = rightC(bacSi, tuongTinh, thaiTue, luuBacSi,
                     luuTuongTinh, luuThaiTue, 11)
    ar1 = CanHaiBen(cung1, cung1r)
    ar2 = CanHaiBen(cung2, cung2r)
    ar3 = CanHaiBen(cung3, cung3r)
    ar4 = CanHaiBen(cung4, cung4r)
    ar5 = CanHaiBen(cung5, cung5r)
    ar6 = CanHaiBen(cung6, cung6r)
    ar7 = CanHaiBen(cung7, cung7r)
    ar8 = CanHaiBen(cung8, cung8r)
    ar9 = CanHaiBen(cung9, cung9r)
    ar10 = CanHaiBen(cung10, cung10r)
    ar11 = CanHaiBen(cung11, cung11r)
    ar12 = CanHaiBen(cung12, cung12r)

    ketQua = [ar1, ar2, ar3, ar4, ar5, ar6, ar7, ar8, ar9, ar10, ar11, ar12]
    return ketQua
