#!/usr/bin/env python3 v2.0
# -*- coding: utf-8 -*-
"""
Created on Fri May 3 14:23:22 2019

@author: jonathan
"""
from itertools import combinations 
import numpy as np
from random import shuffle

class MagicCard:
    
   def __init__(self, name, cmc, card_type, color):
       self.name = name
       self.cmc = cmc
       self.card_type = card_type
       self.color = color
       
# class to specify Land cards
class Land(MagicCard):
    
    def __init__(self, name, basic, col_mana):
        self.name = name
        self.basic = basic
        self.col_mana = col_mana
        MagicCard.__init__(self, name, 0, 'land', '')
    
    def play(self, hand, bfield):
        bfield.append(self)
        hand.pop(hand.index(self))

def decklist():
    
    # multicolor green cards are treated as G
    allosaurus = MagicCard('Allosaurus Rider', 7, 'creature', 'G')
    wurm = MagicCard('Autochthon Wurm', 15, 'creature', 'G') 
    griselbrand = MagicCard('Griselbrand', 8, 'creature', 'B')
    chancellor = MagicCard('Chancellor of the Tangle', 7, 'creature', 'G')
    cantor = MagicCard('Wild Cantor', 1, 'creature', 'G')
    spirit = MagicCard('Simian Spirit Guide', 3, 'creature', 'R')
    maniac = MagicCard('Laboratory Maniac', 3, 'creature', 'U')
        
    eldritch = MagicCard('Eldritch Evolution', 3, 'sorcery', 'G')
    neoform = MagicCard('Neoform', 2, 'sorcery', 'G')
    g_pact = MagicCard('Summoners Pact', 0, 'instant', 'G')
    u_pact = MagicCard('Pact of Negation', 0, 'instant', 'U')
    shoal = MagicCard('Nourishing Shoal', 2, 'instant', 'G')
    manamorphose = MagicCard('Manamorphose', 2, 'instant', 'G')
    #storm = MagicCard('Lightning Storm', 3, 'instant', 'R')
    visions = MagicCard('Serum Visions', 1, 'sorcery', 'U')
    revival = MagicCard('Noxious Revival', 1, 'sorcery', 'G')
    autumn = MagicCard('Edge of Autumn', 2, 'sorcery', 'G')
    lgo = MagicCard('Life Goes On', 1, 'instant', 'G')
    quest = MagicCard('Safewright Quest', 1, 'sorcery', 'G')

    pool = Land('Breeding Pool', False, 'UG')
    sanctum = Land('Botanical Sanctum', False, 'UG')
    gemstone = Land('Gemstone Mine', False, 'WUBRG')
    #yavimaya = Land('Yavimaya Coast', False, 'UG')
    grove = Land('Waterlogged Grove', False, 'UG')

    lands_4 = [sanctum, gemstone] * 4
    lands_3 = [grove] * 3
    lands_2 = [pool] * 2
    lands = lands_4 + lands_3 + lands_2

    quads = [allosaurus, chancellor, spirit, eldritch, neoform, g_pact, shoal,
         manamorphose, visions] * 4
    dups = [wurm, griselbrand] * 2
    singles = [cantor, maniac, revival, u_pact, lgo, quest, autumn]

    return lands + quads + dups + singles

class NeoDeck:
    
    def __init__(self):
        self.deck = decklist()
    
    def shuffle(self):
        for i in range(0,5):
            shuffle(self.deck)
    
    # draw opening hand
    def draw_opener(self, handsize):
        self.shuffle()
        hand = self.deck[:handsize]
        del self.deck[:handsize]
        return hand
    
    def draw(self, hand):
        hand.append(self.deck[0])
        self.deck.pop(0)
    
    def scry_bottom(self):
        self.deck.append(self.deck[0])
        del self.deck[0]    


## searchees for allosaurus rider/pact and neoform/evolution in hand
def rider_and_tutor(hand_dict):
    
    has_rider = 'Allosaurus Rider' in hand_dict or 'Summoners Pact' in hand_dict
    has_tutor = 'Eldritch Evolution' in hand_dict or 'Neoform' in hand_dict
    return True if has_rider and has_tutor else False

## check in hand contains a land
def land_check(hand):
    return 'land' in {card.card_type:0 for card in hand}

