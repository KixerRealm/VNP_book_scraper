from selenium import webdriver
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


akademska_books_list = []
visited_links = set()

page_number_url = f"https://akademskakniga.mk/BooksM/BooksPoSubCat/707?page=1"
driver.get(page_number_url)
page_container = driver.find_element(By.CLASS_NAME,"PagedList-pageCountAndLocation")
num_pages = int(page_container.text.split(" ")[3])
print(num_pages)

for i in range(1, num_pages):
    search_url = f"https://akademskakniga.mk/BooksM/BooksPoSubCat/707?page={i}"
    driver.get(search_url)

    try:
        all_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='BookMojDetails']")
        for link in all_links:
            if link.text.strip() != "":
                href = link.get_attribute("href")
                akademska_books_list.append(href)

    except Exception as e:
        print(e)

print(akademska_books_list)
books = []

for book_url in akademska_books_list:
    driver.get(book_url)
    time.sleep(1)

    title = driver.find_element(By.CSS_SELECTOR, "h5")
    #print(title.text)

    description = driver.find_element(By.CLASS_NAME, "single-book-text")
    #print(description.text)

    category = driver.find_element(By.CSS_SELECTOR, "h2")
    print(category.text)

    book_details = {}
    try:
        card_body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "card-body"))
        )

        ul = card_body.find_element(By.TAG_NAME, "ul")
        li_elements = ul.find_elements(By.TAG_NAME, "li")

        for li in li_elements:
            try:
                label_element = li.find_element(By.TAG_NAME, "label")
                span_element = li.find_element(By.TAG_NAME, "span")

                key = label_element.text.strip().rstrip(":")
                val = span_element.text.strip()

                if key and val:
                    book_details[key] = val

            except:
                continue

        try:
            price_div = card_body.find_element(By.CLASS_NAME, "offset-1")
            price_span = price_div.find_elements(By.TAG_NAME, "span")
            price = price_span[1].text.strip() + " Денари"

            if price:
                book_details["Цена"] = price

        except:
            print("Price not found")
    except:
        print("No <ul> found inside card-body!")

    print(book_details)

    if len(books) >= 549:
        break

    book =  {
        "Наслов" : title.text,
        "Опис" : description.text,
        "Категорија" : category.text,
        "Автор" : book_details["Автор"] if book_details.__contains__("Автор") else "",
        "Издавач" : book_details["Издавач"] if book_details.__contains__("Издавач") else "",
        "Година" : book_details["Година"] if book_details.__contains__("Година") else "",
        "Страници" : book_details["Страници"] if book_details.__contains__("Страници") else "",
        "Цена" : book_details["Цена"] if book_details.__contains__("Цена") else ""
    }
    books.append(book)

df = pd.DataFrame(books)
df.to_csv("akademska_knigа_books.csv", index=False)

