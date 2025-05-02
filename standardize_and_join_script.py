import pandas as pd
import titlecase


def shorten_author(name):
    if not isinstance(name, str):
        return name

    parts = name.strip().split()

    if all(len(p) == 2 and p.endswith('.') for p in parts[:-1]) and len(parts) >= 2:
        return name

    if len(parts) == 3:
        first, middle, last = parts
        return f"{first} {middle[0]}. {last}"

    elif len(parts) > 3:
        first = parts[0]
        middle = parts[1]
        last = parts[-1]
        return f"{first} {middle[0]}. {last}"

    return name

def clean_price(price):
    if pd.isnull(price):
        return price
    first_price = str(price).split(' ')[0].strip() + ' Денари'
    return first_price

def fix_author_format(name):
    if isinstance(name, str) and ',' in name:
        parts = [part.strip() for part in name.split(',', 1)]
        if len(parts) == 2:
            return f"{parts[1]} {parts[0]}"
    return name

df = pd.read_csv("knigamk_books.csv")

df['Наслов'] = df['Наслов'].apply(lambda x: titlecase.titlecase(x) if isinstance(x, str) else x)

df['Автор'] = df['Автор'].apply(shorten_author)

df["Година"] = df["Година"].astype("Int64")
df["Страници"] = df["Страници"].astype("Int64")
df["Цена"] = df["Цена"].apply(clean_price)
df["Извор"] = "knigamk"

df.to_csv("knigamk_books_standardized.csv", index=False)

df1 = pd.read_csv("antolog_books.csv")

df1['Цена'] = df1['Цена'].apply(lambda x: x.replace(',00', '') if isinstance(x, str) and ',00' in x else x)
df1["Извор"] = "antolog"

df1.to_csv("antolog_books_standardized.csv", index=False)

df2 = pd.read_csv("akademska_knigа_books.csv")

df2['Автор'] = df2['Автор'].apply(fix_author_format)
df2["Извор"] = "akademska kniga"

df2.to_csv("akademska_kniga_books_standardized.csv", index=False)

df3 = pd.read_csv("literatura_books.csv")
df3["Извор"] = "literatura"
df3.to_csv("literatura_books_standardized.csv", index=False)

dataframes = [df, df1, df2, df3]

merged_df = pd.concat(dataframes, ignore_index=True)

merged_df.to_csv("all_books_standardized.csv", index=False)