from jina import Client, Document
from jina.types.request import Response


def print_matches(resp: Response):  # the callback function invoked when task is done
    for idx, d in enumerate(resp.docs[0].matches[:10]):  # print top-3 matches
        print(f'[{idx}]{d.scores["euclidean"].value:2f}: "{d.text}"')


query='GAUGE VALVE, MALE NPT inlet x (3 EA.) 1/2 FEMALE NPT OUTLET, 6000PSIG'        
#query='NEEDLE VALVE, FNPT ends, 6000PSIG 316SS body'        
   

c = Client(protocol='grpc', port=12345)  # connect to localhost:12345
c.post('/search', Document(text=query.lower()), on_done=print_matches)
