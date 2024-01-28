import time,csv
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By


"""
This script scrapes reviews from TripAdvisor in Spanish, so you will need to make a change at line 74 def reformat_date():
The function maps the time to convert spanish strings ("13 de julio de 2023") into datetime object 12/07/2023.
"""

def trip_reviews(URL):

    print("starting... please wait")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # show browser or not
    chrome_options.add_argument("--lang=en-US")
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    lst_data = []
    count = 1
    scrapping = True

    url = URL
    driver.get(url)

    #wait until the page it refreshes
    time.sleep(2)

    try:
        reject = driver.find_element(By.XPATH,'//*[@id="onetrust-pc-btn-handler"]')
        reject.click()
        time.sleep(2)

        no_cookies = driver.find_element(By.CLASS_NAME,'ot-pc-refuse-all-handler')
        no_cookies.click()

    except:
        print("Oups... the page does not work as expected, try again..")

    tittle = driver.find_element(By.CLASS_NAME,'acKDw.w.O').text
    tittle = tittle.split()[:-2]

    header = '_'.join(t for t in tittle)


    def scroll():
        #Wait refresh page
        time.sleep(2)

        #Scroll:
        reviews_div = driver.find_element(By.CLASS_NAME,'ratings_and_types')
        driver.execute_script('arguments[0].scrollIntoView(true)',reviews_div)
        more_elements = driver.find_elements(By.CLASS_NAME, 'taLnk.ulBlueLinks')

        #If 'more' button is available click once because all the texts it expands
        if len(more_elements):
            for list_more_element in more_elements:
                list_more_element.click()
                break

        elements = driver.find_elements(By.CLASS_NAME, 'ui_column.is-9')

        return elements

    def reformat_date(date):

        split_dates = date.split()
        day_str = split_dates[0]
        month_str = split_dates[2]
        year_str = split_dates[-1]

        month_mapping = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
            "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
            "septiembre": 9, "octubre": 10, "noviembre": 11,
            "diciembre": 12
        }

        month_str = str(month_mapping[month_str])

        dates_str = day_str + '-' + month_str + '-' + year_str
        datetime_obj = datetime.strptime(dates_str, "%d-%m-%Y").date()
        date = datetime_obj.strftime("%m/%d/%Y")

        return datetime_obj, date

    def dates_flag(dates):

        # Check if the comment is too old:
        date_str = dates.split("Opinión escrita el",1)[1]
        date_obg, date_str = reformat_date(date_str)

        today = datetime.now().date()
        timedelta_obj = (today - date_obg)

        years = int(round(timedelta_obj.days / 365.25))

        if years > 5:

            #It returns False to stop the while loop and stop scrolling
            return False

        else:
            return date_str

    def write_to_csv(data, header):

        cols = ['user_id', 'comment', 'date']  # name
        df = pd.DataFrame(data, columns=cols)
        df.to_csv(f'{header}_tripadvisor_reviews.csv')

        print("Your csv was successfully created!")

    while scrapping:

        elements = scroll()
        time.sleep(2)
        try:
            for element in elements:
                try:

                    user = f'user_{count}'
                    text = element.find_element(By.CLASS_NAME,'partial_entry').text
                    dates = element.find_element(By.CLASS_NAME,'ratingDate').text
                    dates = dates_flag(dates)

                    if not dates:
                        scrapping = False
                        break

                except:
                    user = None
                    text = None

                if user != None:

                    lst_data.append([user, text, dates])
                    count += 1

            #next page
            next = driver.find_element(By.CLASS_NAME,'nav.next.ui_button.primary')
            next.click()


        except:
            srapping = False
            print("scrapping end")

    print("Scraping end it")
    print(f"the csv has {len(lst_data)}  rows")

    write_to_csv(lst_data, header)
    driver.close()

"""
For the program works properly is necessary the link needs to be in the following form:
https://www.tripadvisor.es/Restaurant_Review-g616235-d2708477-Reviews-El_Curry_Verde_Restaurante_Vegetariano-Hondarribia_Province_of_Guipuzcoa_Basque_C.html
"""

def run_trpdvsr():
    question_mark =input("Do you want to download TripAdvisor reviews? yes/no ")

    if question_mark == 'yes':
        URL = input("please paste TripAdvisor URL: ")
        trip_reviews(URL)

    else:
        with open('empty_list_csv', 'w') as f:
            csv.writer(f)

