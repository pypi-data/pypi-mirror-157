
from requests import post
import json
import pandas as pd
from . import ConnectError
from pandas import DataFrame, Series


class TaoSClient:

    def __init__(self, td_config: dict, log: any):

        if td_config.get("HOST"):
            raise ConnectError("td配置文件的命名都应该小写, 如host=..., 而不是HOST")

        self.request_url = f"http://{td_config['host']}:{td_config['port']}/rest/sqlt/{td_config['db']}"
        self.auth = (td_config['user'], td_config['password'])
        self.time_out = (5, 5)
        self.log = log

    def query(self, query: str, measurement=None) -> any:
        """
        执行陶思的sql语句，存在查找字段时，则返回查找结果，查找字段为None，则进入创建表、删除数据、插入数据的操作，成功返回True
        使用方法如下：

        from negentropior.tools.connect.Tdengine import TaoSClient
        td = TaoSClient(td_config: dict, log: log对象)

        def get_sampling_data():
            sql = ''SELECT...'''
            result = td.query(sql, measurement"sampling_status")
            return result

        def insert_sampling_data():
            sql = '''INSERT...'''
            td.query(sql)

        def create_table():
            sql = '''CREATE...'''
            td.query(sql)

        def delete_sampling_data():
            sql = '''DELETE...'''
            td.query(sql)

        :param query: sql语句
        :param measurement: 查找字段
        :return:
        """
        data = None
        try:
            response = post(self.request_url, data=query, auth=self.auth, timeout=self.time_out)
            response_result = json.loads(response.text)

            if response.reason == 'OK':
                if measurement:
                    self.log.info(f'获取监控时序数据请求成功，请求参数正常, {query}')
                    data = response_result['data']
                    data = DataFrame(data, columns=['time_index', measurement])
                    data = Series(data[measurement].values, index=pd.to_datetime(data['time_index'], unit='ms'))
                else:
                    self.log.info(f'创建or写入or删除操作operating_status结果 {response_result}')
                    return True
            else:
                self.log.info(f'获取监控时序数据请求成功,请求参数异常, {query}')
        except Exception as e:
            self.log.error(f'获取监控时序数据请求报错, {e}')

        return data



