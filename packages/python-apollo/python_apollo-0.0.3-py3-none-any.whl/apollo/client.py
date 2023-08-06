import os
import json
import time
import logging
import datetime
import tempfile
import requests
import threading
import yaml

from typing import Any, Dict

log = logging.getLogger(__name__)


class ApolloClient(object):
    def __init__(
            self,
            app_id: str,
            cluster: str = "default",
            config_server_url: str = "http://localhost:8090",
            timeout: int = 60,
            cycle_time: int = 180,
            cache_file_path: str = None,
    ):
        """
        :param app_id:
        :param cluster:
        :param config_server_url:
        :param timeout:
        :param cycle_time:
        :param cache_file_path:
        """
        self.config_server_url = config_server_url
        self.app_id = app_id
        self.cluster = cluster
        self.timeout = timeout

        self._cache = {}
        self._notification_map = {}
        self._cycle_time = cycle_time
        self._hash = {}
        if cache_file_path is None:
            self._cache_file_path = os.path.join(tempfile.gettempdir(), "config", self.app_id,
                                                 f"{datetime.datetime.now().strftime('%Y-%m-%d')}")
        else:
            self._cache_file_path = cache_file_path

        self.display_start_message = False
        self._path_checker()
        self.start()

    def _get_namespaces(self) -> dict:
        """
        获取 namespaces
        :return :
        """
        namespaces = dict()
        url = f"{self.config_server_url}/apps/{self.app_id}/clusters/{self.cluster}/namespaces"
        r = self._request_get(url)
        if r.status_code == 200:
            namespaces = {_.get("namespaceName"): _.get("id") for _ in r.json()}
        return namespaces

    @staticmethod
    def parse(namespace, value):
        """
        解析不同类型的配置文件
        :param namespace:
        :param value:
        :return:
        """
        value = json.loads(value)
        config_type = namespace.split(".")[-1] or ""
        if config_type.upper() in ["JSON", "YAML", "YML", "XML", "TXT"]:
            if config_type.upper() == "JSON":
                return json.loads(value.get("content"))
            elif config_type.upper() in ["YAML", "YML"]:
                return yaml.load(value.get("content"), Loader=yaml.Loader)
            else:
                return value.get("content")
        return value

    def get_values(self, namespace: str = "application", public_namespace: [str] = None):
        """
        获取 namespace 下的所有配置，namespace 中的值优先级高于 public_namespace 中的
        :param namespace:
        :param public_namespace:
        :return:
        """
        value = dict()
        if public_namespace:
            for pub_namespace in public_namespace:
                if pub_namespace in self._cache:
                    value.update(self._cache[pub_namespace])

        if namespace in self._cache:
            value.update(self._cache[namespace])

        return value

    def get_value(self, key: str, default_val: str = None, namespace: str = "application",
                  public_namespace: [str] = None) -> Any:
        """
        根据 key 获取 namespace 下的配置，namespace 中的值优先级高于 public_namespace 中的
        :param key:
        :param default_val:
        :param namespace:
        :param public_namespace:
        :return:
        """
        try:
            # check the namespace is existed or not
            if namespace in self._cache:
                value = self._cache[namespace].get(key)
                if value is not None:
                    return value

            if public_namespace:
                for namespace in public_namespace:
                    if namespace in self._cache:
                        value = self._cache[namespace].get(key)
                        if value is not None:
                            return value

            return default_val
        except Exception:
            return default_val

    def start(self) -> None:
        """
        开始轮询获取配置
        :return:
        """
        # check the cache is empty or not
        if len(self._cache) == 0:
            self._long_poll()
        # start the thread to get config server with schedule
        t = threading.Thread(target=self._listener)
        t.setDaemon(True)
        t.start()

    def _request_get(self, url: str, params: Dict = None) -> requests.Response:
        """

        :param url:
        :param params:
        :return:
        """
        return requests.get(url=url, params=params, timeout=self.timeout)

    def _path_checker(self) -> None:
        """
        检查缓存目录是否存在
        :return:
        """
        if not os.path.exists(self._cache_file_path):
            os.makedirs(self._cache_file_path)

    def _update_local_cache(self, release_key: str, data: str, namespace: str = "application") -> None:
        """
        更新本地缓存
        :param release_key:
        :param data: new configuration content
        :param namespace::s
        :return:
        """
        # trans the config map to md5 string, and check it's been updated or not
        if self._hash.get(namespace) != release_key:
            # if it's updated, update the local cache file
            with open(os.path.join(self._cache_file_path, f"{self.app_id}_{namespace}.conf"), "w") as f:
                new_string = json.dumps(data)
                f.write(new_string)
            self._hash[namespace] = release_key

    def _get_local_cache(self, namespace: str = "application") -> Dict:
        """
        读取本地缓存
        :param namespace:
        :return:
        """
        cache_file_path = os.path.join(self._cache_file_path, f"{self.app_id}_{namespace}.conf")
        if os.path.isfile(cache_file_path):
            with open(cache_file_path, "r") as f:
                result = json.loads(f.read())
            return result
        return {}

    def _get_config_by_namespace(self, namespace: str = "application") -> None:
        """
        根据 namespace 获取配置文件
        :param namespace:
        :return:
        """
        url = f"{self.config_server_url}/apps/{self.app_id}/clusters/{self.cluster}/namespaces/{namespace}/releases/latest"
        try:
            r = self._request_get(url)
            if r.status_code == 200 and r.text != "":
                response_data = r.json()
                config = self.parse(namespace, response_data.get("configurations", {}))
                release_key = response_data.get("releaseKey", str(time.time()))

                self._cache[namespace] = config
                self._update_local_cache(release_key, config, namespace, )
            else:
                data = self._get_local_cache(namespace)
                log.info(f"{self.app_id}-{namespace}: get configuration from local cache file")
                self._cache[namespace] = data
        except BaseException as e:
            log.warning(str(e))
            data = self._get_local_cache(namespace)
            self._cache[namespace] = data

    def _long_poll(self) -> None:
        try:
            self._notification_map = self._get_namespaces()
            for namespace in self._notification_map.keys():
                self._get_config_by_namespace(namespace)
        except requests.exceptions.ReadTimeout as e:
            log.warning(str(e))
        except requests.exceptions.ConnectionError as e:
            log.warning(str(e))
            self._load_local_cache_file()

    def _load_local_cache_file(self):
        """
        :return:
        """
        for file_name in os.listdir(self._cache_file_path):
            file_path = os.path.join(self._cache_file_path, file_name)
            if os.path.isfile(file_path):
                file_simple_name, file_ext_name = os.path.splitext(file_name)
                if file_ext_name == ".swp":
                    continue
                namespace = file_simple_name.split("_")[-1]
                with open(file_path) as f:
                    self._cache[namespace] = json.loads(f.read())

    def _listener(self) -> None:
        """
        :return:
        """
        while True:
            self._long_poll()
            time.sleep(self._cycle_time)

            if not self.display_start_message:
                log.info(f" ======================== Config Client Start Running ========================")
                log.info(self._cache)
                self.display_start_message = True
