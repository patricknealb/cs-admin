from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Optional

from app.database import get_db
from app.models import Message, MessageCategory

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


# ─── Message Categories ───────────────────────────────────────────────────────

@app.get("/categories", response_class=HTMLResponse)
async def list_categories(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MessageCategory).order_by(MessageCategory.message_category))
    categories = result.scalars().all()
    return templates.TemplateResponse("categories.html", {
        "request": request,
        "categories": categories
    })


@app.post("/categories/add")
async def add_category(
    message_category: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    category = MessageCategory(message_category=message_category)
    db.add(category)
    await db.commit()
    return RedirectResponse(url="/categories", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/categories/edit/{message_category_id}")
async def edit_category(
    message_category_id: int,
    message_category: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MessageCategory).where(MessageCategory.message_category_id == message_category_id)
    )
    category = result.scalar_one_or_none()
    if category:
        category.message_category = message_category
        category.row_updated_at = datetime.now(timezone.utc)
        await db.commit()
    return RedirectResponse(url="/categories", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/categories/delete/{message_category_id}")
async def delete_category(
    message_category_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MessageCategory).where(MessageCategory.message_category_id == message_category_id)
    )
    category = result.scalar_one_or_none()
    if category:
        await db.delete(category)
        await db.commit()
    return RedirectResponse(url="/categories", status_code=status.HTTP_303_SEE_OTHER)


# ─── Messages ─────────────────────────────────────────────────────────────────

@app.get("/messages", response_class=HTMLResponse)
async def list_messages(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message).order_by(Message.message_id))
    messages = result.scalars().all()
    categories_result = await db.execute(select(MessageCategory).order_by(MessageCategory.message_category))
    categories = categories_result.scalars().all()
    return templates.TemplateResponse("messages.html", {
        "request": request,
        "messages": messages,
        "categories": categories
    })


@app.post("/messages/add")
async def add_message(
    message_id: str = Form(...),
    message_text: str = Form(...),
    message_category_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    message = Message(
        message_id=message_id,
        message_text=message_text,
        message_category_id=message_category_id
    )
    db.add(message)
    await db.commit()
    return RedirectResponse(url="/messages", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/messages/edit/{row_id}")
async def edit_message(
    row_id: int,
    message_text: str = Form(...),
    message_category_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Message).where(Message.row_id == row_id)
    )
    message = result.scalar_one_or_none()
    if message:
        message.message_text = message_text
        message.message_category_id = message_category_id
        message.row_updated_at = datetime.now(timezone.utc)
        await db.commit()
    return RedirectResponse(url="/messages", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/messages/delete/{row_id}")
async def delete_message(
    row_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Message).where(Message.row_id == row_id)
    )
    message = result.scalar_one_or_none()
    if message:
        await db.delete(message)
        await db.commit()
    return RedirectResponse(url="/messages", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/")
async def root():
    return RedirectResponse(url="/messages")