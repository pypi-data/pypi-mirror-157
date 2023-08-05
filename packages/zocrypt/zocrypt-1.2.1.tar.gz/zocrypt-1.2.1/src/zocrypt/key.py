import random
import os
alphabet='abcdefghijklm nopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%&*()-_+="\';:<>,.?{}[]'


def generate():  # needed only while making new key
        alphabet='abcdefghijklm nopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%&*()-_+="\';:<>,.?{}[]'
        alphabet = list(alphabet)
        random.shuffle(alphabet)
        return ''.join(alphabet) #then store this in a safe place for example environment variable

#print(generate())
