from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, UploadFile, Form,File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import get_db, engine, Base
from models import Post
from schemas import PostCreate,PostResponse
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_app:FastAPI):
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    
    await engine.dispose()

app= FastAPI(lifespan=lifespan)



@app.post("/uploads")
async def upload_file(file:UploadFile=File(...),caption:str=Form(""),
                      db:AsyncSession=Depends(get_db)):
    post=Post(
        caption=caption,
        url="dummy Url"
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@app.get("/feed",response_model=PostResponse)
async def get_feed(db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(Post).order_by(Post.created_at.desc()))
    posts=result.scalars().all()
    
    return posts
        
       
    

# GET all posts
@app.get("/posts")
async def get_all_posts(db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(Post))
    posts = result.scalars().all()
    return posts


# GET a single post
@app.get("/posts/{post_id}")
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


# CREATE a new post
@app.post("/posts")
async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db)):
    new_post = Post(
        caption=post.content,
        url=post.title  # or any mapping you prefer
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post





