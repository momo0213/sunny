"""
============================
Author:周振全
Time:2020/2/23 10:42 下午
E-mail:17764509133@163.com
============================
"""

"""封装颜色"""

from colorama import Fore, Back


class Colour(object):

    def white_green(self, s):
        return Fore.BLACK + Back.GREEN + s + Fore.RESET + Back.RESET

    def white_red(self, s):
        return Fore.BLACK + Back.RED + s + Fore.RESET + Back.RESET


color = Colour()
