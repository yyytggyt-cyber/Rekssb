import os
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from build_article import build_article

BLOG_ID = "8822017970635882646"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

# الاختبار الأول: فيلم واحد فقط
# بعد نجاح الاختبار غيّر القيمة إلى 100
LIMIT = 99

BASE = "https://api.themoviedb.org/3"
LOG_FILE = Path("data/published_new_blog.json")


def tmdb_get(path, params=None):
    params = dict(params or {})
    params["api_key"] = API_KEY

    url = BASE + path + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "CineView/1.1"}
    )

    with urllib.request.urlopen(request, timeout=40) as response:
        return json.loads(response.read().decode("utf-8"))


def load_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text(encoding="utf-8"))

    return {"movies": [], "post_ids": []}


def save_log(data):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def get_existing_posts(service):
    existing = set()
    token = None

    print("فحص منشورات المدونة لمنع التكرار...")

    while True:
        result = service.posts().list(
            blogId=BLOG_ID,
            maxResults=500,
            fetchBodies=False,
            status=["LIVE", "DRAFT", "SCHEDULED"],
            pageToken=token
        ).execute()

        for post in result.get("items", []):
            for label in post.get("labels", []):
                if label.startswith("tmdb-"):
                    existing.add(label[5:])

        token = result.get("nextPageToken")
        if not token:
            break

    return existing


def get_movies():
    movies = []
    seen = set()

    print("جلب الأفلام ذات الأوصاف العربية من TMDb...")

    for page in range(1, 51):
        result = tmdb_get(
            "/discover/movie",
            {
                "language": "ar",
                "sort_by": "popularity.desc",
                "include_adult": "false",
                "include_video": "false",
                "page": page
            }
        )

        for movie in result.get("results", []):
            movie_id = str(movie.get("id", ""))
            title = (movie.get("title") or "").strip()
            overview = (movie.get("overview") or "").strip()

            if not movie_id or movie_id in seen:
                continue

            if not title or not overview:
                continue

            movie["media_type"] = "movie"
            movie["translations"] = []

            movies.append(movie)
            seen.add(movie_id)

        if page >= result.get("total_pages", 0):
            break

        if len(movies) >= 150:
            break

    print("عدد الأفلام العربية المتاحة:", len(movies))
    return movies


def main():
    global API_KEY

    API_KEY = (
        os.environ.get("TMDB_API_KEY")
        or input("أدخل TMDb API Key: ").strip()
    )

    if not API_KEY:
        print("لم يتم إدخال مفتاح TMDb.")
        return

    if not Path("token.json").exists():
        print("ملف token.json غير موجود.")
        return

    creds = Credentials.from_authorized_user_file(
        "token.json", SCOPES
    )

    service = build("blogger", "v3", credentials=creds)

    log = load_log()

    # السجل المحلي
    local_ids = set(str(x) for x in log.get("movies", []))

    # السجل الفعلي للمدونة، بما فيه المسودات
    remote_ids = get_existing_posts(service)

    movies = get_movies()

    published = 0
    skipped = 0

    for movie in movies:
        if published >= LIMIT:
            break

        movie_id = str(movie["id"])

        if movie_id in local_ids or movie_id in remote_ids:
            print("تخطي فيلم موجود:", movie.get("title"))
            skipped += 1
            continue

        try:
            title, content, language_count = build_article(movie)

            post = {
                "kind": "blogger#post",
                "title": title,
                "content": content,
                "labels": [
                    "movie",
                    f"tmdb-{movie_id}"
                ]
            }

            # نشر مباشر للعامة، وليس مسودة
            result = service.posts().insert(
                blogId=BLOG_ID,
                body=post,
                isDraft=False
            ).execute()

            log.setdefault("movies", []).append(movie_id)
            log.setdefault("post_ids", []).append(
                str(result.get("id"))
            )
            save_log(log)

            local_ids.add(movie_id)
            remote_ids.add(movie_id)

            published += 1

            print("\nتم النشر المباشر بنجاح!")
            print("الفيلم:", movie.get("title"))
            print("العنوان:", result.get("title"))
            print("معرّف الفيلم:", movie_id)
            print("معرّف المقال:", result.get("id"))
            print("اللغات:", language_count)
            print("الرابط:", result.get("url"))

            time.sleep(1)

        except Exception as error:
            print("توقف النشر بسبب خطأ:", error)
            print("الأفلام المنشورة محفوظة في سجل النشر.")
            break

    print("\n===== ملخص العملية =====")
    print("المقالات المنشورة الآن:", published)
    print("الأفلام المتخطاة:", skipped)
    print("إجمالي الأفلام المسجلة:", len(log.get("movies", [])))
    print("ملف السجل:", LOG_FILE)


if __name__ == "__main__":
    main()
