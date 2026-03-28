from fastapi import FastAPI,HTTPException
from schemas import PostCreate

app = FastAPI()

text_posts = {1:{"id":1,"title":"New Post", "Content":"Cool Test Post"}}

@app.get("/posts")
def get_all_posts():
    return "Hello World"

@app.get("/posts/{id}")
def get_post(id:int):
    return text_posts.get(id)


@app.post("/posts")
def create_post(post:PostCreate):
    new_id = max(text_posts.keys()) + 1 if text_posts else 1
    new_post = {
        "id":new_id,
        "title": post.title,
        "content":post.content
    }
    
    text_posts.append(new_post)
    return new_post