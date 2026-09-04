"""Async test suite for Phase 2: Auth and Profiles."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from app.main import app


async def run_tests():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        test_email = "alex.mercer@example.com"
        test_password = "SecurePassword123!"

        # 1. Register a new user
        register_payload = {
            "email": test_email,
            "password": test_password,
            "name": "Alex Mercer",
            "bio": "Full-stack Python and React developer",
            "skills": ["FastAPI", "PostgreSQL", "React"],
            "website": "https://alexmercer.dev",
            "social_links": {"github": "https://github.com/alexmercer", "linkedin": "https://linkedin.com/in/alexmercer"},
            "availability": "available",
        }
        res_reg = await client.post("/api/v1/auth/register", json=register_payload)
        if res_reg.status_code == 400:
            print("[INFO] User already registered, continuing with login.")
        else:
            assert res_reg.status_code == 201, res_reg.text
            user_data = res_reg.json()
            assert user_data["email"] == test_email
            assert user_data["name"] == "Alex Mercer"
            assert user_data["rating"] == 0.0  # Read-only default rating
            assert "FastAPI" in user_data["skills"]
            print("[PASS] User Registration")

        # 2. Duplicate registration check
        res_dup = await client.post("/api/v1/auth/register", json=register_payload)
        assert res_dup.status_code == 400
        print("[PASS] Duplicate Registration Blocked (400)")

        # 3. Login
        login_payload = {
            "email": test_email,
            "password": test_password,
        }
        res_login = await client.post("/api/v1/auth/login", json=login_payload)
        assert res_login.status_code == 200, res_login.text
        tokens = res_login.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        print("[PASS] User Login")

        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # 4. Refresh Token
        res_refresh = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert res_refresh.status_code == 200, res_refresh.text
        new_tokens = res_refresh.json()
        assert "access_token" in new_tokens
        new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
        print("[PASS] Token Refresh")

        # 5. Get Current User Profile (GET /me)
        res_me = await client.get("/api/v1/users/me", headers=new_headers)
        assert res_me.status_code == 200, res_me.text
        profile = res_me.json()
        assert profile["email"] == test_email
        assert profile["rating"] == 0.0
        user_id = profile["id"]
        print("[PASS] GET /api/v1/users/me")

        # 6. Update Profile (PUT /me)
        update_payload = {
            "name": "Alex Mercer, Senior Engineer",
            "bio": "Lead backend developer with async FastAPI expertise",
            "skills": ["FastAPI", "PostgreSQL", "React", "Docker", "AsyncIO"],
            "availability": "busy",
        }
        res_update = await client.put("/api/v1/users/me", json=update_payload, headers=new_headers)
        assert res_update.status_code == 200, res_update.text
        updated_profile = res_update.json()
        assert updated_profile["name"] == "Alex Mercer, Senior Engineer"
        assert "Docker" in updated_profile["skills"]
        assert updated_profile["availability"] == "busy"
        assert updated_profile["rating"] == 0.0  # Confirm rating remained untouched
        print("[PASS] PUT /api/v1/users/me (Rating read-only verified)")

        # 7. Fetch by ID (GET /{user_id})
        res_user_id = await client.get(f"/api/v1/users/{user_id}", headers=new_headers)
        assert res_user_id.status_code == 200, res_user_id.text
        assert res_user_id.json()["id"] == user_id
        print(f"[PASS] GET /api/v1/users/{user_id}")

        # 8. List Users (GET /)
        res_list = await client.get("/api/v1/users/", headers=new_headers)
        assert res_list.status_code == 200, res_list.text
        assert len(res_list.json()) >= 1
        print("[PASS] GET /api/v1/users/")

        # 9. Password Reset Flow
        res_forgot = await client.post("/api/v1/auth/forgot-password", json={"email": test_email})
        assert res_forgot.status_code == 200, res_forgot.text
        msg = res_forgot.json()["message"]
        reset_token = msg.split(": ")[-1]
        print("[PASS] Forgot Password Token Generation")

        # Reset password
        new_password = "NewSuperPassword2026!"
        res_reset = await client.post("/api/v1/auth/reset-password", json={
            "token": reset_token,
            "new_password": new_password,
        })
        assert res_reset.status_code == 200, res_reset.text
        print("[PASS] Reset Password")

        # Login with new password
        res_login_new = await client.post("/api/v1/auth/login", json={
            "email": test_email,
            "password": new_password,
        })
        assert res_login_new.status_code == 200, res_login_new.text
        print("[PASS] Login With New Password")

        # 10. Unauthorized access check
        res_unauth = await client.get("/api/v1/users/me")
        assert res_unauth.status_code == 401
        print("[PASS] Unauthorized Access Blocked (401)")

        print("\n==============================================")
        print(" ALL PHASE 2 AUTH & PROFILES TESTS PASSED! ")
        print("==============================================")


if __name__ == "__main__":
    asyncio.run(run_tests())
