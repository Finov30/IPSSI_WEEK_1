file_path = r"C:\IPSSI_19_11_2025\StockUniteLegale_utf8.csv"

with open(file_path, encoding='utf-8') as f:
    header = f.readline().strip()
    columns = header.split(',')
    print("Header columns:")
    for col in columns:
        print(col)
