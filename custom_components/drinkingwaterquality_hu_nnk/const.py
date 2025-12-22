DOMAIN = "drinkingwaterquality_hu_nnk"
PLATFORMS = ["binary_sensor"]

BASE_URL = (
    "https://www.nnk.gov.hu/index.php/"
    "kornyezetegugy/kornyezetegeszsegugyi-laboratoriumi-osztaly/"
    "vizhigienes-laboratorium/ivoviz/magyarorszagi-telepulesek-ivovizminosege.html"
)
URL_TEMPLATE = BASE_URL + "?view=placemark&id={placemark_id}"

# Csak a 4 hivatalos kifejezés – pontos egyezés (normalizálva) alapján
OK_PHRASES_EXACT = {
    "biztonságosan fogyasztható ivóvíz",
    "biztonságosan fogyasztható ivóvíz, amelyben egészségre nem ártalmas bakteriológiai vagy kémiai eltérés tapasztalható",
}

PROBLEM_PHRASES_EXACT = {
    "biztonságosan fogyasztható ivóvíz, amelyben eseti bakteriológiai vagy kémiai eltérés tapasztalható",
    "nem iható víz, kémiai szempontból nem elfogadható",
}
