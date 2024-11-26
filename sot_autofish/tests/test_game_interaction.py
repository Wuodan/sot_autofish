""" Testing game_interaction """
import time

from sot_autofish.game_interaction import GameInteraction


def equip_fishing_rod(game: GameInteraction):
    """equip fishing rod"""
    game.hold_key('q')
    game.press_key('f')
    game.press_key('5')
    game.release_key('q')


def unequip(game: GameInteraction):
    """unequip, drop whatever is in hands"""
    game.press_key('x')



# try:
GLOBAL_LOG_LEVEL='INFO'

my_game = GameInteraction(game_title="Sea of Thieves")
time.sleep(5)
equip_fishing_rod(my_game)
time.sleep(10)
unequip(my_game)

# game.release_key('q')
# time.sleep(2)
# game.hold_key('f')
# game.hold_key('5')
# time.sleep(1)
# game.reset_keys()
# game.press_key('q')
# time.sleep(2)
# game.hold_key('q')
# time.sleep(2)
# game.release_key('f')
# time.sleep(2)
# game.hold_key('q')
# time.sleep(2)
# game.hold_key('f')
# time.sleep(2)
# game.hold_key('5')
# time.sleep(2)
# game.reset_keys()
# time.sleep(2)
# game.left_click()
# time.sleep(2)
# game.right_click()
# time.sleep(2)
# except GameWindowError as e:
#     print(f"Error: {e}")
# except Exception as e:
#     print(f"Unexpected error: {e}")
