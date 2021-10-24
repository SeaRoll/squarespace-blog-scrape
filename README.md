# squarespace-blog-scrape
#### Description
This is a Squarespace blog scraper. selenium, and pandas was used to create the scraper.
According to [squarespace](https://developers.squarespace.com/view-json-data), A json view of a certain 
blog page can be viewed with all of its item.
The question now is, why would selenium be needed?

The reason for selenium being used is because it only shows the max amounts of post in that certain page.
Selenium allows us to scrape all of the posts inside the blog page.

#### How it was made

this is the setup function for our chromium driver. by setting it to headless and windows size, 
we can expect that the 'hidden'
chrome browser will show in desktop view.
```python
def setup():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % "1920,1080")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    return driver
```


this is the json scraper for the particular web page. the request link is depending on if it's the base page or a older posts page.
it then takes all of the items inside the json returned and adds a post to the `blog_posts` list. keep in mind that squarespace gives a longer
list on available data that can be scraped
```python
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
```


this function takes the driver and tries to find the older posts link. for each time it finds the link, it will click on the link and scrape the
json content inside the page. `page` is used to determine if it's the base page or not.
```python
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
```


this gets the list of blog posts and then exports to csv
```python
def export_via_pd(blog_posts):
    df = pd.DataFrame(blog_posts)
    print(df.head())
    df.to_csv('export.csv', encoding='utf-8', index=False)
```


This is the base function that runs the scraper.
```python
def run_scraper(blog_link):

    # holds all of the info for blog posts
    blog_posts = []

    # Run
    driver = setup()
    driver.get(blog_link)
    scrape_all_pages(blog_posts, driver)
    export_via_pd(blog_posts)
```
