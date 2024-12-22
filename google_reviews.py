import time,csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,WebDriverException
from datetime import datetime
from dateutil.relativedelta import relativedelta


class GetGoogleReviews:
    def __init__(self, url:str):

        self.donwload_google_reviews(url)



    def donwload_google_reviews(self, url:str):

        def time_converter(date: str):

            current_time = datetime.now()
            date = date.split(' ')[1:]

            if  'un'  in date or 'una' in  date:
                date[0] = 1
            else:
                date[0]=int(date[0])

            if date[1] == 'día' or date[1] == 'días':
                relative_time = relativedelta(days=date[0])
            if date[1] == 'mes' or date[1] == 'meses':
                relative_time = relativedelta(months=date[0])
            if date[1] == 'semana' or date[1] == 'semanas':
                relative_time = relativedelta(weeks=date[0])
            if date[1] == 'año' or date[1] == 'años':
                relative_time = relativedelta(years=date[0])

            new_time = current_time - relative_time
            formatted_date = new_time.strftime("%Y-%m-%d")

            return formatted_date

        def get_data(driver):

            count=1
            print('getting data... please wait')
            more_elements = driver.find_elements(By.CLASS_NAME, 'w8nwRe.kyuRq')

            for list_more_element in more_elements:
                list_more_element.click()

            elements = driver.find_elements(By.CLASS_NAME,'jftiEf')

            lst_data = [ ]

            for data in elements:

                try:
                    #name = data.find_element(By.CLASS_NAME, 'd4r55 ').text
                    user = f'user_{count}'
                    text = data.find_element(By.CLASS_NAME, 'wiI7pd').text
                    time=data.find_element(By.CLASS_NAME,'rsqaWe').text
                    date = time_converter(time)
                    score = data.find_element(By.CLASS_NAME,'kvMYJc').get_attribute("aria-label")

                except NoSuchElementException:
                    text = "Text Null"

                lst_data.append([user, text, time, date, score]) # name

                #print(len(lst_data),' row is generated')

                count+=1

            return lst_data

        def counter(tittle):

        #deprecated: result = driver.find_element_by_class_name('jANrlb').find_element_by_class_name('fontBodySmall').text

            result = driver.find_element(By.CLASS_NAME,'jANrlb').text
            rating = result[:3]
            result = result.split('\n')[1].split(' ')
            result =  result[0]

            print(f'{tittle}  has {rating}  and {result} reviews ')

            if '.' in result:
                result = int(result.replace('.', ''))
                if result >=2500:
                    print("to many reviews to scroll... fetched to 200 scroll down ") # each scroll down takes 2 sec  to wait comments to appears
                    result = 200
                    return result
                return int((result / 10) + 1)

            return int(int(result) / 10) + 1

        def scrolling(counter):

            print('scrolling over the reviews...')

            scrollable_div = driver.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[11]/div')

            for _i in range(counter):
                #time.sleep(2)
                try:
                    scrolling = driver.execute_script(
                        'document.getElementsByClassName("dS8AEf")[0].scrollTop = document.getElementsByClassName("dS8AEf")[0].scrollHeight',
                        scrollable_div, time.sleep(2))

                except WebDriverException:

                    print('stop scrolling... ')
                    return

            print("scrolling was complete")

            # Scroll up
            driver.execute_script('document.getElementsByClassName("dS8AEf")[0].scrollTop = 0')

        def write_to_csv(data, tittle):

            print('Writing to csv...')
            cols = ['user_id', 'comment', 'time', 'date', 'rating']
            df = pd.DataFrame(data, columns=cols)
            df.to_csv(f'{tittle}_google_reviews.csv')

            print("Your csv was successfully created!")


        print('starting...')

        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument("--headless")  # show browser or not
        chrome_options.add_argument("--lang=en-US")
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)

        #Example
        #URL = 'https://www.google.com/maps/place/El+Curry+Verde/@43.3769804,-1.8015808,17z/data=!3m1!4b1!4m6!3m5!1s0xd5109081bb759a1:0xc866b9f78bb1dc19!8m2!3d43.3769766!4d-1.7967152!16s%2Fg%2F1hc7nn793?entry=ttu'
        #URL = input("Please, paste the url to get the reviews:     ")
        driver.get(url)

        time.sleep(3)

        button = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[1]/div/div/button/span')
        time.sleep(3)
        driver.execute_script("arguments[0].click();", button)

        header =driver.find_element(By.CLASS_NAME,'DUwDvf').text

        reviews = driver.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]/div[2]/div[2]')
        reviews.click()

        counter = counter(header)
        scrolling(counter)

        data = get_data(driver)
        driver.close()

        write_to_csv(data, header)


"""
For the program works properly is necessary the link needs to be in the following form:
https://www.google.com/maps/place/El+Curry+Verde/@43.3769804,-1.8015808,17z/data=!3m1!4b1!4m6!3m5!1s0xd5109081bb759a1:0xc866b9f78bb1dc19!8m2!3d43.3769766!4d-1.7967152!16s%2Fg%2F1hc7nn793?entry=ttu
"""

#def run_ggl():
#
#    question_mark =input("Do you want to download Google reviews? yes/no ")
#
#    if question_mark == 'yes':
#        URL = input("please paste google URL: ")
#        donwload_google_reviews(URL)
#
#    else:
#        with open('empty_list_csv', 'w') as f:
#            csv.writer(f)


URL="https://www.google.com/maps/place/El+Curry+Verde/@43.3769804,-1.8015808,17z/data=!3m1!4b1!4m6!3m5!1s0xd5109081bb759a1:0xc866b9f78bb1dc19!8m2!3d43.3769766!4d-1.7967152!16s%2Fg%2F1hc7nn793?entry=ttu"

GetGoogleReviews(URL)
