# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 16:20
# @Author  : Bob Zou
# @Mail    : bob_zou@trendmicro.com
# @File    : poker-deuces
# @Software: PyCharm
# @Function:


# from deuces import Card
from deuces import Evaluator
from deuces import Deck

evaluator = Evaluator()


def calculate_winning_probability(hand, borad, player_num, count):
    '''
    通过已知手牌、桌牌、玩家数，模拟发牌，计算自己赢的次数
    :param hand: 玩家手牌
    :param borad: 已知桌面牌，没有则输入 []
    :param player_num: 玩家总数，包括自己
    :param count: 需要采集的样本数量
    :return: 胜率
    '''

    # 默认胜率为0
    win = 0

    for i in range(count):
        if is_win(hand, borad, player_num):
            win += 1

    return round(win * 1.0 / count, 2)


def is_win(hand, board, player_num):
    '''
    模拟一局游戏，判断自己是否获胜
    :param hand:
    :param board:
    :param player_num:
    :return: True or False
    '''

    # 生产一副新牌
    deck = Deck()
    # 去除目前自己的手牌
    deck.cards.remove(hand[0])
    deck.cards.remove(hand[1])

    # 去除目前已知桌牌
    for board_card in board:
        deck.cards.remove(board_card)

    # 随机获取剩余桌牌
    new_board_cards = deck.draw(5 - len(board))

    # 如果 （5 - len(board)） 等于 1，那么取出的会是一个int
    if type(new_board_cards) == int:
        new_board_cards = [new_board_cards]

    # 5 张桌面牌
    draw_board = board + new_board_cards

    # 计算自己牌的大小，值越小牌越好
    my_cards_evaluate = evaluator.evaluate(draw_board, hand)
    # 最大值是7432
    other_cards_evaluate = 10000
    for i in range(player_num - 1):
        # 为其他玩家随机发两张牌
        player_cards = deck.draw(2)

        # 机器玩家牌的大小
        random_other_cards_evaluate = evaluator.evaluate(draw_board, player_cards)

        # 更新其他玩家最大牌
        if random_other_cards_evaluate < other_cards_evaluate:
            other_cards_evaluate = random_other_cards_evaluate

        # 如果已有一个玩家的牌大于自己，判断自己输
        if other_cards_evaluate < my_cards_evaluate:
            return False

    # 没有玩家牌大于自己，判定自己赢
    return True