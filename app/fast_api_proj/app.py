from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Form
from app.fast_api_proj.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from app.fast_api_proj.db import Post, get_async_session, create_db_and_tables, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.fast_api_proj.images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile
from app.fast_api_proj.users import current_active_user, auth_backend, fastapi_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])


@app.post("/upload")
async def upload_file(
    file:UploadFile = File(...),
    caption: str = Form(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):

    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                tags =["backend-upload"]
            )
        )

        if upload_result.response_metadata.http_status_code == 200:
            

                post = Post(
                    user_id = user.id,
                    caption = caption,
                    url = upload_result.url,
                    file_type = "video" if file.content_type.startswith("video/") else "image",
                    file_name = upload_result.name
                )
                session.add(post)
                await session.commit()
                await session.refresh(post)
                return post
    except Exception as e:
         raise HTTPException(status_code=500, detail = str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {u.id: u.email for u in users}

    posts_data =[]
    for posts in posts:
        posts_data.append(
            {
                "id": str(posts.id),
                "user_id": str(posts.user_id),
                "caption": posts.caption,
                "url": posts.url,
                "file_type": posts.file_type,
                "file_name": posts.file_name,
                "created_at": posts.created_at.isoformat(),
                "is_owner": posts.user_id == user.id,
                "email": user_dict.get(posts.user_id, "Unknown")
            }
        )
    return {"posts": posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session),
                      user: User = Depends(current_active_user)):
     try:
          post_uuid = uuid.UUID(post_id)
          result = await session.execute(select(Post).where(Post.id == post_uuid))
          post = result.scalars().first()

          if not post:
               raise HTTPException(status_code = 404, detail = "Post not found")

          if post.user_id != user.id:
               raise HTTPException(status_code = 403, detail = "You are not authorized to delete this post")

          await session.delete(post)
          await session.commit()

          return{"success": True, "message": "Post deleted successfully"}

     except Exception as e:
          raise HTTPException(status_code = 500, detail = str(e))
     
