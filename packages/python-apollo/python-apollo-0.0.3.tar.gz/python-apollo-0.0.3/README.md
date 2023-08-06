### 简介
基于[apollo-client](https://github.com/BruceWW/pyapollo)，修改的 Apollo 客户端。


### 使用示例
**安装**

```shell
pip install -U python-apollo
```

**使用示例**
```python
from apollo.client import ApolloClient

# 获取 ApolloClient 实例
apollo = ApolloClient(app_id='xxx', config_server_url='http://127.0.0.1:8090', cycle_time=30)

# 从指定的 namespace 中获取 host 的值。
apollo.get_value("host", namespace='application')

# 从指定的 namespace 中获取 host 的值, 如果没有则去公共 namespace 中获取。如果都存在则私有的优先级高于公共的。
apollo.get_value("host", namespace='application', public_namespace=["common.smtp"])

# 获取指定 namespace 下的所有配置值
apollo.get_values(namespace='application')

# 获取指定 namespace 和 public_namespace 下的所有配置值。如果都存在则私有的优先级高于公共的。
apollo.get_values(namespace='application', public_namespace=["common.smtp"])
```
