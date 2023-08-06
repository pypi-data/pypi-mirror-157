import os

from apollo.client import ApolloClient

apollo = ApolloClient(
    app_id=os.environ.get("APOLLO_APP_ID"),
    config_server_url=os.environ.get("APOLLO_CONFIG_SERVER_URL")
)

if __name__ == '__main__':
    print(apollo.get_values(namespace="application"))  # properties 类型可不添加后缀
    print(apollo.get_values(namespace="config.json"))  # json
    print(apollo.get_values(namespace="config.yaml"))  # yaml
    print(apollo.get_values(namespace="config.yml"))   # yml
