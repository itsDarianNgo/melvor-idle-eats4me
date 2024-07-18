import logging
import time

def monitor_health_and_heal(driver):
	while True:
		try:
			# Retrieve player and enemy base stats
			player_current_hp = driver.execute_script("return game.combat.player.stats.character.hitpoints;")
			player_max_hp = driver.execute_script("return game.combat.player.stats._maxHitpoints;")
			enemy_max_hit = driver.execute_script("return game.combat.enemy.stats.maxHit;")

			# Fetch status of effects
			is_sleep = driver.execute_script("return game.combat.player.activeEffectGroups.get('melvorD:Sleep') === 1;")
			is_stun = driver.execute_script("return game.combat.player.activeEffectGroups.get('melvorD:StunLike') === 1;")
			is_freeze = driver.execute_script("return game.combat.player.activeEffectGroups.get('melvorD:Freeze') === 1;")

			# Calculate additional damage modifiers based on active effects
			effect_modifier = 1.0 + (0.20 if is_sleep else 0) + (0.30 if is_stun or is_freeze else 0)

			# Calculate enhanced enemy max hit considering normal effects
			enhanced_enemy_max_hit = enemy_max_hit * effect_modifier

			# Retrieve and calculate max hit from special attacks
			special_attacks = driver.execute_script("return game.combat.enemy.availableAttacks.map(attack => attack.attack.descriptionTemplateData.attackDamageMaxValue0 || '0');")
			max_special_attack_damage = max(int(damage) for damage in special_attacks) * effect_modifier

			# Apply damage reduction
			damage_reduction_map = driver.execute_script('''
                return Array.from(game.combat.player.stats._resistances).map(
                    entry => ({ key: entry[0]['_localID'], value: entry[1] })
                );
            ''')
			damage_reduction = next((entry['value'] for entry in damage_reduction_map if entry['key'] == 'Normal'), 0)

			final_enemy_max_hit = max(enhanced_enemy_max_hit, max_special_attack_damage) * (1 - damage_reduction / 100)

			logging.info(f"Player Current HP: {player_current_hp}, Player Max HP: {player_max_hp}, Effective Enemy Max Hit: {final_enemy_max_hit}")

			# Heal if necessary
			if final_enemy_max_hit >= player_current_hp:
				logging.info("Healing required! Initiating healing...")
				heal_player(driver, player_max_hp, player_current_hp)
			else:
				logging.info("No immediate healing needed.")

			time.sleep(0.5)  # Check interval

		except Exception as e:
			logging.error(f"An error occurred during health monitoring and healing: {str(e)}")
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