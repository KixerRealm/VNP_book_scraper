from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0")

driver = webdriver.Chrome(options=options)


antolog_books_list = set()
visited_links = set()


for i in range(1, 52):
    search_url = f"https://antolog.mk/product-category/knigi/fiktsija/page/{i}/"
    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "products"))
        )

        products_list = driver.find_element(By.CLASS_NAME, "products")

        links = products_list.find_elements(By.CSS_SELECTOR, "li.product a.woocommerce-LoopProduct-link")

        for link in links:
            try:
                href = link.get_attribute("href")
                if href:
                    antolog_books_list.add(href)
            except Exception as e:
                print(e)
                continue

    except Exception as e:
        print(f"Error on page {i}: {e}")

print(antolog_books_list)
print(len(antolog_books_list))
books = []

for book_url in antolog_books_list:
    driver.get(book_url)
    time.sleep(1)

    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1.product_title").text
        print(title)
    except NoSuchElementException:
        title = ""

    try:
        description_element = driver.find_element(By.ID, "tab-description")
        description = description_element.text.strip()
        #print(description)
    except NoSuchElementException:
        description = ""

    try:
        info_tab = driver.find_element(By.CSS_SELECTOR, "li.additional_information_tab a")
        driver.execute_script("arguments[0].click();", info_tab)
        time.sleep(0.5)
    except Exception as e:
        print("Could not click tab:", e)

    try:
        author_element = driver.find_element(By.CSS_SELECTOR,'.product-term.product-term--display-name a span.product-term__name')
        author_name = author_element.text.strip()
        print(author_name)
    except NoSuchElementException:
        author_name = ""
        print("Author not found")

    book_details = {}

    try:
        panel = driver.find_element(By.ID, "tab-additional_information")
        table = panel.find_element(By.CSS_SELECTOR, ".shop_attributes")
        rows = table.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            try:
                key = row.find_element(By.TAG_NAME, "th").text.strip()
                try:
                    val = row.find_element(By.TAG_NAME, "td").find_element(By.TAG_NAME, "p").text.strip()
                except NoSuchElementException:
                    val = row.find_element(By.TAG_NAME, "td").text.strip()

                if key and val:
                    book_details[key] = val
            except Exception:
                continue

        # Price
        try:
            price_element = driver.find_element(By.CSS_SELECTOR, ".price .woocommerce-Price-amount")
            price = price_element.text.strip().split(" ")[0] + " Денари"
            print(price)
            if price:
                book_details["Цена"] = price
        except NoSuchElementException:
            print("Price not found")

    except Exception as e:
        print("Details table not found:", e)

    print(book_details)

    #print(book_details)
    book =  {
        "Наслов" : title,
        "Опис" : description,
        "Kатегорија" : "Фикција",
        "Автор" : author_name,
        "Издавач" : book_details["Издавач"] if book_details.__contains__("Издавач") else "",
        "Година" : book_details["Година"] if book_details.__contains__("Година") else "",
        "Страници" : book_details["Страници"] if book_details.__contains__("Страници") else "",
        "Цена" : book_details["Цена"] if book_details.__contains__("Цена") else ""
    }
    books.append(book)

print(books)
df = pd.DataFrame(books)
df.to_csv("antolog_books.csv", index=False)

