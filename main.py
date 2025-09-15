# main.py


from __future__ import annotations
from typing import Optional, List
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from models import User, Todo, Priority

app = FastAPI(title="SimpleMicroservices - HW1 Demo")

# In-memory stores
USERS: dict[UUID, User] = {}
TODOS: dict[UUID, Todo] = {}

# ----------- Schemas for partial updates ----------- #
class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    completed: Optional[bool] = None
    priority: Optional[Priority] = None

# ----------- Users ----------- #
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User):
    if any(u.email == user.email for u in USERS.values()):
        raise HTTPException(status_code=400, detail="Email already exists")
    USERS[user.id] = user
    return user

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: UUID):
    u = USERS.get(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u

@app.get("/users", response_model=List[User])
def list_users(limit: int = 50, offset: int = 0):
    items = list(USERS.values())
    return items[offset: offset + limit]

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID):
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found")
    # cascade: delete user's todos
    for tid in [tid for tid, t in TODOS.items() if t.owner_id == user_id]:
        del TODOS[tid]
    del USERS[user_id]
    return

# ----------- Todos ----------- #
@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: Todo):
    if todo.owner_id not in USERS:
        raise HTTPException(status_code=400, detail="owner_id not found")
    # ensure server can assign ID if client passes empty/placeholder
    if not getattr(todo, "id", None):
        object.__setattr__(todo, "id", uuid4())  # pydantic v2 models are frozen by default only if configured; safe here
    TODOS[todo.id] = todo
    return todo

@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: UUID):
    t = TODOS.get(todo_id)
    if not t:
        raise HTTPException(status_code=404, detail="Todo not found")
    return t

@app.get("/todos", response_model=List[Todo])
def list_todos(limit: int = 50, offset: int = 0, owner_id: Optional[UUID] = None):
    items = list(TODOS.values())
    if owner_id:
        items = [t for t in items if t.owner_id == owner_id]
    return items[offset: offset + limit]

@app.get("/users/{user_id}/todos", response_model=List[Todo])
def list_user_todos(user_id: UUID, limit: int = 50, offset: int = 0):
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found")
    items = [t for t in TODOS.values() if t.owner_id == user_id]
    return items[offset: offset + limit]

@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: UUID, patch: TodoUpdate):
    t = TODOS.get(todo_id)
    if not t:
        raise HTTPException(status_code=404, detail="Todo not found")
    data = patch.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(t, k, v)
    TODOS[todo_id] = t
    return t

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: UUID):
    if todo_id not in TODOS:
        raise HTTPException(status_code=404, detail="Todo not found")
    del TODOS[todo_id]
    return
