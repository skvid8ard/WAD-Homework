import httpx
import urllib.parse
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.oauth import OAuthUserData

class GoogleOAuthProvider:
    # URL для обмена кода на токен
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    # URL для получения данных пользователя
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    @classmethod
    async def get_user_data(cls, code: str) -> OAuthUserData:

        decoded_code = urllib.parse.unquote(code) # Декодирование URL-кодированного кода авторизации

        async with httpx.AsyncClient(timeout=15.0) as client:

            # Обмен временного кода на access token
            token_response = await client.post(
                cls.TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": decoded_code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI
                },
                headers={"Accept": "application/json"}
            )

            if token_response.status_code != 200:
                print(f"GOOGLE TOKEN ERROR: {token_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange authorization code for token with Google / Не удалось обменять код авторизации на токен у Google"
                )

            access_token = token_response.json().get("access_token")

            # Получение данных пользователя с помощью access token
            user_response = await client.get(
                cls.USER_INFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch user info from Google / Не удалось получить информацию о пользователе от Google"
                )

            user_info = user_response.json()

            # Формирование данных для создания или поиска пользователя в системе
            return OAuthUserData(
                provider="google",
                account_id=user_info["sub"],
                email=user_info["email"]
            )

class GitHubOAuthProvider:
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_INFO_URL = "https://api.github.com/user"
    EMAILS_URL = "https://api.github.com/user/emails"

    @classmethod
    async def get_user_data(cls, code: str) -> OAuthUserData:
        decoded_code = urllib.parse.unquote(code)
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_response = await client.post(
                cls.TOKEN_URL,
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": decoded_code,
                    "redirect_uri": settings.GITHUB_REDIRECT_URI
                },
                headers={"Accept": "application/json"}
            )
        
            if token_response.status_code != 200 or "error" in token_response.json():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange authorization code for token with GitHub / Не удалось обменять код авторизации на токен у GitHub"
                )

            access_token = token_response.json().get("access_token")

            user_response = await client.get(
                cls.USER_INFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch user info from GitHub / Не удалось получить информацию о пользователе от GitHub"
                )

            user_info = user_response.json()
            account_id = str(user_info["id"])

            email_response = await client.get(
                cls.EMAILS_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if email_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch user emails from GitHub / Не удалось получить электронные адреса пользователя от GitHub"
                )

            emails = email_response.json()
            # Поиск основной и подтвержденной почты
            primary_email = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)

            if not primary_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No verified primary email found for GitHub user / Не найден подтвержденный основной электронный адрес для пользователя GitHub"
                )

            return OAuthUserData(
                provider="github",
                account_id=account_id,
                email=primary_email
            )