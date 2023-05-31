from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
# chrome driver downlad: https://sites.google.com/chromium.org/driver/?pli=1

PATH = "chromedriver64/chromedriver.exe"
driver = webdriver.Chrome(PATH) # chose chrome as our browser

# open up a website 
driver.get("https://www.boots.com/savings")
print(driver.title) # grabs the title of the website

# search by element - below we're searching for element 'name'='searchTerm'
# search_box = driver.find_element(By.NAME,"searchTerm")
# search_box.send_keys("purfume") # this allows us to put 'test' in the search box
# search_box.send_keys(Keys.RETURN) # click 'ENTER/RETURN'

# scrape and access entire website
# print(driver.page_source)

content = driver.find_element(By.CLASS_NAME, 'product_listing_container') 
#print("content",content.text)
products = content.find_elements(By.CLASS_NAME, 'product_name_link')
for product in products: 
    product_title = product.text
    print("product_title:",product_title)

time.sleep(5)


driver.quit() # close the browser