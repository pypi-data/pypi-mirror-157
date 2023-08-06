import json
import keycloak as kc


class Keycloak:
    def __init__(self, server, username, password, user_realm_name, realm_name):
        self.server = server
        self.username = username
        self.password = password
        self.user_realm_name = user_realm_name
        self.realm_name = realm_name

        print(f"{server}")
        self.keycloak_admin = kc.KeycloakAdmin(server_url=server,
                                            username=username,
                                            password=password,
                                            user_realm_name=user_realm_name,
                                            realm_name=realm_name)

    def import_mappers(self, f):
        data = json.load(f)
        mappers = data["identityProviderMappers"]

        for mapper in mappers:
            self.keycloak_admin.add_mapper_to_idp(mapper["identityProviderAlias"], mapper)
