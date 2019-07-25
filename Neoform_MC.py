#!/usr/bin/env python3 v3.1
# -*- coding: utf-8 -*-
"""
@author: jonathan t lee - https://github.com/jontaklee
"""

import csv
from itertools import combinations 
import numpy as np

import card_classes as cc

## assemble a table of cards used in the deck
def card_dict():
    
    lands = set(['Breeding Pool', 'Botanical Sanctum', 'Gemstone Mine', 
                 'Waterlogged Grove', 'Yavimaya Coast', 'Island'])
    tbl = {}
    with open('neobrand_cards.csv', 'r') as neocards:
        reader = csv.reader(neocards, delimiter=',')
        for row in reader:
            if row[0] in lands:
                tbl[row[0]] = cc.Land(row[0], int(row[1]), row[2])
            else:
                tbl[row[0]] = cc.MagicCard(row[0], int(row[1]), row[2], row[3])
    
    return tbl

## generate a decklist from a MTGO formatted text file
def assemble_decklist(card_dict, decklist):
    
    outlist = []
    with open(decklist, 'r') as decklist:
        for row in decklist:   
            row = row.strip()
            
            # break before the sideboard
            if not row: break
            
            row = row.split(' ', 1)
            count = 1
            while count <= int(row[0]):
                outlist.append(card_dict[row[1]])
                count += 1
    
    return outlist

## searchees for allosaurus rider/pact and neoform/evolution in hand
def rider_and_tutor(hand_dict):
    
    has_rider = 'Allosaurus Rider' in hand_dict or "Summoner's Pact" in hand_dict
    has_tutor = 'Eldritch Evolution' in hand_dict or 'Neoform' in hand_dict
    return True if has_rider and has_tutor else False

## check if hand contains a land
def land_check(hand_dict):
    
    all_lands = set(['Breeding Pool', 'Botanical Sanctum', 'Gemstone Mine', 
                 'Waterlogged Grove', 'Yavimaya Coast', 'Island'])
    hand_lands = all_lands.intersection(hand_dict)

    if hand_lands == set(['Island']): return 1
    return 2 if hand_lands else False

## check if hand has mana to cast neoform
def try_neoform(hand_dict):
    
    land_flag = land_check(hand_dict)
    tangle_count = hand_dict.get('Chancellor of the Tangle', 0)
    ssg_count = hand_dict.get('Simian Spirit Guide', 0)
    filter_count = hand_dict.get('Manamorphose', 0) + hand_dict.get(
            'Wild Cantor', 0)
    has_quest = hand_dict.get('Safewright Quest', 0)
    
    # ug land + tangle
    if land_flag and tangle_count:
        return 1
    
    # land + ssg + manamorphose/cantor
    if land_flag and ssg_count and filter_count:
        return 2
    
    # 2 tangle and/or ssg + manamorphose/cantor
    if tangle_count + ssg_count >= 2 and filter_count:
        return 2
    
    # 2 tangle + safewright quest
    if tangle_count >= 2 and has_quest:
        return 3
    
    # note: spending 2 ssg is acceptable because a land drop can be made later
    
    return False

def try_evolution(hand_dict):
    
    land_flag = land_check(hand_dict)
    tangle_count = hand_dict.get('Chancellor of the Tangle', 0)
    ssg_count = hand_dict.get('Simian Spirit Guide', 0)
    filter_count = hand_dict.get('Manamorphose', 0) + hand_dict.get(
            'Wild Cantor', 0)
    
    # land + 2 tangle, or 3 tangle
    if tangle_count >= 3:
        return 1
    
    # land + 2 tangle
    if land_flag and tangle_count >= 2:
        return 1
    
    # ug land + tangle + ssg
    if land_flag == 1 and tangle_count and ssg_count:
        return 1
    
    # island + tangle + ssg + color filter
    if land_flag == 2 and tangle_count and ssg_count and filter_count:
        return 2
    
    # 2 tangle + ssg
    if tangle_count == 2 and ssg_count:
        return 1
    
    # 1 tangle + 2 ssg + color filter
    if tangle_count == 1 and ssg_count >= 2 and filter_count:
        return 2
    
    # note: can't spend 2 ssg and a land, or 3 ssg

    return False

## check if 2 green cards available to discard to allosaurus rider
def count_green(hand, tutor, tutor_flag):
    
    ex_dict = {'Allosaurus Rider': set(['Allosaurus Rider', 'Summoners Pact']),
               'Summoners Pact': set(['Allosaurus Rider', 'Summoners Pact']),
                tutor: set([tutor])}
    
    # added if a color filter is required for the hand to function
    if tutor_flag == 2:
        ex_dict['Manamorphose'] = set(['Manamorphose', 'Wild Cantor'])
        ex_dict['Wild Cantor'] = set(['Manamorphose', 'Wild Cantor'])
    
    if tutor_flag == 3:
        ex_dict['Safewright Quest'] = set(['Safewright Quest'])
    
    green_count = 0
    for card in hand:
        if card.name in ex_dict:
            ex_dict = {cn:ex_dict[cn] for cn in set(ex_dict) - 
                       ex_dict[card.name]}
        elif card.color == 'G': green_count += 1
        else: continue
        
    return True if green_count >= 2 else False

## primary function to evaluate for turn 1 neoform
def eval_hand(hand):
    
    keep = False
    neoform_flag = False
    evolution_flag = False
    
    hand_dict = {}
    for card in hand:
        hand_dict[card.name] = hand_dict.get(card.name, 0) + 1
    
    # first check: check that both griselbrands aren't in hand
    if hand_dict.get('Griselbrand', 0) == 2:
        return False
    
    # second check: rider/pact + neoform/evolution
    if not rider_and_tutor(hand_dict):
        return False
    
    # third check: check for neoform mana
    if 'Neoform' in hand_dict:
        neoform_flag = try_neoform(hand_dict)
    
    # fourth check: check for evolution mana
    if 'Eldritch Evolution' in hand_dict:
        evolution_flag = try_evolution(hand_dict)
    
    # fifth check: green cards to cast rider
    if neoform_flag:
        keep = count_green(hand, 'Neoform', neoform_flag)
        if keep:
            return keep
        
    if evolution_flag: 
        keep = count_green(hand, 'Eldritch Evolution', evolution_flag)

    return keep

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

## perform simulation
def sim_with_mulligans(decklist):
    
    library = cc.Deck(decklist)
    mull_count = 0
    keep = False
    while not keep and mull_count <= 2:
        hand = library.draw_opener(7)
        keep = eval_mulligan(hand, mull_count)
        mull_count += 1
        
    return keep

## user inputs for decklist and number of simulations
def get_inputs():

    while 1:
        infile = input('import a decklist, or return for default list: ')
        if not infile:
            decklist = assemble_decklist(card_dict(), 'NeobrandDefaultList.txt')
            break
        try: decklist = assemble_decklist(card_dict(), infile)
        except: print('Invalid decklist. Must follow MTGO formatting.')
        else: break
    
    while 1:
        n = input('number of simulated hands: ')
        try: n = int(n)
        except: print('input must be a positive integer')
        else: break
    
    return decklist, n

def main():
    
    decklist, n = get_inputs()
    sims = [sim_with_mulligans(decklist) for x in range(n)]
    print('results: ' + str(sum(sims)) + ' turn 1 Griselbrands in ' 
          + str(n) + ' hands: ' 
          + str(round(np.mean(sims)*100, 2)) + '% success rate')

if __name__ == '__main__':
    main()