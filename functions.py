import re
import os
import csv
from datetime import datetime, timedelta
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
        today = datetime.today()

        if 'hour ago' in date or 'hours ago' in date:
            return today.strftime('%d/%m/%Y')
        elif 'day ago' in date or 'days ago' in date:
            days_ago = int(date.split()[0])
            date_converted = today - timedelta(days=days_ago)
            return date_converted.strftime('%d/%m/%Y')
        else:
            match = re.search(r'\b([A-Za-z]{3} \d{1,2}, \d{4})\b', date)
            if match:
                date_converted = datetime.strptime(match.group(1), '%b %d, %Y')
                return date_converted.strftime('%d/%m/%Y')
            else:
            # Return the original string if no date found
                return 'No data'
    except:
        return 'No data'



# def write_csv_data(data: list) -> None:
#     with open("result.csv", "w") as f:
#         writer = csv.writer(f)
#         # writer.writerow(header)
#         writer.writerows(data)


def write_csv_data(data: list) -> None:
    #headers = ["date", "title", "description", "picture_filename", "title_dolar", "description_dolar", "count"]
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