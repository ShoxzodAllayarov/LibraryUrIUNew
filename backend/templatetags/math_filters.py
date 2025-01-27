from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """ Умножает значение на аргумент """
    return int(value) * int(arg)

@register.filter
def divisibleby(value, arg):
    """ Делит значение на аргумент """
    return int(value) // int(arg)

@register.filter
def minus(value, arg):
    """ Вычитает arg из value """
    return -int(value) + int(arg)
