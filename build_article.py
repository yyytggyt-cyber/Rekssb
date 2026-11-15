import json
import html
import os

LANG_NAMES = {
    "ar": "العربية",
    "en": "English",
    "fr": "Français",
    "es": "Español",
    "de": "Deutsch",
    "pt": "Português",
    "tr": "Türkçe",
    "it": "Italiano",
    "ru": "Русский",
    "ja": "日本語",
    "ko": "한국어",
    "zh": "中文",
    "hi": "हिन्दी",
    "id": "Bahasa Indonesia",
    "nl": "Nederlands",
    "pl": "Polski",
    "uk": "Українська",
    "fa": "فارسی",
    "ur": "اردو",
    "vi": "Tiếng Việt",
    "fi": "Suomi",
    "ka": "ქართული",
    "bg": "Български",
    "cs": "Čeština",
    "sl": "Slovenščina",
    "lv": "Latviešu",
    "az": "Azərbaycan dili",
    "et": "Eesti",
    "th": "ภาษาไทย",
    "ro": "Română",
    "el": "Ελληνικά",
    "ca": "Català",
    "sr": "Српски",
    "lt": "Lietuvių",
    "be": "Беларуская",
    "hr": "Hrvatski",
    "da": "Dansk",
    "no": "Norsk",
    "sv": "Svenska",
    "he": "עברית",
    "ms": "Bahasa Melayu",
    "bn": "বাংলা",
    "ta": "தமிழ்",
    "fa": "فارسی",
    "mk": "Македонски",
}

TITLE_SUFFIX = {
    "ar": "في نافذة السينما بجودة عالية",
    "en": "at CineView in High Quality",
    "fr": "sur CineView en haute qualité",
    "es": "en CineView en alta calidad",
    "de": "bei CineView in hoher Qualität",
    "pt": "no CineView em alta qualidade",
    "tr": "CineView'de yüksek kalitede",
    "it": "su CineView in alta qualità",
    "ru": "на CineView в высоком качестве",
    "ja": "CineViewで高画質",
    "ko": "CineView 고화질",
    "zh": "CineView 高清版",
    "hi": "CineView पर उच्च गुणवत्ता में",
    "id": "di CineView dengan kualitas tinggi",
    "nl": "op CineView in hoge kwaliteit",
    "pl": "w CineView w wysokiej jakości",
    "uk": "на CineView у високій якості",
    "fa": "در CineView با کیفیت بالا",
    "ur": "CineView پر اعلیٰ معیار میں",
}

def esc(value):
    return html.escape(str(value or ""), quote=True)

def make_title(name, lang):
    suffix = TITLE_SUFFIX.get(lang)
    if not suffix:
        return name

    if lang == "ar":
        return f"مشاهدة {name} {suffix}"

    if lang == "en":
        return f"Watch {name} {suffix}"

    return f"{name} — {suffix}"

def build_article(movie):
    main_title = (
        movie.get("title")
        or movie.get("original_title")
        or "عمل سينمائي"
    )

    release = movie.get("release_date", "")
    rating = movie.get("vote_average", "غير متوفر")
    overview = movie.get("overview", "")
    poster = movie.get("poster_path")

    image = (
        "https://image.tmdb.org/t/p/w780" + poster
        if poster else ""
    )

    # الاحتفاظ بلغة واحدة وعنوان واحد لكل رمز لغة
    variants = [{
        "language": "ar",
        "title": main_title
    }]

    seen_languages = {"ar"}

    translations = movie.get("translations", [])

    if isinstance(translations, list):
        for item in translations:
            if not isinstance(item, dict):
                continue

            lang = str(item.get("language") or "").strip().lower()
            name = str(item.get("title") or "").strip()

            if not lang or not name:
                continue

            # لا نضيف اللغة نفسها مرتين
            if lang in seen_languages:
                continue

            variants.append({
                "language": lang,
                "title": name
            })

            seen_languages.add(lang)

    post_title = make_title(main_title, "ar")

    rows = []

    for item in variants:
        lang = item["language"]
        name = item["title"]

        label = LANG_NAMES.get(lang, f"لغة أخرى ({lang})")

        direction = (
            "rtl" if lang in ("ar", "fa", "ur", "he")
            else "ltr"
        )

        rows.append(
            f'<li lang="{esc(lang)}" dir="{direction}">'
            f'<strong>{esc(label)}:</strong> '
            f'{esc(make_title(name, lang))}</li>'
        )

    image_html = ""

    if image:
        image_html = (
            f'<img src="{esc(image)}" '
            f'alt="{esc(main_title)}" '
            'loading="lazy" '
            'style="max-width:100%;height:auto;">'
        )

    content = f'''<article class="cineview-article" lang="ar" dir="rtl">
  <h1>{esc(post_title)}</h1>
  {image_html}
  <p><strong>تاريخ الإصدار:</strong> {esc(release)}</p>
  <p><strong>التقييم:</strong> {esc(rating)}</p>
  <h2>قصة العمل</h2>
  <p>{esc(overview)}</p>
  <section class="cineview-title-translations">
    <h2>عنوان العمل بلغات متعددة</h2>
    <ul>{''.join(rows)}</ul>
  </section>
  <p><small>بيانات العمل والترجمات: TMDb</small></p>
</article>'''

    return post_title, content, len(variants)

def main():
    with open("data/movie.json", encoding="utf-8") as f:
        movie = json.load(f)

    title, content, language_count = build_article(movie)

    os.makedirs("data", exist_ok=True)

    with open("data/article.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("تم إنشاء مقال واحد بنجاح.")
    print("عنوان Blogger الأساسي:", title)
    print("عدد اللغات الفعلية دون تكرار:", language_count)
    print("الملف: data/article.html")

if __name__ == "__main__":
    main()
