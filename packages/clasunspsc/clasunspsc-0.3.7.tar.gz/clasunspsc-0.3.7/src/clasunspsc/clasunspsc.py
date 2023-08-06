from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import spacy
import re
from ipywidgets import interact, interactive, Layout
import ipywidgets as widgets
from IPython.core.display import HTML
from nltk.stem import SnowballStemmer
spanish_stemmer = SnowballStemmer('spanish')
DF_Clas=pd.read_csv('https://raw.githubusercontent.com/ANCP-CCE-Analitica/clas_unspsc/main/data/Clas_UNSPSC_lemma.csv')
vectorizer = TfidfVectorizer() 

def CodUNSPSC_mascercanos(m, topk, mask=None):
    """
    Usamos la distancia del coseno sobre todos los tokens y se determinan los más cercanos.
    m (np.array): matriz de cosenos  
    topk (int): cantidad de elementos seleccionados del mejor al peor.
    """
    # Promedio de todos los cosenos
    if len(m.shape) > 1:
        cos_sim = np.mean(m, axis=0) 
    else: 
        cos_sim = m
    index = np.argsort(cos_sim)[::-1] # Indices desde el mayor al menor 
    if mask is not None:
        assert mask.shape == m.shape
        mask = mask[index]
    else:
        mask = np.ones(len(cos_sim))
    mask = np.logical_or(cos_sim[index] != 0, mask)
    best_index = index[mask][:topk]  
    dis=cos_sim[best_index]
    return best_index,dis

def get_recommendations_tfidf(sentence, tfidf_mat,topk):
    
    """
    Return the database sentences in order of highest cosine similarity relatively to each 
    token of the target sentence. 
    """
    # Embed the query sentence
    tokens_query = [str(tok) for tok in sentence.split()]
    embed_query = vectorizer.transform(tokens_query)
    # Create list with similarity between query and dataset
    mat = cosine_similarity(embed_query, tfidf_mat)
    # Best cosine distance for each token independantly
    best_index, dis = CodUNSPSC_mascercanos(mat, topk)
    return best_index,dis


lista=DF_Clas.groupby('Nombre Segmento').agg({'Código Segmento':(lambda x: x.value_counts().index[0])})
lista=lista.to_dict()['Código Segmento']
def recomendador(j,topk):
    try:
        j=re.sub("[^A-Za-zóáéíúñ]+"," ",j)
        j=' '.join([spanish_stemmer.stem(k) for k in j.split()])
        print(j)
        tfidf_mat = vectorizer.fit_transform(DF_Clas['Lema'])     
        best_index,dis = get_recommendations_tfidf(j.upper(), tfidf_mat,topk)
        dici=DF_Clas[['Código Producto','Nombre Producto','Nombre Clase']].iloc[best_index].to_dict()
        if dis[0]>0.005:
            print(dis)
            return display(HTML(pd.DataFrame(dici).to_html()))
        else:
            return display(HTML('<h2><b>Nada que recomendar</b></h2>'))
        
    except:
        return display(HTML('<h2><b>Nada que recomendar</b></h2>'))
    
def recomendador_api(j,topk):
    try:
        j=re.sub("[^A-Za-zóáéíúñ]+"," ",j)
        j=' '.join([spanish_stemmer.stem(k) for k in j.split()])
        print(j)
        tfidf_mat = vectorizer.fit_transform(DF_Clas['Lema'])     
        best_index,dis = get_recommendations_tfidf(j.upper(), tfidf_mat,topk)
        dici=DF_Clas[['Código Producto','Nombre Producto','Nombre Clase']].iloc[best_index].to_dict()
        if dis[0]>0.005:
            print(dis)
            return dici
        else:
            return {'Result':'Nada que recomendar'}
        
    except:
        return {'Result':'Nada que recomendar'}
    
def recomendador_int():
    estilo=Layout(width='80%', height='100px')
    box_text=widgets.Textarea(
        value='',
        placeholder='Haga una breve descripción de los productos que quiere usar ...',
        description='String:',
        disabled=False,
        layout=estilo
    )
    interact(recomendador,j=box_text,topk=[2,3,4,5,6,7,8,9,10])
    return