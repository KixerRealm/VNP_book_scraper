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


knigamk_books_list = set()
visited_links = set()


for i in range(1, 13):
    search_url = f"https://kniga.mk/c/9/knigi/beletristika/romani?sort=publish_at-DESC&page={i}"
    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product-single"))
        )

        products = driver.find_elements(By.CLASS_NAME, "product-single")

        for product in products:
            try:
                link = product.find_element(By.CSS_SELECTOR, ".product-thumb a")
                href = link.get_attribute("href")
                if href:
                    knigamk_books_list.add(href)
            except Exception as e:
                print(e)
                continue

    except Exception as e:
        print(f"Error on page {i}: {e}")

print(knigamk_books_list)
print(len(knigamk_books_list))
books = []

for book_url in knigamk_books_list:
    driver.get(book_url)
    time.sleep(1)

    title = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()

    try:
        description_div = driver.find_element(By.ID, "tab1")
        paragraphs = description_div.find_elements(By.TAG_NAME, "p")
        description = "\n".join([p.text.strip() for p in paragraphs if p.text.strip() != ""])
    except NoSuchElementException:
        description = ""

    #print(description)

    book_details = {}

    try:
        product_info = driver.find_element(By.CLASS_NAME, "product-info")

        spans = product_info.find_elements(By.CSS_SELECTOR, "span.item-number, span.item-cat")

        for span in spans:
            text = span.text.strip()
            if ":" in text:
                key, value = text.split(":", 1)
                book_details[key.strip()] = value.strip()

        try:
            price = product_info.find_element(By.CLASS_NAME, "price").text.strip()
            if price:
                book_details["Цена"] = price
        except:
            print("Price not found")

    except Exception as e:
        print(f"Error parsing book details: {e}")
    print(book_details)

    print(book_details)
    book =  {
        "Наслов" : title,
        "Опис" : description,
        "Kатегорија" : book_details["Жанр"] if book_details.__contains__("Жанр") else "",
        "Автор" : book_details["Автор"] if book_details.__contains__("Автор") else "",
        "Издавач" : book_details["Издавач"] if book_details.__contains__("Издавач") else "",
        "Година" : book_details["Година на издавање"] if book_details.__contains__("Година на издавање") else "",
        "Страници" : book_details["Број на страни"] if book_details.__contains__("Број на страни") else "",
        "Цена" : book_details["Цена"] if book_details.__contains__("Цена") else ""
    }
    books.append(book)

print(books)
df = pd.DataFrame(books)
df.to_csv("knigamk_books.csv", index=False)

