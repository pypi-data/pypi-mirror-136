#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 23:50:25 2022

@author: Mohammad Asim
"""

from firestream.stream import Input
from firestream.model import Disaggregator

class Runner():
    
    def __init__(self, config):
       
        """
            Initialize Runner
        """
        
        self.config = config
        self.models = config['models'] if 'models' in config.keys() else None
        self.appliances = config['appliances']
        self.optimizers = config['optimizers']
        self.disaggregators = []

    def run(self):
        
        """
            Runner script
        """
        
        for optimizer in self.optimizers:
            
            print('Optimizer: ', optimizer)
            print('======================\n')
            
            for obj in self.models:
            
                print('Model: ', obj['model'].name)
                print('----------------------')
                stream = Input(self.config, obj['window_length'])
                stream.build()
                model = obj['model']
                disaggregator = Disaggregator(obj['name'], stream, model, optimizer)
                disaggregator.build()
                disaggregator.train()
                self.disaggregators.append(disaggregator)
                