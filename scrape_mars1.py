# Dependencies
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import pymongo

# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
    
# Define database and collection
db = client.mars_db
collection = db.items

def scrape_mars():


    # -----NASA Mars News-----

    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response.text, 'html.parser')
    #print(soup.prettify())
    # Collect the latest news from NASA Mars News Site
    news_title = soup.title.text
    # Collect the latest news paragraph text
    news_p = soup.p.text

    #----JPL Mars Space Images - Featured Image-----

    # URL of page to be scraped
    url_images = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    # Retrieve page with the requests module
    response_images = requests.get(url_images)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response_images.text, 'html.parser')

    # Collect article with class- fancybox and then determine its href
    image_article=soup.find("a",class_='fancybox')
    image_path=image_article.get('data-fancybox-href')

    # Determine the image ural by concatenating https:...
    featured_image_url=("https://www.jpl.nasa.gov"+(image_path))


    #-----Mars Weather -----

    # URL of page to be scraped
    url_weather = 'https://twitter.com/marswxreport?lang=en'

    # Retrieve page with the requests module
    response_weather = requests.get(url_weather)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response_weather.text, 'html.parser')

    # source for splitlines= https://www.google.com/search?q=remove+%5Cn+in+python&rlz=1C1CHBF_enUS839US840&oq=remove+%5Cn+in+python&aqs=chrome..69i57j0l5.8972j1j9&sourceid=chrome&ie=UTF-8
    # Collect all Div with class as tweet text container and then find its paragraph
    container=soup.find("div",class_='js-tweet-text-container')
    weather=container.find("p",class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')
    # Use Splitlines to remove /n
    weather=weather.text.splitlines()
    #weather

    # Manipulate temp, pressure and wind variables
    wind=weather[1]
    temp=weather[0][8:]
    #temp
    pressure=weather[2][:-26]
    #pressure

    # Declaring empty mars_weather list and appending with manipulated temp,wind and pressure
    mars_weather=[]
    mars_weather.append(temp)
    #mars_weather
    mars_weather.append(wind)
    #mars_weather
    mars_weather.append(pressure)
    #mars_weather


    #--------Mars Facts-------

    # URL of page to be scraped
    url_facts = 'https://space-facts.com/mars/'
    facts_df=pd.read_html(url_facts)[0]

    # Rename the columns of facts table
    facts_df= facts_df.rename(columns={0: "Description",1: "Value"})
    # Parse df into html format
    facts_df=facts_df.to_html(classes='table table-striped')


    #-------Mars Hemispheres--------

    # URL of page to be scraped
    url_hemispheres = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    # Retrieve page with the requests module
    response_hemispheres = requests.get(url_hemispheres)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response_hemispheres.text, 'html.parser')

    # Collect all the hemisphere titles
    conts=soup.find_all('div',class_="description")

    # Manipulate conts to derive hemisphere titles
    hemispheres=[]
    for cont in conts:
        a=cont.h3.text
        a=a[:-9]
        hemispheres.append(a)

    # URL of full image pages to be scraped
    url_ce='https://astrogeology.usgs.gov/search/map/Mars/Viking/cerberus_enhanced'
    url_sc='https://astrogeology.usgs.gov/search/map/Mars/Viking/schiaparelli_enhanced'
    url_sy='https://astrogeology.usgs.gov/search/map/Mars/Viking/syrtis_major_enhanced'
    url_va='https://astrogeology.usgs.gov/search/map/Mars/Viking/valles_marineris_enhanced'

    # Retrieve page with the requests module
    response_ce = requests.get(url_ce)
    response_sc = requests.get(url_sc)
    response_sy = requests.get(url_sy)
    response_va = requests.get(url_va)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup_ce = BeautifulSoup(response_ce.text, 'html.parser')
    soup_sc = BeautifulSoup(response_sc.text, 'html.parser')
    soup_sy = BeautifulSoup(response_sy.text, 'html.parser')
    soup_va = BeautifulSoup(response_va.text, 'html.parser')

    # Collect, manipulate and  append empty list of images with url of different hemispheres
    images=[]
    images.append(('https://astrogeology.usgs.gov')+(soup_ce.find('img',class_="wide-image").get('src')))
    images.append(('https://astrogeology.usgs.gov')+(soup_sc.find('img',class_="wide-image").get('src')))
    images.append(('https://astrogeology.usgs.gov')+(soup_sy.find('img',class_="wide-image").get('src')))
    images.append(('https://astrogeology.usgs.gov')+(soup_va.find('img',class_="wide-image").get('src')))

    # Form a dictionary with hemisphere titles and images
    hemisphere_images_urls= [{"title":hemispheres[0],"image_url":images[0]}, {"title":hemispheres[1],"image_url":images[1]}, {"title":hemispheres[2],"image_url":images[2]},{"title":hemispheres[3],"image_url":images[3]}]




    # Store all Mars data in a dictionary
    scrape_data={
        "News": news_title,
        "News_paragraph": news_p,
        "Featured_image_url": featured_image_url,
        "Weather": mars_weather,
        "Mars_facts": facts_df,
        "hemispheres_url": hemisphere_images_urls
    }
    
  

    # Insert the dictionary into Mongo
    collection.insert(scrape_data)
    # Return results
    return scrape_data

