from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Query, Request, status, Form
from app.dependencies import SessionDep
from . import router, templates
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from app.utilities.security import access_token_cookie_kwargs


@router.get("/login", response_class=HTMLResponse)
async def login_view(request: Request, role: str = Query(default="student")):
    login_role = "landlord" if role.lower() == "landlord" else "student"
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"login_role": login_role},
    )


@router.post("/login", response_class=HTMLResponse)
async def login_action_ajax(
    db: SessionDep,
    request: Request,
    username: str = Form(),
    password: str = Form(),
    role: str = Form(default="student"),
):
    login_role = "landlord" if role.lower() == "landlord" else "student"
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    access_token = auth_service.authenticate_user(username, password)
    if not access_token:
        flash(request, "Incorrect username or password", "danger")
        return RedirectResponse(
            url=request.url_for("login_view").include_query_params(role=login_role),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    user = user_repo.get_by_username(username)
    username_role = username.strip().lower()
    user_role = user.role.lower() if user and user.role else ""
    account_is_landlord = user_role in {"admin", "landlord"} or username_role in {"admin", "landlord"}
    if login_role == "landlord" and not account_is_landlord:
        flash(request, "Use a landlord account to sign in here.", "danger")
        return RedirectResponse(
            url=request.url_for("login_view").include_query_params(role="landlord"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    if login_role == "student" and account_is_landlord:
        flash(request, "Use a student account to sign in here.", "danger")
        return RedirectResponse(
            url=request.url_for("login_view").include_query_params(role="student"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    if account_is_landlord:
        dest = "landlord_requests_view"
    else:
        dest = "user_home_view"
    response = RedirectResponse(
        url=request.url_for(dest),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        **access_token_cookie_kwargs(),
    )
    return response
