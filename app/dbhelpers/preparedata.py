#!/usr/bin/env python

"""
Script for inserting data into database.
"""

from insert import insertImages

if __name__ == '__main__':
    insertImages('../outputs/images_data.txt', 'FoodAdvisor', 'images')