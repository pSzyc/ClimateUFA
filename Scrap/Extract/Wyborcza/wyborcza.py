#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import csv
import os
from selenium import webdriver
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options

html_parser = {
    'title': 'art-title',
    'department': 'art-product-name',
    'author': 'art-author',
    'date': 'art-datetime',
    'text': 'art_paragraph'
    }

def list_articles(url):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    articles = soup.find_all(class_='result-item-link',href=True)
    return articles

def get_article_data(link, driver):
    data = {
        'title': None,
        'department': None,
        'author': None,
        'date': None,
        'text': None,
        'link': link
    }
    try:
        driver.get(link)
    except:
        print('ERROR')
        data['title'] = 'ERROR'
        return data
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for key, value in html_parser.items():
        try:
            if key == 'text':
                paragraphs = soup.find_all(class_=value)
                data[key] = " ".join([paragraph.text for  paragraph in paragraphs]).replace('\n',"").strip()
            else:
                data[key] = soup.find(class_=value).text.replace('\n',"").strip()
        except:
            pass
    return data

def process_page(link_page, driver):
    data_list = []    
    articles = list_articles(link_page)
    for article in articles:
        link='https://classic.wyborcza.pl/archiwumGW/'+article['href']
        data = get_article_data(link, driver=driver)
        data_list.append(data)
    return data_list

if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-data-dir=selenium")

    csv_file = 'wyborcza.csv'
    if not os.path.exists(csv_file):
        print(f"Creating file {csv_file}")
        column_names = ['Title', 'Department', 'Author', 'Date', 'Text', 'Link']
        with open(csv_file, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_names)
    else:
        print(f"Appending to {csv_file}")

    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        page = 0
        for page in tqdm(range(4930)):
            driver = webdriver.Chrome(options=chrome_options)
            link_page = f'https://classic.wyborcza.pl/archiwumGW/0,160510.html?searchForm=&datePeriod=0&initDate=2020-10-5&endDate=2022-12-31&publicationsString=1%3B5&author=&page={page}&sort=OLDEST'
            data_list = process_page(link_page, driver=driver)
            if len(data_list) == 0:
                print(f"No more articles found on page {page}")
                break
            for data in data_list:
                writer.writerow([data['title'], data['department'], data['author'], data['date'], data['text'], data['link']])    
            driver.quit()