# -*- coding: utf-8 -*-
# @Time    : 2018/6/28 10:03
# @Author  : Bob Zou
# @Mail    : bob_zou@trendmicro.com
# @File    : player
# @Software: PyCharm
# @Function:

import json
import sys
import os
import time
import hashlib

from deuces import Card
import poker_deuces
from websocket import create_connection
from websocket._exceptions import WebSocketTimeoutException

# 默认计算胜率采样次数
SAMPLE_COUNT = 5000

# 自己位置的得分
UTG = 1
MP = 2
CO = 3
BTN = 4
SB = 5
BB = 6


MY_SITE = None
HAND_CARDS = []
BOARD_CARDS = []
MINBET = None

# 服务器地址
TM_SERVER="ws://poker-dev.wrs.club:3001"


def get_my_site(data):
    small_blind = data['table']['smallBlind']['playerName']
    big_blind = data['table']['bigBlind']['playerName']

    players = data['players']

    small_index = None
    for i, player in enumerate(players):
        if player['playerName'] == small_blind:
            small_index = i
            break

    if small_index == 0:
        pass
    elif small_index > 0:
        players = players[small_index:] + players[:small_index]

    my_index = None
    for i, player in enumerate(players):
        if player['playerName'] == name_md5:
            my_index = i
            break

    return my_index + 1, len(players)


def take_action(ws, event_name, data):
    global MY_SITE
    global HAND_CARDS
    global BOARD_CARDS
    global MINBET
    if event_name in ["__game_prepare", "__game_start"]:
        pass
    elif event_name == "__new_round":
        my_site, online_player_number = get_my_site(data)
        hand_cards = [player for player in data['players'] if player['playerName'] == name_md5][0]['cards']
        HAND_CARDS = [Card.new('{}{}'.format(hand_card[0], str.lower(hand_card[-1]))) for hand_card in hand_cards]
        if my_site == 1:
            MY_SITE = SB
            return
        elif my_site == 2:
            MY_SITE = BB
            return
        elif online_player_number >= 8:
            if my_site <= 4:
                MY_SITE = UTG
                return
            if online_player_number - my_site >= 2:
                MY_SITE = MP
                return
            if online_player_number - my_site >= 1:
                MY_SITE = CO
                return
            else:
                MY_SITE = BTN
                return
        else:
            if my_site <= 3:
                MY_SITE = UTG
                return
            if online_player_number - my_site >= 2:
                MY_SITE = MP
                return

            if online_player_number - my_site >= 1:
                MY_SITE = CO
                return
            else:
                MY_SITE = BTN
                return

    elif event_name == "__bet":
        BOARD_CARDS = [Card.new('{}{}'.format(card[0], str.lower(card[-1]))) for card in data['game']['board']]
        MINBET = data['self']['minBet']
        Card.print_pretty_cards(HAND_CARDS + BOARD_CARDS)
        win_prob = poker_deuces.calculate_winning_probability(HAND_CARDS, BOARD_CARDS, len(
            [player for player in data['game']['players'] if not player['folded']]), SAMPLE_COUNT)
        print('my winning probability: {}%'.format(win_prob * 100))

        ws.send(json.dumps({
            "eventName": "__action",
            "data": {
                "action": "bet"
            }
        }))
    elif event_name == "__action":
        BOARD_CARDS = [Card.new('{}{}'.format(card[0], str.lower(card[-1]))) for card in data['game']['board']]
        MINBET = data['self']['minBet']
        Card.print_pretty_cards(HAND_CARDS + BOARD_CARDS)
        win_prob = poker_deuces.calculate_winning_probability(HAND_CARDS, BOARD_CARDS, len([player for player in  data['game']['players'] if not player['folded']]), SAMPLE_COUNT)
        print('my winning probability: {}%'.format(win_prob * 100))

        ws.send(json.dumps({
            "eventName": "__action",
            "data": {
                "action": "call"
            }
        }))
    elif event_name == "__show_action":
        BOARD_CARDS = [Card.new('{}{}'.format(card[0], str.lower(card[-1]))) for card in data['table']['board']]
        # MINBET = data['action']['amount']
        win_prob = poker_deuces.calculate_winning_probability(HAND_CARDS, BOARD_CARDS, len(
            [player for player in data['players'] if not player['folded']]), SAMPLE_COUNT)
        Card.print_pretty_cards(HAND_CARDS + BOARD_CARDS)
        print('my winning probability: {}%'.format(win_prob * 100))
    elif event_name == "__round_end":
        MY_SITE = None
        MINBET = None
        HAND_CARDS = []
        BOARD_CARDS = []

        print('Round End')
    elif event_name == "__game_over":
        print('Game Over')
        os._exit(0)
    else:
        pass


def do_listen(player_name):
    try:
        ws = create_connection(TM_SERVER)

        # Join Game
        ws.send(json.dumps({
            "eventName": "__join",
            "data": {
                "playerName": player_name,
            }
        }))

        # wait for msg and take action
        while True:
            try:
                result = ws.recv()
                if len(result) == 0:
                    print(
                        "{} loss connection for recv zero buffer".format(player_name))
                    time.sleep(10)
                    continue
            except WebSocketTimeoutException:
                print("{} loss connection for timeout.".format(player_name))
                time.sleep(10)
                continue

            msg = json.loads(result)
            event_name = msg["eventName"]
            data = msg["data"]
            # print(event_name)
            # pprint.pprint(data)
            take_action(ws, event_name, data)
    except Exception as e:
        print(str(e))
        do_listen(player_name)


if __name__ == '__main__':
    name_md5 = hashlib.md5(sys.argv[1].encode('utf-8')).hexdigest()
    print(name_md5)
    do_listen(sys.argv[1])