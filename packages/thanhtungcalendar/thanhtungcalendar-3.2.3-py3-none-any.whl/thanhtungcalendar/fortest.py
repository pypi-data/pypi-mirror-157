import TsptCalendar as m


print(m.NgayAmLich(1987, 10, 25, 0, 30, 7))
print(m.CanThangTietKhi(m.TichThangTietKhi(
    1987, m.TietKhiHienTai(1987, 10, 25, 7))))
print(m.CanThangAmLich(m.TichThangAmLich(1987, 10, 25, 2, 30, 7)))
