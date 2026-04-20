import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Тест успешной регистрации"""
    response = await client.post(
        "/auth/register",
        json={"username": "testtester", "password": "StrongPassword123!"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testtester"
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_register_invalid_password(client: AsyncClient):
    """Тест валидации пароля (нет цифр/спецсимволов)"""
    response = await client.post(
        "/auth/register",
        json={"username": "weakuser", "password": "onlyletters"}
    )
    assert response.status_code == 422
    # Проверяем, что ошибка содержит наше русское сообщение
    assert "Пароль должен содержать" in response.json()["detail"][0]["msg"]

@pytest.mark.asyncio
async def test_login_and_refresh(client: AsyncClient):
    """Комплексный тест: Login -> Access Token -> Refresh"""
    # 1. Сначала регистрируемся
    user_data = {"username": "loginuser", "password": "ComplexPass123!"}
    await client.post("/auth/register", json=user_data)
    
    # 2. Логинимся
    login_res = await client.post("/auth/login", json=user_data)
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()
    
    # Проверяем, что кука установилась
    assert "refresh_token" in login_res.cookies
    
    # 3. Пробуем рефреш (кука передастся автоматически)
    refresh_res = await client.post("/auth/refresh")
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()

@pytest.mark.parametrize("password, expected_msg", [
    ("short", "не менее 8 символов"),
    ("alllowercase1!", "хотя бы одну заглавную букву"),
    ("ALLUPPERCASE1!", "хотя бы одну строчную букву"),
    ("NoDigitsHere!", "хотя бы одну цифру"),
    # Исправляем здесь на "спецсимвол"
    ("NoSpecialChar123", "хотя бы один спецсимвол"), 
])
@pytest.mark.asyncio
async def test_register_password_complexity(client: AsyncClient, password: str, expected_msg: str):
    """
    Параметризованный тест для проверки всех правил сложности пароля.
    """
    response = await client.post(
        "/auth/register",
        json={"username": f"user_{password}", "password": password}
    )
    
    # Мы ожидаем 422 Unprocessable Entity (ошибка валидации Pydantic)
    assert response.status_code == 422
    
    # Проверяем, что в ответе именно та ошибка, которую мы ожидали
    error_detail = response.json()["detail"][0]
    assert expected_msg in error_detail["msg"]