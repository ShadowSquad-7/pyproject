#биток
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Настройка драйвера
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    driver.get("https://www.binance.com/ru/markets")

    while True:  # Бесконечный цикл для парсинга динамических данных
        try:
            # Каждый раз ищем элемент заново
            price_element1 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[data-area="right"].layout-ellipsis.t-Body2.w-\\[148px\\].items-center')
                )
            )
            print(f"Текущая цена: {price_element1.text}")

        except Exception as e:
            print(f"Ошибка при получении элемента: {str(e)}")

        time.sleep(3)  # Пауза между обновлениями

except KeyboardInterrupt:
    print("Парсинг остановлен пользователем")
finally:
    driver.quit()
