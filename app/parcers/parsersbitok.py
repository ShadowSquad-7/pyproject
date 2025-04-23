#биток
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    driver.get("https://www.binance.com/ru/markets")

    while True:
        try:
            # Получаем ВСЕ элементы с ценами (не только первый)
            price_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'div[data-area="right"].layout-ellipsis.t-Body2.w-\\[148px\\].items-center')
                )
            )
            desired_index = 0  

            if len(price_elements) > desired_index:
                print(f"Цена валюты: {price_elements[desired_index].text}")
            else:
                print(f"Элемент с индексом {desired_index} не найден")

        except Exception as e:
            print(f"Ошибка при получении элементов: {str(e)}")

        time.sleep(3)

except KeyboardInterrupt:
    print("Парсинг остановлен пользователем")
finally:
    driver.quit()
