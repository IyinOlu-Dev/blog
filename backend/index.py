from fastapi import FastAPI, Body, Response, status, HTTPException, Depends
from uuid import UUID
from sqlalchemy import func
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session


from backend.database import Base, engine, get_db
from backend.model import PostModel
from backend.schema import PostCreate, PostResponse, PostHomeResponse, PostPatch

app = FastAPI()
Base.metadata.create_all(bind=engine)

while True:
    try :
        conn = psycopg2.connect(host="localhost", database="learning", 
                                user = "postgres", password = "postgres",
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Database connection failed")
        print("Error: ", error)
        time.sleep(2)

@app.get("/", response_model=list[PostHomeResponse])
def home_page(db: Session = Depends(get_db), limit: int = 10, offset: int = 5):
    screen = db.query(
        PostModel.id,
        PostModel.title,
        func.substring(PostModel.content, 1, 10).label("snippet"),
        PostModel.created_at).limit(limit).all()
    return(screen)

@app.get("/posts", response_model=list[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(PostModel).all()
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
def create_post(post:PostCreate, db: Session = Depends(get_db)):
    new_post = PostModel(**post.model_dump()) 
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return (new_post)

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post( id: UUID, db: Session = Depends(get_db),):
    post_query = db.query(PostModel).filter(PostModel.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"post with id: '{id}' not found"
            
        )
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return(Response(status_code=status.HTTP_204_NO_CONTENT))

@app.patch("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_post(id:UUID, post_update:PostPatch, db:Session = Depends(get_db)):
    post_query = db.query(PostModel).filter(PostModel.id == id)
    post = post_query.first()
    
    if post is None:
        raise HTTPException (
            status_code = status.HTTP_404_NOT_FOUND,
            detail= f"Post with id {id} not found"
        )
    
    post_query.update(post_update.model_dump(exclude_unset = True), synchronize_session = "fetch")
    db.commit()
    return post_query.first()
