import requests
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import random
import time

BASE_URL = " " 
ADMIN_URL = " "

# Тестовые данные
STORES = {
    31895: "Кировоградская, 13А",
    31896: "Хабарова, 2",
    31897: "Озёрная, 50",
    31898: "Сочи, Новая Заря, 7"
}

PRODUCTS = {
    462778: "Торт У Палыча Дубайский шоколад",
    462754: "Торт Малина-фисташка Мистер Торт",
    462623: "Торт Миндальный",
    462616: "Торт Красный бархат",
    462773: "Филе голени индейки охлажденное Индилайт ГВУ",
    462769: "Порижное Тропиканка Виктория"
}

# Авторизация
def get_auth_cookies():
    login_url = f"{BASE_URL}/api/v1/external/login"
    login_data = {
        "login": "login",
        "password": "password"
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:138.0) Gecko/20100101 Firefox/138.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Origin': BASE_URL,
        'Connection': 'keep-alive'
    }
    response = requests.post(login_url, json=login_data, headers=headers)
    print(f"\nОтвет авторизации: {response.text}")
    if response.status_code != 200:
        raise Exception(f"Ошибка авторизации: {response.status_code}")
    return response.cookies

def get_admin_cookies():
    session = requests.Session()
    login_page = session.get(f"{ADMIN_URL}/login")
    soup = BeautifulSoup(login_page.text, "html.parser")
    csrf = soup.find('input', {'name': '_csrf_token'})
    if not csrf:
        raise Exception('CSRF token not found on admin login page')
    csrf_token = csrf['value']
    login_data = {
        '_username': '+71234456423',
        '_password': 'password',
        '_csrf_token': csrf_token,
        '_phone': ''
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:138.0) Gecko/20100101 Firefox/138.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': ADMIN_URL,
        'Referer': f'{ADMIN_URL}/login',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    resp = session.post(f"{ADMIN_URL}/login_check", data=login_data, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'Admin login failed: {resp.status_code}')
    if 'login' in resp.url:
        raise Exception('Still on login page after admin login')
    return session.cookies

def get_initial_report():
    today = datetime.now().strftime("%d.%m.%Y")
    admin_url = f"{ADMIN_URL}/admin/reptns?date={today}"
    print(f"\nПолучаем начальный отчёт за {today}: {admin_url}")
    
    admin_resp = requests.get(
        admin_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        },
        cookies=get_admin_cookies()
    )
    
    if admin_resp.status_code != 200:
        raise Exception(f"Ошибка получения отчёта: {admin_resp.status_code}")
        
    # Парсим начальное количество
    soup = BeautifulSoup(admin_resp.text, "html.parser")
    initial_quantities = {}
    
    for row in soup.select('table.table tbody tr'):
        cells = row.select('td')
        if len(cells) >= 6:
            store_address = cells[0].text.strip()
            placements = cells[3].text.strip()
            initial_quantities[store_address] = int(placements)
            
    return initial_quantities

def create_placement():
    # Случайный выбор магазина и товара
    store_id = random.choice(list(STORES.keys()))
    product_id = random.choice(list(PRODUCTS.keys()))
    quantity = random.randint(1, 100)
    today = datetime.now().strftime("%Y-%m-%d")
    next_year = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    
    placement_data = [{
        "store_id": store_id,
        "quantity": quantity,
        "executor_phone": "87312393919",
        "expiration_dates": [next_year],
        "product_id": product_id,
        "created_at": today
    }]
    
    print(f"\nСоздаем выкладку:")
    print(f"Магазин: {STORES[store_id]} (ID: {store_id})")
    print(f"Товар: {PRODUCTS[product_id]} (ID: {product_id})")
    print(f"Количество: {quantity}")
    
    create_response = requests.post(
        f"{BASE_URL}/api/v1/external/add-product-placement",
        json=placement_data
    )
    print(f"\nОтвет на создание: {create_response.text}")
    if create_response.status_code != 200:
        raise Exception(f"Ошибка создания выкладки: {create_response.status_code}")
    if not create_response.json()["success"]:
        raise Exception("Ошибка создания выкладки: success=False")
        
    return store_id, quantity

def verify_placement(store_id, expected_quantity, initial_quantities):
    # Проверка через API
    check_data = {
        "store_id": store_id,
        "executor_phone": "89612199742",
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    print(f"\nПроверяем через API:")
    print(f"Магазин: {STORES[store_id]} (ID: {store_id})")
    
    check_response = requests.post(
        f"{BASE_URL}/api/v1/external/get-product-placements",
        json=check_data
    )
    print(f"\nОтвет API: {check_response.text}")
    
    if check_response.status_code != 200:
        raise Exception(f"Ошибка проверки через API: {check_response.status_code}")
        
    placements = check_response.json()["data"]
    if not placements:
        raise Exception("Выкладка не найдена в API")
        
    # Проверка через админку
    print("\nЖдем 5 секунд для обновления админки...")
    time.sleep(5)
    
    today = datetime.now().strftime("%d.%m.%Y")
    admin_url = f"{ADMIN_URL}/admin/reptns?date={today}"
    print(f"\nПроверяем в админке за {today}: {admin_url}")
    
    admin_resp = requests.get(
        admin_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        },
        cookies=get_admin_cookies()
    )
    
    if admin_resp.status_code != 200:
        raise Exception(f"Ошибка получения отчёта: {admin_resp.status_code}")
        
    soup = BeautifulSoup(admin_resp.text, "html.parser")
    admin_quantity = 0
    
    for row in soup.select('table.table tbody tr'):
        cells = row.select('td')
        if len(cells) >= 6:
            store_address = cells[0].text.strip()
            placements = cells[3].text.strip()
            if store_address == STORES[store_id]:
                admin_quantity = int(placements)
                print(f"\nКоличество в админке: {admin_quantity}")
                break
    
    # Считаем разницу
    initial_quantity = initial_quantities.get(STORES[store_id], 0)
    quantity_diff = admin_quantity - initial_quantity
    
    print(f"Начальное количество: {initial_quantity}")
    print(f"Конечное количество: {admin_quantity}")
    print(f"Разница: {quantity_diff}")
    
    if quantity_diff != expected_quantity:
        raise Exception(f"Разница в количестве ({quantity_diff}) не совпадает с ожидаемым ({expected_quantity})")
        
    print("\nТест успешно пройден!")

def main():
    try:
        # Получаем начальный отчёт
        initial_quantities = get_initial_report()
        
        # Создаем выкладку
        store_id, quantity = create_placement()
        
        # Проверяем
        verify_placement(store_id, quantity, initial_quantities)
        
    except Exception as e:
        print(f"\nОшибка: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
