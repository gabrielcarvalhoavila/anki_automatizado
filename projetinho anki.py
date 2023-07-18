from bs4 import BeautifulSoup
import requests
import genanki
import random
import os
from funcoes_auxiliares import gerar_cor_aleatoria, percentual
from webscraping import download_images

#headers = {'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58'}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'} #antigo
modelo_card = genanki.BASIC_MODEL        
meu_deck = genanki.Deck(1661023725586, 'ENGLISH')
#1655412292133 id antigo
dir_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(dir_path, 'ingles.txt')

if __name__ == '__main__':
    with open (file_path) as arq:
        for i in arq:

            quantidade_cards = 2     #Quantos cards quer fazer
            listafrases = []
            listasignificados = []
            dicio_sig_frequencias = {}
            palavra_pesquisada = i.strip().lower()


            
            palavra = palavra_pesquisada.replace(' ', '+')
            url = requests.get(f'https://context.reverso.net/translation/english-portuguese/{palavra}', headers= headers).text
            soup = BeautifulSoup(url, 'lxml')
            download_images(palavra_pesquisada,quantidade_cards)
            # Coleta as frases e os significados do site context.reverso.net
            try:
                frases = soup.find_all('div', class_= 'src ltr')
                significados = soup.find_all('span', class_= 'display-term')
            except:
                continue
            frequencias = soup.find_all(attrs={"data-freq": True})
            freq_values = [tag['data-freq'] for tag in frequencias]
            freq_values = list(map(int, freq_values))

            
            somafrequencias = sum(freq_values)
            listafrequencias = [(x / somafrequencias) for x in freq_values]
    
            for significado in significados:
                listasignificados.append(significado.text.strip())

            
            for i in range(len(listafrequencias)):
                dicio_sig_frequencias[listafrequencias[i]] = listasignificados[i]

            # Dicionário pareia os significados com as frequências, e ordena o dicionário de forma que o significado mais frequente seja o primeiro
            dicio_sig_frequencias = dict(sorted(dicio_sig_frequencias.items(), reverse=True))
            chave_a_remover = None
            # Remove as palavras que são iguais a palavra pesquisada
            for chave, valor in dicio_sig_frequencias.items():
                if valor.strip().lower() == palavra_pesquisada.strip().lower():
                    chave_a_remover = chave
                    break       
            if chave_a_remover is not None:
                del dicio_sig_frequencias[chave_a_remover]
            listafrequencias = list(map(percentual, list(dicio_sig_frequencias.keys())))
            listasignificados = list(dicio_sig_frequencias.values())
            for frase in frases:
               listafrases.append(frase.text.strip())
            if len(listasignificados) == 0:
                continue
            ### Gera os cards ###

            for i in range(quantidade_cards):
                random_color = gerar_cor_aleatoria()
                fraseatual =  listafrases[i]
                fraseatual = fraseatual.replace(palavra_pesquisada, f'<span style="color:{random_color}">{palavra_pesquisada}</span>') 
                imagem_atual = palavra_pesquisada + str(i+1)+'.jpg'

                nota = genanki.Note(
                    model=modelo_card,
                    fields=[fraseatual, f'{listasignificados[0]}, {listasignificados[1]}, {listasignificados[2]} <br> <img src="{imagem_atual}">'] if len(listasignificados) >= 3 else [fraseatual, f'{listasignificados[0]} <br> <img src="{imagem_atual}">']

                    )
                print(fraseatual)
                if len(listafrequencias) >= 3:        
                    print(f'{listasignificados[0]}, {listasignificados[1]}, {listasignificados[2]}')
                else:
                    print(f'{listasignificados[0]}')
                meu_deck.add_note(nota)

        pacote_anki = genanki.Package(meu_deck)
        pacote_anki.write_to_file('ENGLISH.apkg')
    #