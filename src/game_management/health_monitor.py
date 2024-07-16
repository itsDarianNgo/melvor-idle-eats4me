import logging
import time


def monitor_health_and_heal(driver):
	while True:
		try:
			player_current_hp = driver.execute_script("return game.combat.player.stats.character.hitpoints;")
			player_max_hp = driver.execute_script("return game.combat.player.stats._maxHitpoints;")
			enemy_max_hit = driver.execute_script("return game.combat.enemy.stats.maxHit;")

			# Fetch the entries from resistances Map
			damage_reduction_map = driver.execute_script(

				'''return Array.from(game.combat.player.stats._resistances).map(
                entry => ({ key: entry[0]['_localID'], value: entry[1] })
            );'''
			)

			damage_reduction = 0
			# Find the 'Normal' damage reduction value
			for entry in damage_reduction_map:
				if entry['key'] == 'Normal':
					damage_reduction = entry['value']
					break

			effective_enemy_max_hit = enemy_max_hit * (1 - damage_reduction / 100)
			logging.info(f"Player Current HP: {player_current_hp}, Player Max HP: {player_max_hp}")
			logging.info(f"Effective Enemy Max Hit: {effective_enemy_max_hit}")

			if effective_enemy_max_hit >= player_current_hp:
				logging.info("Healing required! Initiating healing...")
				heal_player(driver, player_max_hp, player_current_hp)
			else:
				logging.info("No immediate healing needed.")

			time.sleep(2)  # Polling interval

		except Exception as e:
			logging.error(f"An error occurred during health monitoring and healing: {e}")
			break


def heal_player(driver, player_max_hp, player_current_hp):
	"""
	Execute the healing action using in-game food resources from slot 1.
	"""
	food_healing_value = driver.execute_script("return game.combat.player.stats.character.food.slots[0].item.healsFor;")
	actual_healing_amount = food_healing_value * 100
	needed_food_count = (player_max_hp - player_current_hp) // actual_healing_amount + 1

	driver.execute_script("game.combat.player.stats.character.selectFood(0);")
	driver.execute_script(f"game.combat.player.stats.character.eatFood({needed_food_count});")
	logging.info(f"Player healed using {needed_food_count} items from Food Slot 1, each healing for {actual_healing_amount}.")