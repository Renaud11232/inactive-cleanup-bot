import os
import json


class GuildConfig:

    def __init__(self, path, defaults):
        self.__config_path = os.path.join(path, "config.json")
        if os.path.exists(self.__config_path):
            with open(self.__config_path, "r") as config_file:
                self.__config = json.load(config_file)
        else:
            self.__config = dict()
        self.__defaults = defaults

    def __get_default(self, config):
        current_config_item = self.__defaults
        for item in config:
            if item in current_config_item:
                current_config_item = current_config_item[item]
            else:
                return None
        return current_config_item

    def __get(self, config):
        config = config.split(".")
        current_config_item = self.__config
        for item in config:
            if item in current_config_item:
                current_config_item = current_config_item[item]
            else:
                return self.__get_default(config)
        return current_config_item

    def __set(self, config, value):
        config = config.split(".")
        current_config_item = self.__config
        for item in config:
            if item == config[-1]:
                current_config_item[item] = value
            elif item not in current_config_item:
                current_config_item[item] = dict()
            current_config_item = current_config_item[item]

    def __save(self):
        with open(self.__config_path, "w") as config_file:
            json.dump(self.__config, config_file, indent=2, sort_keys=True)

    def set_active(self, value):
        self.__set("active", value)
        self.__save()

    def is_active(self):
        return self.__get("active")

    def set_timeout(self, value):
        self.__set("timeout", value)
        self.__save()

    def get_timeout(self):
        return self.__get("timeout")

    def add_admin_role(self, value):
        roles = self.__get("admin.roles")
        if not roles:
            self.__set("admin.roles", [value])
        else:
            if value not in roles:
                roles.append(value)
        self.__save()

    def remove_admin_role(self, value):
        roles = self.__get("admin.roles")
        if roles and value in roles:
            roles.remove(value)
        self.__save()

    def add_admin_user(self, value):
        users = self.__get("admin.users")
        if not users:
            self.__set("admin.users", [value])
        else:
            if value not in users:
                users.append(value)
        self.__save()

    def remove_admin_user(self, value):
        users = self.__get("admin.users")
        if users and value in users:
            users.remove(value)
        self.__save()

    def add_immunity_role(self, value):
        roles = self.__get("immunity.roles")
        if not roles:
            self.__set("immunity.roles", [value])
        else:
            if value not in roles:
                roles.append(value)
        self.__save()

    def remove_immunity_role(self, value):
        roles = self.__get("immunity.roles")
        if roles and value in roles:
            roles.remove(value)
        self.__save()

    def get_immunity_roles(self):
        return self.__get("immunity.roles") or []

    def add_immunity_user(self, value):
        users = self.__get("immunity.users")
        if not users:
            self.__set("immunity.users", [value])
        else:
            if value not in users:
                users.append(value)
        self.__save()

    def remove_immunity_user(self, value):
        users = self.__get("immunity.users")
        if users and value in users:
            users.remove(value)
        self.__save()

    def get_immunity_users(self):
        return self.__get("immunity.users") or []
