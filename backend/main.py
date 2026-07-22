from fastapi import FastAPI, Body, Response, status, HTTPException, Depends

from uuid import UUID
import time
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.database import Base, engine, get_db
from backend.model import PostModel, UserModel, LikedModel
from backend.schema import PostCreate, PostResponse, PostHomeResponse, PostPatch
from backend.schema import CreateUser, UserResponse, LoginRequest, UserPosts, PostLikes
from backend.utils import hash_password
from backend.utils import verify_password
from backend.oauth import create_acess_token, get_current_user


app = FastAPI()
Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://blog-f1vp.onrender.com",
                "https://immoran-blog-sulb.onrender.com"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model= list[PostHomeResponse])
async def home_page(db: Session = Depends(get_db),
              limit:  int= 10,
              offset: int = 0):
    limit = min(limit, 50)
    post_query = select(PostModel).offset(offset).limit(limit)
    posts = db.scalars(post_query).all()
    return posts

@app.get("/posts", response_model=list[PostResponse])
async def get_posts(db: Session = Depends(get_db),
                limit: int = 10,
                offset: int = 0):
    
    posts = db.query(PostModel).filter(PostModel.published==True).offset(offset).limit(limit).all()
    return posts

@app.get("/posts/{id}", response_model=PostResponse)
async def get_single_post(id: UUID, db: Session = Depends(get_db)):
    post_query= db.query(PostModel).filter(PostModel.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"Post with id:'{id}' not found"
        )
    return post

@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post:PostCreate, 
                db: Session = Depends(get_db),
                current_user: UserModel= Depends(get_current_user)):
    new_post = PostModel(**post.model_dump(), user_id= current_user.id) 
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return (new_post)

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post( id: UUID, 
                db: Session = Depends(get_db),
                current_user: UserModel = Depends(get_current_user)):
    post_query = db.query(PostModel).filter(PostModel.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"post with id: '{id}' not found"
            
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= "Unauthorized Action")    
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return(Response(status_code=status.HTTP_204_NO_CONTENT))

@app.patch("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_post(id:UUID, 
                post_update:PostPatch, 
                db:Session = Depends(get_db),
                current_user: UserModel= Depends(get_current_user)):
    post_query = db.query(PostModel).filter(PostModel.id == id)
    post = post_query.first()
    
    if post is None:
        raise HTTPException (
            status_code = status.HTTP_404_NOT_FOUND,
            detail= f"Post with id {id} not found"
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= "Unauthorized Action"
        )

    post_query.update(post_update.model_dump(exclude_unset = True), synchronize_session = "fetch")
    db.commit()
    return post_query.first()

@app.post("/post/{id}/like")
async def like_post(id:UUID, 
              db:Session = Depends(get_db),
              current_user: UserModel= Depends(get_current_user)):
    
    post_query = db.query(PostModel).filter(PostModel.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException (
            status_code = status.HTTP_404_NOT_FOUND,
            detail= f"Post with id {id} not found"
        )

    already_liked = db.query(LikedModel).filter(
        LikedModel.post_id == id,
        LikedModel.user_id == current_user.id
    ).first()
        
    if already_liked:
        db.delete(already_liked)
        db.commit()
        return {"detail": "Post Sucessfully unliked"}
    
    new_like = LikedModel(post_id = id, user_id= current_user.id)
    db.add(new_like)
    db.commit()
    return {"detail": "Post liked sucessfully"}

# ----- User Path-----#

@app.post("/new_user", status_code=status.HTTP_201_CREATED, response_model= UserResponse)
async def create_user(post:CreateUser, db: Session = Depends(get_db)):
    user_data = post.model_dump()
    user_data["password"] = hash_password(user_data["password"])
    new_user = UserModel(**user_data)
    # post.password = hash_password(post.password)
    # new_user = UserModel(**post.model_dump()) 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return (new_user)

@app.post("/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(
        (UserModel.email == credentials.identifier ) |(UserModel.username==credentials.identifier)).first()
    
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    token = create_acess_token(data={"sub": str(user.id)})
        
    return {"access_token": token, "token_type": "bearer"}

@app.get("/user/posts/{id}", response_model=UserPosts)
async def get_user_posts_history(id: UUID, 
                            db: Session= Depends(get_db),
                            current_user: UserModel= Depends(get_current_user)):
    
    user_query = db.query(UserModel).filter(UserModel.id == id)
    user = user_query.first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not found"
        )
        
    if id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= "Unathorized Action"
        )
        
    return user

@app.get("/user/me", response_model=UserResponse)
async def get_user_profile(current_user: UserModel= Depends(get_current_user)):
    
    return current_user
    

