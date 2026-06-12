from fastapi import FastAPI, Body, Response, status, HTTPException, Depends
from uuid import UUID
import time
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.model import PostModel, UserModel
from backend.schema import PostCreate, PostResponse, PostHomeResponse, PostPatch, CreateUser, UserResponse, LoginRequest, UserPosts
from backend.utils import hash_password
from backend.utils import verify_password
from backend.oauth import create_acess_token, get_current_user


app = FastAPI()
Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/posts", response_model=list[PostResponse])
def get_posts(db: Session = Depends(get_db),
              limit: int = 10,
              offset: int = 0):
    
    posts = db.query(PostModel).filter(PostModel.published==True).offset(offset).limit(limit).all()
    return posts

@app.get("/posts/{id}")
def get_single_post(id: UUID, db: Session = Depends(get_db)):
    post_query= db.query(PostModel).filter(PostModel.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"Post with id:'{id}' not found"
        )
    return post

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post:PostCreate, 
                db: Session = Depends(get_db),
                current_user: UserModel= Depends(get_current_user)):
    new_post = PostModel(**post.model_dump(), user_id= current_user.id) 
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return (new_post)

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post( id: UUID, 
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
def update_post(id:UUID, 
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

# ----- User Path-----#

@app.post("/new_user", status_code=status.HTTP_201_CREATED, response_model= UserResponse)
def create_user(post:CreateUser, db: Session = Depends(get_db)):
    post.password = hash_password(post.password)
    new_user = UserModel(**post.model_dump()) 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return (new_user)

@app.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(
        (UserModel.email == credentials.identifier ) |
                                      (UserModel.username==credentials.identifier)
                                      ).first()
    
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )
    
    token = create_acess_token(data={"sub": str(user.id)})
        
    return {"access_token": token, "token_type": "bearer"}

@app.get("/user/posts/{id}", response_model=UserPosts)
def get_user_posts_history(id: UUID, 
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

@app.get("/user/{id}", response_model=UserResponse)
def get_user_history(id: UUID, 
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
    

