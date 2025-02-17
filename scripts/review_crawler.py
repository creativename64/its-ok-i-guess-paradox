
import os
import json
import requests
import dataclasses
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from dataclasses import dataclass, field

@dataclass
class Review:
    body: str = ''
    recommended: bool = True
    play_time: float = -1
    funny_votes: int = -1

@dataclass
class Game:
    appid: int = -1
    name: str = ''
    reviews: list[Review] = field(default_factory=list)

driver = webdriver.Chrome(ChromeDriverManager().install())
appids = ['529340', '684450', '604540', '1158310', '718850', '637090', '464920', '572410', '616240', '362960', '384490', '281990', '233450', '238370', '255710', '205990', '226840', '236850', '227760', '266840', '1677280', '916440', '2109370', '1044720', '1121640', '826630', '466560', '779340', '1605220', '1029780', '32470', '289070', '905370', '8930', '1410710', '1124300', '1099410', '294100', '703080', '323190', '1455840', '975370', '1366540', '24780', '1466860', '1811990', '365360', '553540', '562810', '287450', '1651560', '1105420', '459220', '1385380', '1637320', '368260', '1997040', '1449850', '859580', '225420', ]

db = []

Path('headers/').mkdir(parents=True, exist_ok=True)

for i, appid in enumerate(appids):
    game = Game()

    # Navigate to the reviews page, sorted by funny
    reviews_page = f'https://steamcommunity.com/app/{appid}/reviews/?browsefilter=funny&filterLanguage=english'
    driver.get(reviews_page)

    # Do not proceed if the user was redirected.
    # This may happen when accessing non-store apps, like Source SDK and Spacewar or dedicated servers.
    if driver.current_url != reviews_page:
        print(f'❌ [{i+1}/{len(appids)}] {game.name} ({game.appid})')
        continue

    # Assign appid
    game.appid = appid
    
    try:
        # Age check might prompt, try to continue
        driver.find_element_by_id('age_gate_btn_continue').click()
        driver.find_element_by_xpath("//select[@name='ageYear']/option[text()='1900']").click()
    except NoSuchElementException:
        pass

    try:
        driver.find_element_by_xpath("//select[@name='ageYear']/option[text()='1900']").click()
        driver.find_element_by_css_selector('.btnv6_blue_hoverfade[href="#"]').click()
    except NoSuchElementException:
        pass

    # Find game name based on appid
    try:
        game.name = driver.find_element_by_class_name('apphub_AppName').text
    except NoSuchElementException:
        print(f'❌ [{i+1}/{len(appids)}] {game.name} ({game.appid})')
        continue

    # Delete a couple of elements so I can easily extract review text
    driver.execute_script("""
        let el1 = document.getElementsByClassName('date_posted');
        while (el1[0]) el1[0].parentNode.removeChild(el1[0]);

        let el2 = document.getElementsByClassName('early_access_review');
        while (el2[0]) el2[0].parentNode.removeChild(el2[0]);

        let el3 = document.getElementsByClassName('received_compensation');
        while (el3[0]) el3[0].parentNode.removeChild(el3[0]);

        let el4 = document.getElementsByClassName('refunded');
        while (el4[0]) el4[0].parentNode.removeChild(el4[0]);
    """)

    reviews = []

    for elem in driver.find_elements_by_class_name('apphub_UserReviewCardContent'):
        review = Review()

        # Filter out reviews that less than 150 people thought were funny
        try:
            funny_votes = elem.find_element_by_class_name('found_helpful').text
            review.funny_votes = int(funny_votes.split('\n')[1].split(' ')[0].replace(',', ''))

            if review.funny_votes < 25:
                continue
        except Exception:
            continue

        body = elem.find_element_by_css_selector('.apphub_CardTextContent').text

        if len(body) < 280:
            review.body = body
        else:
            continue

        review.recommended = elem.find_element_by_css_selector('.title').text == 'Recommended'

        try:
            play_time = float(elem.find_element_by_css_selector('.hours').text.split(' ')[0].replace(',', ''))
            review.play_time = play_time
        except NoSuchElementException:
            review.play_time = 0

        reviews.append(dataclasses.asdict(review))

    if len(reviews) >= 3:
        game.reviews = reviews
        db.append(dataclasses.asdict(game))
        
        # Download banner image
        with open(f'./headers/{appid}_header.jpg', 'wb') as file:
            res = requests.get(f'https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg')
            file.write(res.content)

        print(f'✔️  [{i+1}/{len(appids)}] {game.name} ({game.appid})'.encode('utf-8'))
    else:
        print(f'❌ [{i+1}/{len(appids)}] {game.name} ({game.appid})'.encode('utf-8'))

driver.close()

with open('reviews.json', 'w') as file:
    json_str = json.dumps(db, indent=2)
    file.write(json_str)
