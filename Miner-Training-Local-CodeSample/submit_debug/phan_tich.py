import json
import codecs

game = json.load(codecs.open('game_2.json', 'r', 'utf-8-sig'))
for step in game:
    print(step.keys())
    for player in step['players']:
        if player['status'] != 0:
            print(player)