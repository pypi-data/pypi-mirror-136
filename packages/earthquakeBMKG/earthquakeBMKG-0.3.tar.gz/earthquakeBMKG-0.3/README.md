# LATEST INDONESIA EARTHQUAKE
This package will get the latest earthquake from BMKG | Meteorological, Climatological, and Geophysical Agency.

## HOW IT WORK?
This package will scrape from [BMKG](https://www.bmkg.go.id/) to get latest quake happend in indonesia.

this package will use BeautifulSoup4 and Requests, to produce output in the form of JSON that is ready to be used in WEB or Mobile Applications

## HOW TO USE?
```
if __name__ == '__main__':
    result = gempaterkini.ekstrasi_data()
    gempaterkini.tampilkan_data (result) 
```

## AUTHOR
Asep Sopiyan