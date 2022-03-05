import os
import json
import time


class GuildUsers:

    def __init__(self, path, config):
        self.__config = config
        self.__users_path = os.path.join(path, "users.json")
        if os.path.exists(self.__users_path):
            with open(self.__users_path, "r") as users_file:
                self.__users = json.load(users_file)
        else:
            self.__users = dict()

    def __save(self):
        with open(self.__users_path, "w") as users_file:
            json.dump(self.__users, users_file, indent=2, sort_keys=True)

    def track_new_members(self, members):
        for member in members:
            member_id = str(member.id)
            if member_id not in self.__users:
                self.__users[member_id] = {
                    "last_activity": time.ctime(),
                    "username": member.name
                }
        self.__save()

    def update_member(self, member):
        member_id = str(member.id)
        self.__users[member_id] = {
            "last_activity": time.ctime(),
            "username": member.name
        }
        self.__save()

    def inactive(self):
        inactive_users = []
        now = time.time()
        for user_id, user_data in self.__users.items():
            last_activity = time.strptime(user_data["last_activity"])
            last_activity = time.mktime(last_activity)
            if now - last_activity > self.__config.get_timeout():
                inactive_users.append(int(user_id))
        return inactive_users

