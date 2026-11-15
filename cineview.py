import json
import os
import urllib.parse
import urllib.request

API_KEY = os.environ.get("TMDB_API_KEY") or input("أدخل TMDb API Key: ").strip()
MOVIE_ID = int(os.environ.get("TMDB_MOVIE_ID", "687163"))
BASE = "https://api.themoviedb.org/3"

def tmdb_get(path, params=None):
    params = dict(params or {})
    params["api_key"] = API_KEY
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "CineView/1.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def main():
    try:
        movie = tmdb_get(f"/movie/{MOVIE_ID}", {"language": "ar"})
        translations = tmdb_get(f"/movie/{MOVIE_ID}/translations").get("translations", [])
        localized, seen = [], set()
        for item in translations:
            lang = item.get("iso_639_1", "")
            country = item.get("iso_3166_1", "")
            data = item.get("data") or {}
            title = (data.get("title") or "").strip()
            key = (lang, country, title.casefold())
            if lang and title and key not in seen:
                localized.append({"language": lang, "country": country, "title": title,
                                  "overview": (data.get("overview") or "").strip()})
                seen.add(key)
        movie["translations"] = localized
        movie["media_type"] = "movie"
        os.makedirs("data", exist_ok=True)
        with open("data/movie.json", "w", encoding="utf-8") as f:
            json.dump(movie, f, ensure_ascii=False, indent=2)
        print("نجح الاتصال بـ TMDb!")
        print("العنوان العربي:", movie.get("title"))
        print("عدد عناوين TMDb المترجمة:", len(localized))
        print("تم حفظ البيانات والترجمات في data/movie.json")
    except Exception as error:
        print("حدث خطأ أثناء جلب بيانات TMDb:", error)

if __name__ == "__main__":
    main()
