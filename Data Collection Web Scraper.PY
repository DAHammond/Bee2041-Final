#install the required packages - this may not be required if the code has been run before, however I needed to the first time.
!pip install selenium
!pip install webdriver-manager

# selenium is used instead of beautiful soup because of the nature of the website. Beautifulsoup wouks well with static webpages however, we need to click through dynamic webpages to access the final data in our project, therefore Selenium is a better selection.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

# Define the range of match IDs to scrape
## Go onto the understat website and click onto the first and last games in the desired season. Look in the URL bar for the IDs (the digits at the end of the url). This stage simplifies the automation process by not requiring us to write code to interact and loop through the first display pages.
start_match_id = 18202
end_match_id = 18581

# Set up the Selenium WebDriver - this allows us to interact with the internet in the google chrome environment and is important as we will need to click through a page on the website
service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=service)

# Data container for all matches that will then be transformed into a CSV when all data has been collected
all_match_data = []

# Looping through all of the desired matches and their unique URLs, iterating through match IDs
## This is the loop that contains all of the scraping for each individual url page (match) and returns the data to the data container all_match_data
for match_id in range(start_match_id, end_match_id + 1):
    url = f"https://understat.com/match/{match_id}"
    browser.get(url)

    # Add a delay to ensure that the web-page has loaded completely
    time.sleep(2)

    # Now find and click the 'Stats' button if it exists (which it should). This can be found by looking into and analysing the source code to be able to put it into this python scipt. To reiterate, the information we want is hidden behind a click menu.
    try:
        stats_button = browser.find_element(By.XPATH, "//label[@for='scheme3']")
        stats_button.click()
        time.sleep(1)  # Delay required to ensure the stats page has completely loaded
    except Exception as e:
        print(f"Could not find stats button for match ID {match_id}: {e}")
        continue # this should not be an issue however for robustness, this message will be printed into the terminal

    # Extract the stats data - available now that we are in the right place
    match_data = {'match_id': match_id}
    stats_elements = browser.find_elements(By.CLASS_NAME, 'progress-bar')

    for stat in stats_elements:
        title_element = stat.find_element(By.CLASS_NAME, 'progress-title')
        title = title_element.text

        if title in ['TEAMS', 'GOALS', 'xG']: #using a list and conditional function so that we can just add different variables available on the webpage into this list at a later date without having to edit any more code.
            home_stat = stat.find_element(By.CLASS_NAME, 'progress-home').text
            away_stat = stat.find_element(By.CLASS_NAME, 'progress-away').text

            match_data[f'{title.lower()}_home'] = home_stat
            match_data[f'{title.lower()}_away'] = away_stat

    all_match_data.append(match_data) # adding the code from that specific URL into the data container so that it can be added to the csv file in the next stage when the webscraping is complete.

# Close the browser when all URL's have been scraped
browser.quit()

# Write data to CSV file so that it can be analysed later - this will store in the same directory as this .PY file
with open('EPL_2022-2023_match_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['match_id', 'teams_home', 'teams_away', 'goals_home', 'goals_away', 'xg_home', 'xg_away']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for match in all_match_data:
        writer.writerow(match)

print("Data extraction complete without faults. CSV file has been written.")

# As a check for this code having been successful, open the csv file. There should be seven colums with 380 games in the 2022-23 Premier League Season. The number of games will change if you change the league for which the data is being scraped.