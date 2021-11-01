from django import template

register = template.Library()

def get_item(dictionary, key):
    return dictionary.get(key)