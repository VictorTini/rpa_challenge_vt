import time
import os
from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems

from functions import (create_image_folder,extract_date,write_csv_data,download_image_from_url,check_phrases,
                       check_for_dolar_sign,split_extracted_text,get_all_files_from_folder)

#from settings import URL,SEARCH_PHRASE,CATEGORY

#os.environ['RC_WORKSPACE_ID'] = 'e65f7ad1-9f8c-40d5-89dd-3677462fb731'


class RpaChallenge:

    def __init__(self):
        self.browser = Selenium()

    def close_browser(self) -> None:
        self.browser.close_browser()

    def open_website(self, url: str) -> None:
        self.browser.open_available_browser(url)
        self.browser.maximize_browser_window()
        terms_accept = '//*[@id="onetrust-accept-btn-handler"]'
        self.browser.click_button(locator=terms_accept)

    def begin_search(self, search_phrase: str) -> None:
        try:
            search_xpath = '//*[@id="root"]/div/div[1]/div[1]/div/header/div[4]/div[2]/button'
            self.browser.click_button_when_visible(locator=search_xpath)
            field_xpath = '//*[@id="root"]/div/div[1]/div[2]/div/div/form/div[1]/input'
            self.browser.input_text(locator=field_xpath, text=search_phrase)
            go_button_xpath = '//*[@id="root"]/div/div[1]/div[2]/div/div/form/div[2]/button'
            self.browser.click_button_when_visible(locator=go_button_xpath)

        except ValueError as e:
            raise f"Error on execution of begin_search -> {e}"

    def sort_newest_news(self, list_value='date') -> None:
        try:
            sort_dropdow_btn = '//*[@id="search-sort-option"]'
            self.browser.select_from_list_by_value(sort_dropdow_btn, list_value)

        except ValueError as e:
            raise f"Error on execution of sort_newest_news -> {e}"

    def load_all_news(self):
        show_more_button = '//*[@id="main-content-area"]/div[2]/div[2]/button'
        while self.browser.does_page_contain_button(show_more_button):
            try:
                self.browser.wait_until_page_contains_element(locator=show_more_button)
                self.browser.scroll_element_into_view(locator=show_more_button)
                self.browser.click_button_when_visible(show_more_button)
                time.sleep(3)
            except:
                print("Page show more button done")

    def get_element_value(self, path: str) -> str:
        if self.browser.does_page_contain_element(path):
            return self.browser.get_text(path)
        return ""

    def get_image_value(self, path: str) -> str:
        if self.browser.does_page_contain_element(path):
            return self.browser.get_element_attribute(path, "src")
        return ""

    def extract_website_data(self, search_phrase: str) -> None:
        self.load_all_news()
        list_of_news = list(range(1, 101))
        extracted_data = []
        for value in list_of_news:
            element_list = f'//*[@id="main-content-area"]/div[2]/div[2]/article[{value}]'
            date = extract_date(self.get_element_value(f"{element_list}/div[2]/div[2]"))
            title = self.get_element_value(f"{element_list}/div[2]/div[1]")
            description = self.get_element_value(f"{element_list}/div[2]/div[2]")
            image = download_image_from_url(self.get_image_value(f"{element_list}/div[3]/div/div/img"))
            is_title_dolar = check_for_dolar_sign(title)
            is_description_dolar = check_for_dolar_sign(description)
            phrases_count = check_phrases(text_pattern=search_phrase, text=title)

            extracted_data.append(
                [
                    date,
                    title,
                    description,
                    image,
                    is_title_dolar,
                    is_description_dolar,
                    check_phrases(
                        text_pattern=search_phrase,
                        text=description,
                        count=phrases_count,
                    ),
                ]
            )
            time.sleep(2)
        write_csv_data(extracted_data)


    def main(self) -> None:
        try:
            create_image_folder()
            wi = WorkItems()
            wi.get_input_work_item()
            url = wi.get_work_item_variable("url")
            search_phrase = wi.get_work_item_variable("search_phrase")
            # category = wi.get_work_item_variable("category")
            #number_of_months = wi.get_work_item_variable("number_of_months")
            self.open_website(url=url)
            time.sleep(2)
            self.begin_search(search_phrase=search_phrase)
            # self.select_category(categorys=category)
            time.sleep(2)
            self.sort_newest_news()
            #self.set_date_range(number_of_months)
            self.extract_website_data(search_phrase)
            wi.add_work_item_file("./result.xlsx", "RESULT_EXCEL.xlsx")
            files = get_all_files_from_folder()
            wi.create_output_work_item(files=files, save=True)
            wi.create_output_work_item(files="./result.xlsx", save=True)

        finally:
            self.close_browser()


@task
def run_main_task():
    obj = RpaChallenge()
    obj.main()

if __name__ == "__main__":
    run_main_task()