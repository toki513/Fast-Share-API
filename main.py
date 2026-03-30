from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, UploadFile, Form,File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import get_db, engine, Base
from models import Post
from schemas import PostCreate,PostResponse,UploadFileResult
from contextlib import asynccontextmanager
from images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile




@asynccontextmanager
async def lifespan(_app:FastAPI):
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    
    await engine.dispose()

app= FastAPI(lifespan=lifespan)


@app.post("/uploads")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)

        with open(temp_file_path, "rb") as f:
            upload_result = imagekit.upload_file(
                file=f,
                file_name=file.filename
            )

      
        if upload_result.response_metadata.http_status_code == 200:
            post = Post(
                caption=caption,
                url=upload_result.url,
                file_type="video" if file.content_type.startswith("video/") else "image",
                file_name=upload_result.name
            )

            db.add(post)
            await db.commit()
            await db.refresh(post)

            return post

        else:
            raise HTTPException(status_code=400, detail="Upload failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
      
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        await file.close() 
    
    
    
    
   

@app.get("/feed",response_model=list[PostResponse])
async def get_feed(db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(Post).order_by(Post.created_at.asc()))
    posts=result.scalars().all()
    
    return [PostResponse.from_orm(post) for post in posts] 
        
       
@app.delete("/posts/{post_id}")
async def delete_post(post_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    result=await db.execute(select(Post).where(Post.id == post_id))
    post=result.scalars().first()
    
    if not post:
       

    await db.delete(post)
    await db.commit()
    return {"success":True}
    
    
    
    
    


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





