#!/usr/bin/env python3 v1.0
# -*- coding: utf-8 -*-
"""
@author: jonathan t lee - https://github.com/jontaklee
"""

from random import shuffle

class MagicCard:
    
   def __init__(self, name, cmc, card_type, color):
       self.name = name
       self.cmc = cmc
       self.card_type = card_type
       self.color = color
       
class Land(MagicCard):
    
    def __init__(self, name, basic, col_mana):
        self.name = name
        self.basic = basic
        self.col_mana = col_mana
        MagicCard.__init__(self, name, 0, 'land', '')
    
    def play(self, hand, bfield):
        bfield.append(self)
        hand.pop(hand.index(self))

class Deck:
    
    def __init__(self, decklist):
        self.deck = decklist
    
    def shuffle(self):
        for i in range(0,5):
            shuffle(self.deck)
    
    # draw opening hand
    def draw_opener(self, handsize):
        self.shuffle()
        hand = self.deck[:handsize]
        #del self.deck[:handsize]
        return hand
    
    def draw(self, hand):
        hand.append(self.deck[0])
        self.deck.pop(0)
    
    def scry_bottom(self):
        self.deck.append(self.deck[0])
        del self.deck[0]    