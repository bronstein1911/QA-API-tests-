# Product Placement Integration Test

## What does this script do?
This script verifies whether the product placement system in stores is working correctly. It creates a test placement and checks if it's properly displayed in the system.

## How it works?
1. The script authenticates in the admin panel (retrieves token and cookies)
2. Checks how many products are already placed in stores (parsing via Beautiful Soup)
3. Creates a new placement of a random product in a random store
4. Verifies the placement appears in the system via API
5. Checks if the placement is displayed in the admin panel
6. Compares the product count before and after placement

## Test Coverage
- Admin panel authentication functionality
- Placement creation via API
- Correct display of placements in admin panel
- Matching counts between created placements and system records

## Test Data
The script includes sample stores and products:
- 4 stores
- 6 different products

## How to run?
```bash
python test_placement_new.py
```

# Интеграционный тест выкладки товаров

## Что делает этот скрипт?
Этот скрипт проверяет, правильно ли работает система выкладки товаров в магазинах. Он создает тестовую выкладку и проверяет, что она корректно отображается в системе.

## Как работает?
1. Скрипт авторизуется в админке (забирает токен и куки) 
2. Смотрит, сколько товаров уже выложено в магазинах (парсинг через beautiful soup) 
3. Создает новую выкладку случайного товара в случайном магазине
4. Проверяет, что выкладка появилась в системе через API
5. Проверяет, что выкладка отображается в админке
6. Сравнивает количество товаров до и после выкладки

## Что проверяется?
- Работает ли авторизация в админке
- Работает ли создание выкладки через API
- Правильно ли отображается выкладка в админке
- Совпадает ли количество выложенных товаров с тем, что мы создали

## Тестовые данные
В скрипте есть список тестовых магазинов и товаров:
- 4 магазина
- 6 разных товаров

## Как запустить?
```bash
python test_placement_new.py
```
