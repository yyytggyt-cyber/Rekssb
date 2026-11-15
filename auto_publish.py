import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from build_article import build_article

BLOG_ID = "8822017970635882646"
SCOPES = ["https://www.googleapis.com/auth/blogger"]
DATABASE_PATH = "data/published_new_blog.json"

def get_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

def load_database():
    if not os.path.exists(DATABASE_PATH):
        return {"movies": [], "series": [], "episodes": []}
    with open(DATABASE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for key in ("movies", "series", "episodes"):
        data.setdefault(key, [])
    return data

def save_database(data):
    os.makedirs("data", exist_ok=True)
    temp = DATABASE_PATH + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp, DATABASE_PATH)

def publish_movie(service, movie):
    database = load_database()
    movie_id = str(movie["id"])
    if movie_id in database["movies"]:
        print("هذا الفيلم مسجل كمنشور سابقاً؛ تم تخطيه.")
        return

    title, content, language_count = build_article(movie)
    post = {"kind": "blogger#post", "title": title, "content": content}
    result = service.posts().insert(
        blogId=BLOG_ID, body=post, isDraft=True
    ).execute()

    database["movies"].append(movie_id)
    save_database(database)
    print("تم النشر بنجاح:", result.get("title"))
    print("رابط المقال:", result.get("url"))
    print("عدد اللغات المضمنة:", language_count)

def main():
    with open("data/movie.json", "r", encoding="utf-8") as f:
        movie = json.load(f)
    service = get_service()
    publish_movie(service, movie)

if __name__ == "__main__":
    main()
