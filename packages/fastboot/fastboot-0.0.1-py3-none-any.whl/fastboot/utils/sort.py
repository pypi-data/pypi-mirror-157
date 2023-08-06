from datetime import datetime
from random import randrange, uniform

import time


class MergeSort:

    def __init__(self, list):
        self.list = list

    def accept_one(self, ):
        pass


class Sort:
    ACCEPT_FIRST = 1
    ACCEPT_SECOND = 2
    ACCEPT_ALL = 0

    @staticmethod
    def comparar(lista_a, lista_b, callback):
        nova_lista = []

        index_a = 0
        index_b = 0
        len_lista_a = len(lista_a)
        len_lista_b = len(lista_b)
        index_a_acabou = len_lista_a <= index_a
        index_b_acabou = len_lista_b <= index_b

        while (not (index_a_acabou and index_b_acabou)):

            value_a = None

            if not index_a_acabou:
                value_a = lista_a[index_a]

            value_b = None
            if not index_b_acabou:
                value_b = lista_b[index_b]

            try:

                if index_a_acabou:
                    nova_lista.append(value_b)
                    index_b += 1
                elif index_b_acabou:
                    nova_lista.append(value_a)
                    index_a += 1


                else:
                    value = callback(value_a, value_b)
                    if Sort.ACCEPT_ALL == value:
                        nova_lista.append(value_a)
                        index_a += 1
                        nova_lista.append(value_b)
                        index_b += 1
                    elif Sort.ACCEPT_FIRST == value:
                        nova_lista.append(value_a)
                        index_a += 1
                    elif Sort.ACCEPT_SECOND == value:
                        nova_lista.append(value_b)
                        index_b += 1
            except Exception as e:
                print(e)
            index_a_acabou = len_lista_a <= index_a
            index_b_acabou = len_lista_b <= index_b
        return nova_lista

    @staticmethod
    def mergeSort(lista, callback):
        list = []
        for value in lista:
            list.append([value])
        qtd = len(list)

        while qtd != 1:
            new_list = []
            qtd_anteriror = qtd
            qtd = 0
            for start in range(0, qtd_anteriror, 2):
                end = start + 1
                lista_a = list[start]
                lista_b = []
                if not end >= qtd_anteriror:
                    lista_b = list[end]
                new_list.append(Sort.comparar(lista_a, lista_b, callback))
                qtd += 1
            list = new_list

        return list[0]


