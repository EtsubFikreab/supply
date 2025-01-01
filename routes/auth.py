from fastapi import APIRouter, Form, HTTPException
from db import supabase

router = r = APIRouter()


@r.post("/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    try:
        auth_response = supabase.auth.sign_up({
            'email': email,
            'password': password
        })
        if auth_response.user is None:
            raise HTTPException(status_code=400, detail="Signup failed")
        return {"message": "Signup successful. Please check your email to verify your account."}
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
        return access_token
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@r.post("/logout")
async def logout(access_token: str = Form(...)):
    try:
        response = supabase.auth.sign_out(access_token)
        if response.get("error"):
            raise HTTPException(status_code=400, detail=response.get("error"))
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@r.post("/gmail")
async def gmail():
    try:
        response = supabase.auth.sign_in_with_oauth({
            "provider": 'google'
        })
        if response.user is None:
            raise HTTPException(status_code=400, detail="Login failed")
        access_token = response.session.access_token
        return access_token
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
