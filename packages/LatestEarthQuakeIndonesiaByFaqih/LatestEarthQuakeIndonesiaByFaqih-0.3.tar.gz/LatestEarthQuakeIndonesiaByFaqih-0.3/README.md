# Latest EarthQuake BMKG
This package will get latest earthquake from BMKG | Meteorological, Climatological, and Geophysical Agency
## HOW IT WORK?
This package will scrape from [BMKG](https://bmkg.go.id) to get latest earthquake happened in indonesia

this package will use BeautifulSoup4 and Request, to produce output in the form of JSON that is ready to be used in web or mobile applications

## HOW TO USE

    import gempa_terkini

    if __name__ == '__main__':
    print('Aplikasi Utama')
    result = gempa_terkini.ekstraksi_data()
    gempa_terkini.tampilkan_data(result)
## AUTHOR
Faqih Fakhruddin

