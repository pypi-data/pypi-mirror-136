#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado: 	2022/01/01 20:23:55.455964
#+ Editado:	2022/01/29 17:51:50.619510
# ------------------------------------------------------------------------------
import requests as r
import pandas as pd
from bs4 import BeautifulSoup as bs
from math import ceil
from Levenshtein import distance
from time import time
import sqlite3
import sys
from typing import Optional, List, Union

from src.coinmarketcap_scrapper.excepcions import ErroTipado, ErroPaxinaInaccesibel
from src.coinmarketcap_scrapper.cmc_uteis import lazy_check_types
# ------------------------------------------------------------------------------
class CoinMarketCap:
    # atributos de clase
    __pax: int = 1
    __url: str = 'https://coinmarketcap.com'

    # Constructor --------------------------------------------------------------
    def __init__(self) -> None:
        # variables da instancia
        self.__pax = self.__pax
        self.__url = self.__url
    # --------------------------------------------------------------------------

    # Getters ------------------------------------------------------------------
    def get_pax(self) -> int:
        return self.__pax

    def get_url(self) -> str:
        return self.__url

    def get_con(self) -> None:
        return sqlite3.connect('./media/DB/ligazons.db')

    def get_url_pax(self, nova_pax: Optional[int] = 0) -> str:
        if nova_pax:
            self.__pax = nova_pax

        return self.__url+'/?page='+str(self.__pax)

    # --------------------------------------------------------------------------

    # Setters ------------------------------------------------------------------

    def set_pax(self, nova_pax) -> None:
        self.__pax = nova_pax

    # --------------------------------------------------------------------------

    # get_top
    def get_top(self, topx: Optional[int] = 10) -> List[dict]:
        """
        Devolve o top de moedas en CoinMarketCap.

        @entradas:
            topx    -   Opcional    -   Enteiro
            └ Cantidade de moedas no top.

        @saídas:
            Lista de dicionarios  -   Sempre
            └ Cos datos pedidos.
        """

        # se mete mal o tipo dos valores saca erro
        if not lazy_check_types(topx, int):
            raise ErroTipado('O tipo da variable non entra dentro do esperado (int)')

        pasados = 0
        pax = 1
        lista_top = []
        tope = topx

        #while pax<=ceil(topx/100):
        while True:
            try:
                pax_web = r.get(self.get_url_pax())

                if pax_web.status_code == 404:
                    raise ErroPaxinaInaccesibel

                #df = pd.read_html(r.get(pax_web.text)[0]
                soup = bs(pax_web.text, 'html.parser')
                taboa = soup.find('table').tbody.find_all('tr')

                xpax = len(taboa)
                if topx == 0:
                    tope = xpax

                # o tope fai que o programa sexa lixeiramente máis rápido
                # no caso de que non se requira o scrape de tódolos elementos
                # da páxina
                for indice, fila in enumerate(taboa[:tope], 1):
                    # simbolo
                    try:
                        simbolo = fila.find(class_='crypto-symbol').text
                    except:
                        try:
                            simbolo = fila.find(class_='coin-item-symbol').text
                        except Exception as e:
                            raise Exception(e)
                    # simbolo #

                    # ligazon
                    try:
                        ligazon = fila.find(class_='cmc-link').get('href')
                    except Exception as e:
                        raise Exception(e)
                    # ligazon #

                    # prezo
                    try:
                        prezo = fila.find_all('td')[3].text
                    except Exception as e:
                        raise Exception(e)
                    # prezo #

                    # divisa
                    try:
                        divisa = prezo[0]
                    except Exception as e:
                        raise Exception(e)
                    # divisa #

                    # prezo
                    try:
                        prezo = prezo[1:]
                    except Exception as e:
                        raise Exception(e)
                    # prezo #

                    # nome
                    try:
                        nome = fila.find_all('td')[2].text
                        if nome.endswith('Buy'):
                            nome = nome[:-3]

                        if nome.endswith(simbolo):
                            nome = nome[:-len(simbolo)]

                        # podería dar problema se fose algo tipo Moeda1 o nome
                        if not nome.isdigit():
                            while nome[-1].isdigit():
                                nome = nome[:-1]
                    except Exception as e:
                        raise Exception(e)
                    # nome #

                    lista_top.append({
                        'posicion': indice+pasados,
                        'simbolo': simbolo,
                        'nome': nome,
                        'prezo': prezo,
                        'divisa': divisa,
                        'ligazon': ligazon
                        })

                pax+=1
                pasados += xpax
                if topx != 0:
                    tope -= pasados

                # aki en lugar de no while pq asi podo sacar o xpax sen
                # outro request idiota ou recursión
                if (pax>ceil(topx/xpax)) and (topx!=0):
                    break
            # se peta saese do bucle
            except:
                break

        return lista_top

    # xFCRF devolve soamente usd, molaría para o futuro implementar outras
    # get_info
    def get_info(self, buscado: str, xvalor: Optional[str] = 'nome') -> dict:
        """
        Devolve toda a información posible sobre a moeda inquirida.

        @entradas:
            buscado -   Requirido   -   Catex
            └ Cadea de texto buscada.
            xvalor  -   Opcional    -   Catex
            └ Indica se quere que se busque como nome de moeda ou simbolo.

        @saídas:
            Dicionario  -   Sempre
            └ Con tódolos datos posibles.
        """

        # se mete mal o tipo dos valores saca erro
        if not lazy_check_types([buscado, xvalor], [str, str]):
            raise ErroTipado('O tipo da variable non entra dentro do esperado (int)')

        # se mete un campo raro busca por nome
        if xvalor not in ['nome', 'simbolo']:
            xvalor = 'nome'

        con = self.get_con()
        cur = con.cursor()

        buscado_sentenza = '%'.join(list(buscado))
        sentenza = f'select id, {xvalor} from moeda where {xvalor} like "%{buscado_sentenza}%"'
        busqueda = cur.execute(sentenza).fetchall()

        # non atopou ningún
        if len(busqueda) == 0:
            return {}

        id_buscado = 0
        min_distancia = sys.maxsize
        for moeda in busqueda:
            distancia = distance(buscado, moeda[1])
            if distancia<min_distancia:
                min_distancia = distancia
                id_buscado = moeda[0]

        obx_buscado = cur.execute(f'select simbolo, nome, ligazon from moeda where id={id_buscado}').fetchone()

        pax_web = r.get(self.get_url()+obx_buscado[2])

        if pax_web.status_code == 404:
            raise ErroPaxinaInaccesibel

        soup = bs(pax_web.text, 'html.parser')
        rango = soup.find(class_='namePill namePillPrimary').text.split(' ')[1]
        prezo = soup.find(class_='priceValue').text

        stats = soup.find_all(class_='statsValue')
        market_cap = stats[0].text
        fully_diluted_mc = stats[1].text
        vol24h = stats[2].text
        volume_market_cap = stats[3].text
        circulating_supply = stats[4].text

        supplies = soup.find_all(class_='maxSupplyValue')
        try:
            max_supply = supplies[0].text
        except:
            max_supply = '-'
        try:
            supply = supplies[1].text
        except:
            supply = '-'

        supply_percentage = soup.find(class_='supplyBlockPercentage').text
        watchlists = soup.find_all(class_='namePill')[2].text.split(' ')[1]

        con.close()

        return {
                'timestamp': time(),
                'rango': rango,
                'simbolo': obx_buscado[0],
                'nome': obx_buscado[1],
                'prezo': prezo,
                'market_cap': market_cap,
                'fully_diluted_market__cap': fully_diluted_mc,
                'volume_24h': vol24h,
                'circulating_supply': circulating_supply,
                'circulating_supply_percentage': supply_percentage,
                'max_supply': max_supply,
                'supply': supply,
                'volume_market_cap': volume_market_cap,
                'watchlists': watchlists
                }

# ------------------------------------------------------------------------------

