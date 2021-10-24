from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime
import requests
import re

"""
    Created by Yo Han Joo, yhjoo@kth.se

    MIT License

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
    to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
    and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

#### sets driver up
def setup():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % "1920,1080")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    return driver

#### Scrapes blog posts in particular website from json
def scrape_json(blog_link, isOffset, blog_posts):
    response = requests.get(blog_link + ("&format=json-pretty" if isOffset else "?format=json-pretty"))
    dict_response = response.json()
    for post_from_website in dict_response['items']:
        post = { # This can be changed to include a lot of information about each post
            'title': post_from_website['title'],
            'body': re.sub('<[^<]+?>', '', post_from_website['body']).replace("\n", " ").replace("&nbsp", " ").strip(), # remove \n, &nbsp tags
            'published_date': datetime.datetime.fromtimestamp(post_from_website['publishOn']//1000.0)
        }
        blog_posts.append(post) # add to post

#### Loop every page until 'older posts' is found
def scrape_all_pages(blog_posts, driver):
    page = 0
    while True:
        scrape_json(driver.current_url, True if page > 0 else False, blog_posts)
        older_link = None
        try:
            older_link = driver.find_element_by_xpath('//a[@rel="next"]')
        except:
            break
        driver.execute_script("arguments[0].click();", older_link)
        page += 1

#### Exports the dictionary list into pandas dataframe
def export_via_pd(blog_posts):
    df = pd.DataFrame(blog_posts)
    print(df.head())
    df.to_csv('export.csv', encoding='utf-8', index=False)

#### Run Scraper with given blog link
def run_scraper(blog_link):

    # holds all of the info for blog posts
    blog_posts = []

    # Run
    driver = setup()
    driver.get(blog_link)
    scrape_all_pages(blog_posts, driver)
    export_via_pd(blog_posts)

if __name__ == '__main__':
    print('Enter base blog link: ')
    blog_link = input()
    run_scraper(blog_link)

