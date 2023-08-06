from fastapi import APIRouter
from mb_std import md
from mb_std.mongo import make_query

from mb_base1.app import BaseApp


def init(app: BaseApp) -> APIRouter:
    router = APIRouter()

    @router.get("")
    def get_dlogs(category: str | None = None, limit: int = 100):
        q = make_query(category=category)
        return app.dlog_collection.find(q, "-created_at", limit=limit)

    @router.delete("")
    def delete_all_dlogs():
        return app.dlog_collection.delete_many({})

    @router.get("/{pk}")
    def get_dlog(pk):
        return app.dlog_collection.get(pk)

    @router.delete("/{pk}")
    def delete_dlog(pk):
        return app.dlog_collection.delete_by_id(pk)

    @router.delete("/category/{category}")
    def delete_by_category(category: str):
        return app.dlog_collection.delete_many(md(category))

    return router
