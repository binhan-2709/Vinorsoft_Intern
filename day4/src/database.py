"""
database.py — Giả lập database bằng dict trong bộ nhớ.
Ngày 3 sẽ thay thế bằng SQLAlchemy + PostgreSQL thật sự.
"""
from datetime import datetime
from src.models import PostCreate, PostUpdate, PostResponse, PostSummary


_posts: dict[int, dict] = {}
_counter: int = 0


def _next_id() -> int:
    global _counter
    _counter += 1
    return _counter


def db_create_post(data: PostCreate, author: str) -> PostResponse:
    now = datetime.now()
    record = {
        "id": _next_id(),
        **data.model_dump(),
        "author": author,
        "created_at": now,
        "updated_at": now,
        "views": 0,
    }
    _posts[record["id"]] = record
    return PostResponse(**record)


def db_get_post(post_id: int) -> PostResponse | None:
    if post_id not in _posts:
        return None
    _posts[post_id]["views"] += 1
    return PostResponse(**_posts[post_id])


def db_list_posts(
    *,
    published_only: bool,
    category: str | None,
    search: str | None,
    page: int,
    page_size: int,
) -> tuple[int, list[PostSummary]]:
    results = list(_posts.values())

    if published_only:
        results = [p for p in results if p["published"]]
    if category:
        results = [p for p in results if p["category"] == category]
    if search:
        q = search.lower()
        results = [
            p for p in results
            if q in p["title"].lower() or q in p["content"].lower()
        ]

    total = len(results)
    start = (page - 1) * page_size
    summaries = [
        PostSummary(**{k: p[k] for k in PostSummary.model_fields})
        for p in results[start : start + page_size]
    ]
    return total, summaries


def db_update_post(post_id: int, data: PostUpdate) -> PostResponse | None:
    if post_id not in _posts:
        return None
    _posts[post_id].update(data.model_dump(exclude_none=True))
    _posts[post_id]["updated_at"] = datetime.now()
    return PostResponse(**_posts[post_id])


def db_delete_post(post_id: int) -> bool:
    if post_id not in _posts:
        return False
    del _posts[post_id]
    return True