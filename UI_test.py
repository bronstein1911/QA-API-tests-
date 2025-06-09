from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.options.android import UiAutomator2Options
import unittest
import random
from datetime import datetime, timedelta
import time
import json
import logging
from selenium.common.exceptions import WebDriverException

#  логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class TestNavigation(unittest.TestCase):
    def setUp(self):
        options = UiAutomator2Options()
        options.platform_name = 'Android'
        options.device_name = 'Android Device'
        options.app_package = 'ru.proviante'
        options.app_activity = 'ru.proviante.MainActivity'
        options.no_reset = True
        
        self.driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
        self.wait = WebDriverWait(self.driver, 20)  # Увеличиваем таймаут 20 сек
        
        # Загружаем JSON с продуктами
        with open('тестовые данные/products.json', 'r', encoding='utf-8') as f:
            self.products = json.load(f)['products']

    def safe_click(self, element, max_attempts=3):
        """Безопасный клик с повторными попытками"""
        for attempt in range(max_attempts):
            try:
                element.click()
                return True
            except WebDriverException as e:
                if attempt == max_attempts - 1:
                    raise
                logger.warning(f"Попытка {attempt + 1} не удалась, пробуем снова...")
                time.sleep(2)

    def enter_product_data(self, barcode):
        logger.info(f"Начинаем ввод продукта с штрих-кодом: {barcode}")
        
        # Вводим штрих-код
        barcode_input = self.wait.until(EC.element_to_be_clickable(
            (AppiumBy.ID, "ru.proviante:id/et_barcode")
        ))
        barcode_input.send_keys(barcode)
        logger.info("Штрих-код введен")
        
        # Ждем загрузки данных с бэка
        time.sleep(3)

        # Нажимаем "Сколько выставлено"
        quantity_button = self.wait.until(EC.element_to_be_clickable(
            (AppiumBy.XPATH, "//android.widget.TextView[@text='Сколько выставлено']")
        ))
        self.safe_click(quantity_button)

        # Вводим случайное количество
        quantity_input = self.wait.until(EC.element_to_be_clickable(
            (AppiumBy.ID, "ru.proviante:id/edit_text_discount_input")
        ))
        random_quantity = str(random.randint(1, 100))
        quantity_input.send_keys(random_quantity)
        logger.info(f"Введено количество: {random_quantity}")

        # Нажимаем "Применить"
        apply_button = self.wait.until(EC.element_to_be_clickable(
            (AppiumBy.XPATH, "//android.widget.Button[@text='ПРИМЕНИТЬ']")
        ))
        self.safe_click(apply_button)

        # Нажимаем "Добавить срок годности"
        expiration_button = self.wait.until(EC.element_to_be_clickable(
            (AppiumBy.XPATH, "//android.widget.TextView[@text='Добавить срок годности']")
        ))
        self.safe_click(expiration_button)

        # Генерируем случайную дату в формате ддммгггг
        future_date = datetime.now() + timedelta(days=random.randint(1, 365))
        date_str = future_date.strftime("%d%m%Y")

        # Вводим дату
        expiration_input = self.wait.until(EC.element_to_be_clickable(
            (AppiumBy.ID, "ru.proviante:id/et_expiration")
        ))
        expiration_input.send_keys(date_str)
        logger.info(f"Введен срок годности: {date_str}")

        # Нажимаем "Сохранить"
        save_button = self.wait.until(EC.element_to_be_clickable(
            (AppiumBy.ID, "ru.proviante:id/btn_save")
        ))
        self.safe_click(save_button)

        # Нажимаем "ОТПРАВИТЬ"
        send_button = self.wait.until(EC.element_to_be_clickable(
            (AppiumBy.ID, "ru.proviante:id/btn_send_data")
        ))
        self.safe_click(send_button)
        logger.info("Отправляем данные...")
        
        # Ждем после отправки
        time.sleep(4)
        logger.info("✅ Данные отправлены")

    def test_navigate_to_placement(self):
        logger.info("Начинаем тест выкладки")
        
        # Открываем меню
        menu_button = self.wait.until(EC.element_to_be_clickable(
            (AppiumBy.XPATH, "//android.widget.ImageButton[@content-desc='Open navigation drawer']")
        ))
        self.safe_click(menu_button)
        logger.info("Меню открыто")

        # Кликаем по пункту "Выкладка" в меню
        placement_item = self.wait.until(EC.element_to_be_clickable(
            (AppiumBy.XPATH, "//android.widget.TextView[@text='Выкладка']")
        ))
        self.safe_click(placement_item)
        logger.info("Перешли в раздел выкладки")

        # Проверяем, что мы на экране выкладки
        placement_title = self.wait.until(EC.presence_of_element_located(
            (AppiumBy.XPATH, "//android.widget.TextView[@text='Выкладка']")
        ))
        self.assertTrue(placement_title.is_displayed())

        # Первый продукт
        self.enter_product_data("4601887034582")
        
        # Повторяем действия с рандомными продуктами
        for i in range(10):
            logger.info(f"Начинаем ввод продукта {i+1} из 10")
            random_product = random.choice(self.products)
            self.enter_product_data(random_product['barcode'])

    def tearDown(self):
        logger.info("Завершаем тест")
        self.driver.quit()

if __name__ == '__main__':
    unittest.main() 