## check if hand has mana to cast neoform
def tryNeoform(hand, hand_dict):
    
    has_land = land_check(hand)
    tangle_count = hand_dict.get('Chancellor of the Tangle', 0)
    ssg_count = hand_dict.get('Simian Spirit Guide', 0)
    filter_count = hand_dict.get('Manamorphose', 0) + hand_dict.get(
            'Wild Cantor', 0)
    
    # ug land + tangle
    if has_land and tangle_count:
        return True
    
    # land + ssg + manamorphose/cantor
    if has_land and ssg_count and filter_count:
        return True
    
    # 2 tangle and/or ssg + manamorphose/cantor
    if tangle_count + ssg_count >= 2 and filter_count:
        return True
    
    # note: spending 2 ssg is acceptable because a land drop can be made later
    
    return False

def tryEvolution(hand, hand_dict):
    
    has_land = land_check(hand)
    tangle_count = hand_dict.get('Chancellor of the Tangle', 0)
    ssg_count = hand_dict.get('Simian Spirit Guide', 0)
    filter_count = hand_dict.get('Manamorphose', 0) + hand_dict.get(
            'Wild Cantor', 0)
    
    # land + 2 tangle, or 3 tangle
    if has_land + tangle_count >= 3:
        return True
    
    # land + tangle + ssg
    if has_land and tangle_count and ssg_count:
        return True
    
    # 2 tangle + ssg
    if tangle_count == 2 and ssg_count:
        return True
    
    # 1 tangle + 2 ssg + color filter
    if tangle_count == 1 and ssg_count >= 2 and filter_count:
        return True
    
    # note: can't spend 2 ssg and a land, or 3 ssg

    return False

## check if 2 green cards available to discard to allosaurus rider
def count_green(hand, hand_dict, tutor):
    
    # exclude the allosaurus rider as an option to discard
    hand_names = [card.name for card in hand]
    rm_indeces = []
    if 'Allosaurus Rider' in hand_dict:
        rm_indeces.append(hand_names.index('Allosaurus Rider'))
    else:
        rm_indeces.append(hand_names.index('Summoners Pact'))
    
    # exclude the tutor as an option to discard
    rm_indeces.append(hand_names.index(tutor))
    
    # count green cards
    # does not consider corner case where a color filter gets used up
    simp_hand = [card for i, card in enumerate(hand) if i not in rm_indeces]
    num_green = [card.color for card in simp_hand].count('G')
    return True if num_green >= 2 else False

## primary function to evaluate for turn 1 neoform
def eval_hand(hand):
    
    keep = False
    neoform = False
    evolution = False
    
    hand_dict = {}
    for card in hand:
        hand_dict[card.name] = hand_dict.get(card.name, 0) + 1
    
    # first check: rider/pact + neoform/evolution
    if not rider_and_tutor(hand_dict):
        return keep
    
    # second check: check for neoform mana
    if 'Neoform' in hand_dict:
        neoform = tryNeoform(hand, hand_dict)
    
    # third check: check for evolution mana
    if 'Eldritch Evolution' in hand_dict:
        evolution = tryEvolution(hand, hand_dict)
    
    # fourth check: green cards to cast rider
    if neoform:
        keep = count_green(hand, hand_dict, 'Neoform')
        if keep:
            return keep
        
    if evolution: 
        keep = count_green(hand, hand_dict, 'Eldritch Evolution')

    return keep

## perform simulation with 7 card hands
def simulate_hand():
    
    library = NeoDeck()
    hand = library.draw_opener(7)
    '''
    if on_draw:
        library.draw(hand)
    '''
    return eval_hand(hand)

## helper function to evaluate all hands resulting from a london mulligan
def eval_mulligan(hand, mull_count):
    
    handsize = 7 - mull_count
    subhands = list(combinations(hand, handsize))
    keep = False
    i = 0
    while not keep and i < len(subhands):
        keep = eval_hand(subhands[i])
        i += 1
        
    return keep

## perform simulation with mulligans turned on
def sim_with_mulligans():
    
    mull_count = 0
    keep = False
    while not keep and mull_count <= 2:
        library = NeoDeck()
        hand = library.draw_opener(7)
        keep = eval_mulligan(hand, mull_count)
        mull_count += 1
        
    return keep

def main():
    
    while 1:
        n = input('number of simulated hands: ')
        try: n = int(n)
        except: print('input must be a positive integer')
        else: break
    '''
    while 1:
        pd = input('on the play or on the draw? ').lower()
        pd_tbl = {'play': False, 'draw': True}
        if pd in pd_tbl:
            draw = pd_tbl[pd]
            break
        else: print("error: input must be 'play' or 'draw'")
    '''

    print('running simulations...')
    sims = [sim_with_mulligans() for x in range(n)]
    print('results: ' + str(sum(sims)) + ' turn 1 Griselbrands in ' 
          + str(n) + ' hands: ' 
          + str(round(np.mean(sims)*100, 2)) + '% success rate') 
   

if __name__ == '__main__':
    main()
    