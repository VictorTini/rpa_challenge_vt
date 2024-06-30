import re
import os
import csv
from datetime import datetime
import requests
import uuid
import glob

from RPA.Excel.Files import Files


def create_image_folder() -> None:
    dir = "./images"
    if not os.path.exists(dir):
        os.makedirs(dir)


def set_month_range(number_of_months: int) -> tuple[str, str]:
    today = datetime.date.today()
    end = today.strftime("%m/%d/%Y")
    if number_of_months < 2:
        start = today.replace(day=1).strftime("%m/%d/%Y")
    else:
        start = (
            (today - datetime.timedelta(days=30 * (number_of_months - 1)))
            .replace(day=1)
            .strftime("%m/%d/%Y")
        )
    return start, end


def extract_date(date: str) -> str:
    try:
        date_part = date.split('\n')[-1]
        date_part = date_part.replace('Published On ', '').replace('Last update ', '')
        date_obj = datetime.strptime(date_part, '%d %b %Y')
        return date_obj.strftime('%d/%m/%Y')
    except:
        return 'Without Date'

# def write_csv_data(data: list) -> None:
#     with open("result.csv", "w") as f:
#         writer = csv.writer(f)
#         # writer.writerow(header)
#         writer.writerows(data)


def write_csv_data(data: list) -> None:
    wb = Files()
    wb.create_workbook()
    wb.append_rows_to_worksheet(data)
    wb.save_workbook("result.xlsx")


def download_image_from_url(image_url: str) -> str:
    image_name = str(uuid.uuid4())
    if image_url == "":
        return ""
    img_data = requests.get(image_url).content
    with open(f"./images/{image_name}.jpg", "wb") as handler:
        handler.write(img_data)
    return image_name


def check_phrases(text_pattern: str, text: str, count=0) -> int:
    c = count
    words = text.split()
    for word in words:
        if word.strip(",.;:-?!") == text_pattern:
            c += 1
    return c


def check_for_dolar_sign(text: str) -> bool:
    pattern = re.compile(
        "((\$\s*\d{1,}.\d{0,}.\d{0,})|(\d{1,}\s*(dollars|usd|dollar)))", re.IGNORECASE
    )

    if re.search(pattern, text):
        return True
    return False


def split_extracted_text(text: list) -> tuple[str, str]:
    try:
        date, title, description, *r_date = text

        return date, title, description
    except:
        return "", "", ""


def get_all_files_from_folder(path="./images/*.jpg"):
    files = glob.glob(path)
    return files


if __name__ == "__main__":
    print(set_month_range(1))