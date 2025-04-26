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


literatura_books_list = set()
visited_links = set()

page_number_url = f"https://www.literatura.mk/knigi-za-deca-i-mladi/page-1"
driver.get(page_number_url)
page_container = driver.find_elements(By.CLASS_NAME,"number a")
num_pages = int(page_container[-1].text)
print(num_pages)

for i in range(0, int(num_pages/2)):
    search_url = f"https://www.literatura.mk/knigi-za-deca-i-mladi/page-{i}"
    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "btn-wrapper"))
        )

        btn_wrappers = driver.find_elements(By.CLASS_NAME, "btn-wrapper")

        for wrapper in btn_wrappers:
            try:
                link = wrapper.find_element(By.TAG_NAME, "a")
                href = link.get_attribute("href")
                if href:
                    literatura_books_list.add(href)
            except:
                continue

    except Exception as e:
        print(f"Error on page {i}: {e}")

books = []

for book_url in literatura_books_list:
    driver.get(book_url)
    time.sleep(1)

    title = driver.find_element(By.CSS_SELECTOR, "h1")
    #print(title.text)

    try:
        description = driver.find_element(By.ID, "tab_product_description").text
        #print(description.text)
    except NoSuchElementException:
        description = ""
        #print(description)

    try:
        attr_tab = driver.find_element(By.CSS_SELECTOR, 'a[href="#tab_product_product_atributes"]')
        driver.execute_script("arguments[0].click();", attr_tab)
        time.sleep(0.5)
    except Exception as e:
        print(e)

    book_details = {}
    try:
        card_body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-detail-wrapper"))
        )
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-attrbite-table"))
        )
        rows = table.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            try:
                elements = row.find_elements(By.TAG_NAME, "td")
                key = elements[0].text
                val = elements[1].text
                if key and val:
                    book_details[key] = val

            except:
                continue

        try:
            price_mkd = card_body.find_element(By.CSS_SELECTOR, ".product-price-value").text.strip()
            price = price_mkd + " Денари"
            print(price)
            if price:
                book_details["Цена"] = price

        except:
            print("Price not found")
    except:
        print("No <ul> found inside card-body!")


    book =  {
        "Наслов" : title.text,
        "Опис" : description,
        "Категорија" : book_details["Категорија"] if book_details.__contains__("Категорија") else "",
        "Автор" : book_details["Автор"] if book_details.__contains__("Автор") else "",
        "Издавач" : book_details["Издавач"] if book_details.__contains__("Издавач") else "",
        "Година" : book_details["Година на објавување"] if book_details.__contains__("Година на објавување") else "",
        "Страници" : book_details["Број на страници"] if book_details.__contains__("Број на страници") else "",
        "Цена" : book_details["Цена"] if book_details.__contains__("Цена") else ""
    }
    books.append(book)

print(books)
df = pd.DataFrame(books)
df.to_csv("literatura_books.csv", index=False)

