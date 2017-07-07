import time
import json
import pandas as pd
from django.conf import settings
from couchdb import Server
from couchdb import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

SERVER=Server(getattr(settings, 'COUCHDB_SERVER'))
#SERVER=Server('http://127.0.0.1:5984')
SERVER.resource.credentials=('admin', '*@Ja#9824147318!')
db = SERVER['course_catlog']
db2=SERVER['recommender_data']
#df=pd.DataFrame(columns=['course', 'description', 'id'])
#dk=pd.DataFrame(columns=['course', 'id'])
    
def train(data_source):
    ds=pd.DataFrame(data_source)
    return _train(ds)

def _train(ds):
    tf=TfidfVectorizer(analyzer='word',
                       ngram_range=(1,3),
                       min_df=0,
                       stop_words='english')
    tfidf_matrix=tf.fit_transform(ds['course'].apply(str))

    cosine_similarities=linear_kernel(tfidf_matrix, tfidf_matrix)
    
    for idx, row in ds.iterrows():
        similar_indices = cosine_similarities[idx].argsort()[:-50:-1]
        similar_items = [(cosine_similarities[idx][i], ds['id'][i])
                         for i in similar_indices]
        # First item is the item itself, so remove it.
        # This 'sum' is turns a list of tuples into a single tuple:
        # [(1,2), (3,4)] -> (1,2,3,4)
        flattened = sum(similar_items[1:], ())
        db2[str(idx)]={'rec': list(flattened)}

def _predict(item_id):
    #return flattened.iloc[[item_id-1]]
    return db2[str(item_id)]['rec']
    
def parse_predict(c_to_predict):
    res=_predict(c_to_predict)
    result=[]
    for i in range(1,95,2):
        #result.append({"".join(df.ix[df['id']==res[i]]['course'].astype('str')):
         #             "".join(df.ix[df['id']==res[i]]['description'].astype('str'))})
        result.append(int(res[i]-1))
    return result

def main(c_list=[], key=[], value=[], to_train=False):
#    global df,dk
#    view=db.iterview('query_doc/a_docs', batch=2500)
#    q=0
#    for row in view:
#        q=q+1
#        df=df.append(pd.DataFrame({'course': [row.key], 'description': [row.value], 'id': [int(q)]}))
#        dk=dk.append(pd.DataFrame({'course': [row.key+' '+row.value], 'id': [int(q)]}))
#    q=0
#    for i in range(len(key)):
#        q=q+1
#        df=df.append(pd.DataFrame({'course': [key[i]], 'description': [value[i]], 'id':[int(q)]}))
#        dk=dk.append(pd.DataFrame({'course': [key[i]+' '+value[i]], 'id': [int(q)]}))
#    df.index=range(0,len(df))
#    dk.index=range(0,len(df))
#    print(df)
#    print(dk)
    if to_train:
        dk=pd.DataFrame(columns=['course', 'id'])
        q=0
        for i in range(len(key)):
            q=q+1
            dk=dk.append(pd.DataFrame({'course': [key[i]+' '+value[i]], 'id': [int(q)]}))
        dk.index=range(0,len(dk))
        train(dk)
    else:
        result=[]
        for c in c_list:
            result.extend(parse_predict(c))
        print(result)
        return result
    
