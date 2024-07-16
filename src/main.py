import os
import sys
import logging
import time
from selenium import webdriver

from game_management.health_monitor import monitor_health_and_heal

# Adding the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_management.browser_init import setup_browser
from browser_management.character_select import select_character
from browser_management.login import login
from browser_management.navigate import navigate_to_homepage
# from game_management.health_monitor import monitor_health
from utils.game_state import check_game_ready
from config.settings import GAME_URL, USERNAME, PASSWORD, CHARACTER_NAME


def main():
	logging.basicConfig(level=logging.INFO)
	driver = None

	try:
		driver = setup_browser()
		navigate_to_homepage(driver, GAME_URL)
		login(driver, USERNAME, PASSWORD)
		select_character(driver, CHARACTER_NAME)

		if check_game_ready(driver):
			logging.info("Game Loaded. Beginning health monitoring and potential healing.")
			monitor_health_and_heal(driver)
			# Loop to keep session open, press CTRL+C in terminal or stop the script to exit
			while True:
				time.sleep(10)  # Sleeps 10 seconds before next loop, making it less resource-intensive
		else:
			logging.error("Game is not ready. Please check the steps or configurations.")

	except KeyboardInterrupt:
		logging.info("Shutdown requested by user.")
	except Exception as e:
		logging.error(f"An error occurred: {e}")
	finally:
		if driver:
			logging.info("Closing the game driver.")
			driver.quit()


if __name__ == "__main__":
	main()