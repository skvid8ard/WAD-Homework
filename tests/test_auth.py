import pytest
from httpx import AsyncClient
from unittest.mock import patch
from app.schemas.oauth import OAuthUserData

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Тест успешной регистрации (теперь с email)"""
    response = await client.post(
        "/auth/register",
        json={
            "username": "testtester", 
            "email": "test@test.com", 
            "password": "StrongPassword123!"
        }
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testtester"
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_login_unverified_blocked(client: AsyncClient):
    """Тест: неподтвержденный пользователь не может войти"""
    user_data = {
        "username": "unverified", 
        "email": "unverified@test.com", 
        "password": "StrongPassword123!"
    }
    await client.post("/auth/register", json=user_data)
    
    # Пытаемся войти. ВАЖНО: используем data=, а не json= (т.к. это Form Data)
    login_res = await client.post(
        "/auth/login", 
        data={"username": "unverified", "password": "StrongPassword123!"}
    )
    
    assert login_res.status_code == 403
    assert "Email не подтвержден" in login_res.json()["detail"]

@pytest.mark.asyncio
async def test_oauth_login_new_user(client: AsyncClient):
    """Тест: Вход через Google для нового пользователя (Авто-регистрация)"""
    
    # 1. Готовим фейковые данные, которые якобы вернул Google
    mock_data = OAuthUserData(
        provider="google",
        account_id="google_12345",
        email="new_oauth_user@test.com"
    )
    
    # 2. Подменяем метод get_user_data
    with patch("app.services.oauth_providers.GoogleOAuthProvider.get_user_data", return_value=mock_data):
        response = await client.post(
            "/auth/oauth/google/login",
            json={"code": "fake_auth_code_123"}
        )
        
    # 3. Проверяем, что логин успешен и токены выданы
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.cookies


@pytest.mark.asyncio
async def test_oauth_implicit_linking(client: AsyncClient):
    """Тест: Связывание аккаунтов (Implicit Linking) для существующего пользователя"""
    
    # 1. Регистрируем пользователя классическим способом
    user_email = "linker@test.com"
    await client.post(
        "/auth/register",
        json={
            "username": "linker_guy", 
            "email": user_email, 
            "password": "StrongPassword123!"
        }
    )
    
    # 2. Готовим данные от GitHub с ТОЙ ЖЕ почтой
    mock_data = OAuthUserData(
        provider="github",
        account_id="github_999",
        email=user_email
    )
    
    # 3. Имитируем логин через GitHub
    with patch("app.services.oauth_providers.GitHubOAuthProvider.get_user_data", return_value=mock_data):
        response = await client.post(
            "/auth/oauth/github/login",
            json={"code": "fake_github_code"}
        )
        
    # 4. Проверяем успешный вход (ошибки "email уже существует" быть не должно!)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_oauth_unsupported_provider(client: AsyncClient):
    """Тест: Блокировка неизвестного провайдера"""
    
    response = await client.post(
        "/auth/oauth/yandex/login", # Передаем yandex, которого у нас нет
        json={"code": "some_code"}
    )
    
    assert response.status_code == 400
    assert "Unsupported OAuth provider" in response.json()["detail"]

@pytest.mark.asyncio
async def test_verify_and_universal_login(client: AsyncClient):
    """Комплексный тест: Регистрация -> Верификация -> Логин по нику и почте"""
    user_data = {
        "username": "loginguy", 
        "email": "loginguy@test.com", 
        "password": "ComplexPass123!"
    }
    
    # Подменяем функцию генерации кода, чтобы она точно вернула "123456"
    with patch("app.services.email_service.generate_verification_code", return_value="123456"):
        await client.post("/auth/register", json=user_data)
    
    # 1. Верифицируем почту
    verify_res = await client.post(
        "/auth/verify-email", 
        json={"email": "loginguy@test.com", "verification_code": "123456"}
    )
    assert verify_res.status_code == 200

    # 2. Универсальный логин: по username
    login_username_res = await client.post(
        "/auth/login", 
        data={"username": "loginguy", "password": "ComplexPass123!"}
    )
    assert login_username_res.status_code == 200
    assert "access_token" in login_username_res.json()

    # 3. Универсальный логин: по email
    login_email_res = await client.post(
        "/auth/login", 
        data={"username": "loginguy@test.com", "password": "ComplexPass123!"}
    )
    assert login_email_res.status_code == 200
    assert "refresh_token" in login_email_res.cookies # Проверяем защищенную куку

@pytest.mark.asyncio
async def test_resend_code(client: AsyncClient):
    """Тест повторной отправки кода"""
    user_data = {
        "username": "resendguy", 
        "email": "resend@test.com", 
        "password": "ComplexPass123!"
    }
    await client.post("/auth/register", json=user_data)

    resend_res = await client.post("/auth/resend-code", json={"email": "resend@test.com"})
    assert resend_res.status_code == 200

@pytest.mark.parametrize("password, expected_msg",[
    ("short", "не менее 8 символов"),
    ("alllowercase1!", "хотя бы одну заглавную букву"),
    ("ALLUPPERCASE1!", "хотя бы одну строчную букву"),
    ("NoDigitsHere!", "хотя бы одну цифру"),
    ("NoSpecialChar123", "хотя бы один спецсимвол"), 
])
@pytest.mark.asyncio
async def test_register_password_complexity(client: AsyncClient, password: str, expected_msg: str):
    """Тест Pydantic-валидаторов пароля (параметризованный)"""
    response = await client.post(
        "/auth/register",
        json={
            "username": f"user_{password}", 
            "email": f"test_{password}@test.com", 
            "password": password
        }
    )
    
    assert response.status_code == 422
    assert expected_msg in response.json()["detail"][0]["msg"]