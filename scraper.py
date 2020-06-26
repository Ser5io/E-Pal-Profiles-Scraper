from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import re
import pandas as pd
from random import randint
import time
from datetime import datetime

startID = 22  # First user number
endID = 24  # Last user number

pageLoadDelay = 5  # seconds
contentLoadDelay = 2  # seconds

CHROME_PATH = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
CHROMEDRIVER_PATH = 'C:\Program Files (x86)\Google\Chrome\chromedriver.exe'
WINDOW_SIZE = "1920,1080"

chrome_options = Options()
chrome_options.add_argument("--headless")  # comment this line if you want to see the scraper working
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.binary_location = CHROME_PATH

game = []
username = []
link = []
gamePrice = []
served = []
age = []
following = []
followers = []
visitors = []
recommended = []
averageScore = []

driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                          options=chrome_options)
driver.implicitly_wait(5)

for i in range(startID, endID + 1):
    currentLink = 'https://www.epal.gg/epal/{i}'.format(i=i)

    driver.get(currentLink)

    try:
        myElem = WebDriverWait(driver, pageLoadDelay).until(EC.presence_of_element_located((By.ID, "root")))
        time.sleep(3)
        myElem = WebDriverWait(driver, contentLoadDelay).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ant-typography-ellipsis-single-line')))

        while myElem.text == '':
            myElem = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'ant-typography-ellipsis-single-line')))
        time.sleep(1)
        myElem = driver.find_elements_by_class_name('ant-typography-ellipsis-single-line')
        if len(myElem) > 1:
            while myElem[1].text == '':
                myElem = driver.find_elements_by_class_name('ant-typography-ellipsis-single-line')
        print("Extracting profile of user number {i}".format(i=i))
    except TimeoutException:
        print("Either user does not exist or loading took too much time! (There might be a problem with the internet connection)")
        continue
    except Exception:
        print("Unexpected Error...saving the fetched profiles")
        break

    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")

    link.append(currentLink)

    spans = soup.find_all('span', attrs={'class': 'ant-typography-ellipsis-single-line'})
    username.append(spans[0].text)
    if len(spans) > 1:
        game.append(spans[1].text)
        spans = spans[1].parent.parent.parent.find(string=re.compile("^[$]"))
        gamePrice.append(spans)
    else:
        game.append("No Game")
        gamePrice.append("No Game")

    Div = soup.find('div', text="Average Score")
    spans = Div.parent.find_all('span')
    if spans[0].text != '':
        averageScore.append(spans[0].text)
    else:
        averageScore.append("No Game")

    Div = soup.find('div', text="Served")
    spans = Div.parent.find_all('span')
    served.append(spans[0].text)

    Div = soup.find('div', text="Recommended")
    spans = Div.parent.find_all('span')
    recommended.append(spans[0].text)

    Div = soup.find('div', text="Age")
    spans = Div.parent.find_all('div')
    age.append(spans[0].text)

    spans = Div.parent.find_next_siblings("a")

    following.append(spans[0].contents[0].contents[0].text)

    followers.append(spans[1].contents[0].contents[0].text)

    visitors.append(spans[2].contents[0].contents[0].text)

driver.close()
if game:
    df = pd.DataFrame({'Game': game, 'Username': username, 'Link': link, 'Game Price': gamePrice, 'Served': served,
                       'Age': age, 'Following': following, 'Followers': followers, 'Visitors': visitors,
                       'Recommended': recommended, 'Average Score': averageScore})
    try:
        df.to_csv('profiles_{datetime}.csv'.format(datetime=datetime.today().strftime("%d-%m-%Y--%H-%M-%S")), index=False, encoding='utf-8')
    except PermissionError:
        fileName = 'profiles{randomNumber}.csv'.format(randomNumber=randint(1, 100000))
        df.to_csv(fileName, index=False, encoding='utf-8')
        print('profiles.csv file was still open so we saved it as ', fileName)

else:
    print('Nothing to save')
