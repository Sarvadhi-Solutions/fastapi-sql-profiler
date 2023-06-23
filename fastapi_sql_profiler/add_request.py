import math
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .database import session
from .models import QueryInfo, RequestInfo

router = APIRouter()


BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))


@router.get("/all_request", response_class=HTMLResponse)
async def all_request(request: Request,  page: int = 1, limit: int = 15):
    """Get all request."""
    all_request_info = session.query(
        RequestInfo).order_by(-RequestInfo.id).all()
    total_request_info = len(all_request_info)
    total_pages = math.ceil(total_request_info / limit)

    start_index = (page - 1) * limit
    end_index = start_index + limit
    request_info = all_request_info[start_index:end_index]
    return templates.TemplateResponse("request_show.html", {"request": request, "request_info": request_info, "current_api": "all_request",
                                                            "page": page,
                                                            "limit": limit,
                                                            "total_pages": total_pages,
                                                            })


@router.get("/request_detail/{id}", response_class=HTMLResponse)
def request_show(id: int, request: Request):
    """Get single request."""
    request_query = session.query(RequestInfo).get(id)
    query_detail = session.query(QueryInfo).filter_by(request_id=id)
    sum_on_query = 0
    for query_details in query_detail:
        sum_on_query = sum_on_query + query_details.time_taken
    templates.env.globals['current_id'] = id
    return templates.TemplateResponse("request.html", {"request": request, "request_query": request_query, "sum_on_query": sum_on_query})


@router.get("/request_query/{id}", response_class=HTMLResponse)
def request_query(id: int, request: Request):
    """Get single request."""
    request_query = session.query(RequestInfo).get(id)
    query_detail = session.query(QueryInfo).filter_by(request_id=id)
    sum_on_query = 0
    for query_details in query_detail:
        sum_on_query = sum_on_query + query_details.time_taken
    templates.env.globals['current_id'] = id
    return templates.TemplateResponse("sql_query.html", {"request": request, "request_query": request_query, "query_detail": query_detail, "sum_on_query": sum_on_query})


@router.get("/request_query_details/{id}", response_class=HTMLResponse)
def request_query_details(id: int, request: Request):
    """Get single request."""
    query_detail = session.query(QueryInfo).get(id)
    return templates.TemplateResponse("sql_query_detail.html", {"request": request, "query_detail": query_detail, "current_api": "request_query_details"})
