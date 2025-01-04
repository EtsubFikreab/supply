from fastapi import APIRouter, Form, HTTPException, Depends

from auth import get_current_user
from db import supabase

auth_router = r = APIRouter()


@r.post("/signup")
async def signup(display_name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        auth_response = supabase.auth.sign_up({
            'email': email,
            'password': password,
            'data': {'display_name': display_name}
        })
        if auth_response.user is None:
            raise HTTPException(status_code=400, detail="Signup failed")
        return auth_response.session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@r.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    try:
        auth_response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        if auth_response.user is None:
            raise HTTPException(status_code=400, detail="Login failed")
        access_token = auth_response.session.access_token
        return auth_response.session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@r.post("/logout")
async def logout(access_token: str = Form(...)):
    try:
        response = supabase.auth.sign_out()
        if response.get("error"):
            raise HTTPException(status_code=400, detail=response.get("error"))
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@r.post("/oauth")
async def oauth_token(email: str = Form(...), password: str = Form(...)):
    try:
        auth_response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        if auth_response.user is None:
            raise HTTPException(status_code=400, detail="Login failed")
        access_token = auth_response.session.access_token
        return auth_response
    except Exception as e:
        if (str(e) == "Invalid login credentials"):
            try:
                auth_response = supabase.auth.sign_up({
                    'email': email,
                    'password': password
                })
                if auth_response.user is None:
                    raise HTTPException(
                        status_code=400, detail="Signup failed")
                return auth_response
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@r.get("/current_user")
async def current_user(current_user: dict = Depends(get_current_user)):
    return current_user


@r.post("/refresh")
async def refresh_session(refresh_token: str = Form(...)):
    return supabase.auth.refresh_session(refresh_token)
