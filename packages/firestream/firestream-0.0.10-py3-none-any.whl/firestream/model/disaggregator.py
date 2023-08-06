#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 23:59:01 2022

@author: Mohammad Asim
"""
from tensorflow.keras import Model, Input
from tensorflow.keras.layers import concatenate

class Disaggregator():
    
    def __init__(self, name, stream, model, optimizer):
        
        """
            Initialize disaggregator
        """
        self.name = name
        self.model = model
        self.concat = concatenate
        self.stream = stream
        self.history = []
        self.optimizer = optimizer
        self.appliances = self.stream.config['appliances']
        
    def build(self):
        
        """
            Build disaggregator model
        """
        
        input_node = Input((self.stream.window_length, self.stream.input_width))
        collec = [self.model(self.name+'_'+str(i), self.stream.window_length, self.stream.input_width)(input_node) for i in range(len(self.appliances))]
        concat = concatenate(collec)
        self.model = Model(inputs=[input_node], outputs=concat)
        self.model.compile(loss=self.stream.loss, optimizer=self.optimizer)
    
    def train(self):

        """
            Function to starting training 
        """
        
        self.history = self.model.fit(self.stream.train_dataset, validation_data=self.stream.validation_dataset, epochs=self.stream.epochs)
