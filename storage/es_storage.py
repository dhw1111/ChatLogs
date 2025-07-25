from elasticsearch import Elasticsearch

class ESStorage:
    def __init__(self, config):
        es_host = config.get('es_host')
        es_port = config.get('es_port')
        es_index = config.get('es_index')
        es_username = config.get('es_username')
        es_password = config.get('es_password')
        scheme = config.get('es_scheme', 'http')
        if es_host is None or es_port is None or es_index is None:
            raise ValueError("ES配置项缺失，请在插件管理界面完善es_host、es_port、es_index等配置！")
        if es_username and es_password:
            self.es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': scheme}], http_auth=(es_username, es_password))
        else:
            self.es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': scheme}])
        self.es_index = es_index

    def save_log(self, log: dict):
        self.es.index(index=self.es_index, body=log) 