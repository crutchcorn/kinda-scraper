from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement

driver = webdriver.Chrome()
driver.implicitly_wait(30)


def findNextButton():

    return driver.find_element_by_css_selector(
        "[data-ga*=\"More stories click\"]")


def findArticles():
    return driver.find_elements_by_css_selector('article.js_post_item')


def findLink(articleEl: WebElement):
    link = articleEl.find_element_by_css_selector('[data-ga*="post click"]')
    return link.get_attribute('href')


# Navigate to the application home page
driver.get("https://kinja.com/rockmandash12")

links = []
done = False
while not done:
    articles = findArticles()

    for article in articles:
        links.append(findLink(article))

    try:
        nextButton = findNextButton()
        nextButton.click()
    except NoSuchElementException:
        done = True
        break

with open('article_list.txt', 'w') as filehandle:
    for listitem in links:
        filehandle.write('%s\n' % listitem)

# close the browser window
driver.quit()
