DOMAIN = "drinkingwaterquality_hu_nnk"
PLATFORMS = ["binary_sensor"]

BASE_URL = "https://www.nnk.gov.hu/index.php/kornyezetegugy/kornyezetegeszsegugyi-laboratoriumi-osztaly/vizhigienes-laboratorium/ivoviz/magyarorszagi-telepulesek-ivovizminosege.html"
URL_TEMPLATE = BASE_URL + "?view=placemark&id={placemark_id}"

OK_PHRASES = [
    "Megfelelő minőségű ivóvíz",
    "Megfelelő, indikátor paraméterek miatt tűrhető minőségű ivóvíz",
]
