import re
from .GstoreConnector import GstoreConnector

IP = "127.0.0.1"
Port = 9000
# httpType = "ghttp"
httpType = "grpc"
username = "root"
password = "123456"

gstore_db = "ccks2024people"

def get_sparql_text(query=None, s=None, p=None, o=None, all=False):
    if query:
        query = re.sub(r' <[^>]*> <[^>]*> <[^>]*>(\.)', '', query)
        query = re.sub(r' <[^>]*> <[^>]*> <[^>]*> (\.)', '', query)
        query = re.sub(r' <[^>]*> <[^>]*> "[^>]*" (\.)', '', query)
        # query = re.sub(r' <[^>]*> <[^>]*> <[^>]*> .', '', query)
        # query = re.sub(r' <[^>]*> <[^>]*> <[^>]*>(\.\t)', '', query)
    elif s is not None and p is not None and o is not None:
        raise Exception("Invalid query")
    elif s is not None and p is not None:
        query = "select ?x where { <%s> <%s> ?x }" % (s, p)
    elif s is not None and o is not None:
        query = "select ?x where { <%s> ?x <%s> }" % (s, o)
    elif p is not None and o is not None:
        query = "select ?x where { ?x <%s> <%s> }" % (p, o)  
    elif s is not None:
        query = "select ?x ?y where { <%s> ?x ?y }" % (s)
    elif p is not None:
        query = "select ?x ?y where { ?x <%s> ?y }" % (p)
    elif o is not None:
        query = "select ?x ?y where { ?x ?y <%s> }" % (o)
    elif all:
        query = "select ?x ?y ?z where { ?x ?y ?z }"
    else:
        raise Exception("Invalid query")
    return query

def parse_result(result):
    values = []
    vars = result['head']['vars']
    if len(vars)==0:
        return ["知识库未提及"]
    for binding in result['results']['bindings']:
        for var in vars:
            values.append(binding[var]['value'])
    if len(values)==0:
        return ["知识库未提及"]
    return values

gc = GstoreConnector(IP, Port, username, password, http_type=httpType)

def get_answer_from_gStore(query):
    # sparql_query = get_sparql_text(query)
    # print(sparql_query)
    sparql_query = query
    try:
        result = gc.query(gstore_db, "json", sparql_query, "POST").json()
        if result['StatusCode']==0:
            return parse_result(result), True
        else:
            print("error query:",result)
            return "error query", False
    except:
        raise Exception("gstore error")
    
from zhiwo.app.core.knowledge.text_reader import TextReader
all_relations = TextReader().load_to_set("/home/qihua/study/zhiwo/app/resources/ccks2024people_relations.txt")

def validate_relations(relations: list[str]):
    if relations and set(relations).issubset(all_relations):
        return True
    else:
        return False