import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from build_article import build_article

BLOG_ID = "8822017970635882646"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def publish_draft():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("blogger", "v3", credentials=creds)

    with open("data/movie.json", "r", encoding="utf-8") as f:
        movie = json.load(f)

    title, html_content, language_count = build_article(movie)

    tmdb_id = movie.get("id")
    media_type = movie.get("media_type", "movie")

    labels = [media_type, f"tmdb-{tmdb_id}"]

    post = {
        "kind": "blogger#post",
        "title": title,
        "content": html_content,
        "labels": labels
    }

    result = service.posts().insert(
        blogId=BLOG_ID,
        body=post,
        isDraft=True
    ).execute()

    print("تم إنشاء المسودة بنجاح!")
    print("العنوان:", result.get("title"))
    print("التصنيفات:", result.get("labels"))
    print("معرّف المقال:", result.get("id"))

if __name__ == "__main__":
    publish_draft()
