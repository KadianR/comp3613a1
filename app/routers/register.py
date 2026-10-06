from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Query, Request, status, Form, HTTPException
from app.dependencies import SessionDep
from app.schemas.auth import SignupRequest
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from . import router, templates

# View route (loads the page)
@router.get("/register", response_class=HTMLResponse)
async def register_view(request: Request, role: str = Query(default="student")):
    account_role = "landlord" if role.lower() == "landlord" else "student"
    return templates.TemplateResponse(
        request=request, 
        name="register.html",
        context={"account_role": account_role},
    )

# Action route (performs an action)
@router.post('/register', response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
def signup_user(request:Request, db:SessionDep, 
    username: str = Form(),
    email: str = Form(),
    password: str = Form(),
    role: str = Form(default="student"),
):
    account_role = "landlord" if role.lower() == "landlord" else "student"
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    try:
        auth_service.register_user(username, email, password, account_role)
        flash(request, "Registration completed! Sign in now!")
        return RedirectResponse(
            url=request.url_for("login_view").include_query_params(role=account_role),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except Exception as e:
        flash(request, "Username or email already exists", "danger")
        return RedirectResponse(url=request.url_for("register_view"), status_code=status.HTTP_303_SEE_OTHER)
