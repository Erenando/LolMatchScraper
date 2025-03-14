import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def get_ingame_names(match_url):
    # Setup headless Chrome
    options = Options()
    options.headless = True  # Run browser in headless mode (no GUI)
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(match_url)
        time.sleep(3)  # Wait for JavaScript to load fully

        # Extract fully rendered HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all player names
        ingame_names = []
        for div in soup.find_all("div", class_="txt-info"):
            name = div.text.strip()
            if "#" in name and name not in ingame_names:
                ingame_names.append(name)

        driver.quit()  # Close browser

        if len(ingame_names) < 10:
            print("Could not find 10 in-game names.")
            return

        # Split into two teams
        team1 = ingame_names[:5]
        team2 = ingame_names[5:]

        # Create OP.GG links
        team1_url = "https://www.op.gg/multisearch/euw?summoners=" + ",".join(
            [urllib.parse.quote(name) for name in team1])
        team2_url = "https://www.op.gg/multisearch/euw?summoners=" + ",".join(
            [urllib.parse.quote(name) for name in team2])

        print("Team 1 OP.GG Link:\n", team1_url)
        for player in team1:
            print(player)
        print("\nTeam 2 OP.GG Link:\n", team2_url)
        for player in team2:
            print(player)

    except Exception as e:
        print("Error:", e)
    finally:
        driver.quit()


# Example usage
match_url = "https://www.primeleague.gg/de/leagues/matches/1136675-anyera-esports-vs-whalepower-dolphins"
get_ingame_names(match_url)

def wait_for_input():
    while True:
        match_url = input("Bitte gib den Prime League Match-Link ein (oder 'e' zum Beenden): ")
        if match_url.lower() == 'e':
            print("Programm beendet.")
            break
        get_ingame_names(match_url)


# Run the function
wait_for_input()