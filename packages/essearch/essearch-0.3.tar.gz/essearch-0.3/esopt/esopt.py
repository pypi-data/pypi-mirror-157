# elasticsearch的初始化

from pprint import pprint
import ijson
from tqdm import tqdm
from elasticsearch import Elasticsearch

# 以下路径本机和服务器中不同
json_path = ["/data2/dengyunlong/wiki_cn_data.json", "D:/My_Apps/BaiduNetdiskDownload/563w_baidubaike.json"
                                                     "/563w_baidubaike.json"]


def max_min(x: float, num_max: float, num_min: float):
    x = (x - num_min) / (num_max - num_min)
    return x


# 下面服务器中不需要用户名和密码的设置
def es_start(es_url="http://localhost:9200"):
    global es
    es = Elasticsearch([es_url], timeout=3600)


# 创建索引
def create_mapping(index: str):
    body = {
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "url": {
                    "type": "text"
                },
                "article": {
                    "type": "text",
                    "analyzer": "ik_smart"
                },
                "wiki_id": {
                    "type": "text"
                }
            }
        }
    }
    es.indices.create(index=index, body=body)


# 插入词条
def insert_entry(idx: str, doc: dict):
    es.index(index=idx, body=doc)


# 将json文件转化成elasticsearch接受的doc，并将其全部插入elasticsearch中
def json_to_doc(source: str, index: str):
    print("source:          ", source)
    with open(source, 'r', encoding='utf-8') as f:
        item_list = list(ijson.items(f, ''))[0]
        print(len(item_list))
        for item in tqdm(item_list):
            item_dict = {"wiki_id": item[0], "title": item[1], "url": item[2], "article": item[3]}
            insert_entry(index, item_dict)


# 查询词条
def search_entry(index: str, query: str, min_score=0.0, fields=None, source_includes=None, size=10):
    if source_includes is None:
        source_includes = ['title', 'article', 'wiki_id', 'url']
    if fields is None:
        fields = ['title^5', 'article']
    res_list = []
    analyzer_list = {"wiki_cn_new": "ik_max_word", "wiki_cn": "standard"}
    resp = es.search(index=index, size=100,
                     query={
                         "multi_match": {
                             "query": query,
                             "analyzer": analyzer_list[index],
                             "fields": fields
                         }
                     })
    score_list = []
    for res in resp['hits']['hits']:
        if len(res['_source']['article']) < 20:
            res['_score'] = float(res['_score']) / 3.0
        score_list.append(res['_score'])
    max_res_score = max(score_list)
    min_res_score = min(score_list)
    for res in resp['hits']['hits']:
        res['_score'] = max_min(res['_score'], max_res_score, min_res_score)
        res_list.append(res)
    res_list.sort(key=lambda x: (x['_score']), reverse=True)
    final_res_list = []
    size_num = 0
    for res in res_list:
        size_num += 1
        if res['_score'] >= min_score and size_num <= size:
            final_res = {}
            for item in source_includes:
                final_res.update({item: res['_source'][item]})
            final_res_list.append(final_res)
    return final_res_list


if __name__ == '__main__':
    es_start()
    create_mapping('wiki_cn_new')
    json_to_doc(json_path[0], 'wiki_cn_new')
    pprint(search_entry(index='wiki_cn_new', query='上海市的语言', source_includes=['title'], min_score=0.0))
