import numpy as np
from jina import DocumentArray, Executor, requests
import pandas as pd
from collections import defaultdict
import numpy as np
from jina import DocumentArray, Executor, requests
from jina import Flow
from jina import Document
import joblib

vec=joblib.load('vec.pkl')
svd = joblib.load('svd.pkl')
count=0

class CharEmbed(Executor):  # a simple character embedding with mean-pooling
    offset = 32  # letter `a`
    dim = 127 - offset + 1  # last pos reserved for `UNK`
    char_embd = np.eye(dim) * 1  # one-hot embedding for all chars

    @requests
    def foo(self, docs: DocumentArray, **kwargs):
        global count
        global vec
        for d in docs:
            #print (d)
            #r_emb = [ord(c) - self.offset if self.offset <= ord(c) <= 127 else (self.dim - 1) for c in d.text]
            #print (r_emb)
            #d.embedding = self.char_embd[r_emb, :].mean(axis=0)  # average pooling
            
            d.embedding = svd.transform(vec.transform(['adf']).toarray())[0]
         
            count+=1
            print (count)

class Indexer(Executor):
    _docs = DocumentArray()  # for storing all documents in memory

    @requests(on='/index')
    def foo(self, docs: DocumentArray, **kwargs):
        self._docs.extend(docs)  # extend stored `docs`

    @requests(on='/search')
    def bar(self, docs: DocumentArray, **kwargs):
        docs.match(self._docs, metric='euclidean', limit=10)

        
data = pd.read_csv('SAP-Data.csv',low_memory=False)
data['text'] = data[['SAP_Part_Short','Desc(40)','Long Text']].apply(lambda x: str(x[1])+' '+str(x[2]),axis=1)
li = data[['SAP_Part_Short','text']].values.tolist()
d = defaultdict(list)
for item in li:
    d[item[1].lower()].append(item[0])
to_index = [item[0] for item in d.items()]

    
f = (Flow(protocol='grpc', port_expose=12345)#port_expose=12345, protocol='http')#, cors=True)
        .add(uses=CharEmbed, replicas=10)
        .add(uses=Indexer))  # build a Flow, with 2 shard CharEmbed, tho unnecessary       
   
with f:
    f.post('/index', (Document(text=t.strip()) for idx,t in enumerate(to_index) if t.strip() and idx < 500000))  # index all lines of _this_ file
    #f.post('/index', get_document, request_size=10)  # index all lines of _this_ file
    
    f.block()  # block for listening request     
        

