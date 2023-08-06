from json import dumps, loads


class ExecMappingData:
    def __init__(self, proj_name, redis_app, logger_func=print):
        self.__proj_name = proj_name
        self.__redis_app = redis_app
        self.__logger = logger_func

    def hget(self, name: str, default_value):
        return loads(self.__redis_app.hget(
            f"{self.__proj_name}." + 'MappingData', key=name.lower()) or b'null') or default_value

    def redis_setup_mapping_data(self, MappingData: type, mapping_data_default):
        default_value = mapping_data_default
        mapping_data = MappingData.__dict__
        name = list(mapping_data.keys())[list(mapping_data.values()).index(default_value)]
        self.__hdel_mapping_data(name)
        default_value = MappingData.__dict__[name]
        self.__setup_mapping_data(name, default_value)

    def redis_setup_all_mapping_data(self, MappingData: type, support_types=(list, int, dict, str)):
        flag = input('Will set all MappingData with default value on Redis. Y/N:')
        if flag == 'Y':
            for k, v in MappingData.__dict__.items():
                if "__" not in k and isinstance(v, support_types):
                    self.__setup_mapping_data(k, v)

    def __setup_mapping_data(self, name: str, value):
        self.__logger(f"Setup {self.__proj_name}.MappingData.{name}: "
                      f"{self.__hset_mapping_data(name.lower(), dumps(value))}")

    def __hset_mapping_data(self, key=None, value=None, mapping=None):
        return self.__redis_app.hset(f"{self.__proj_name}." + 'MappingData', key=key, value=value, mapping=mapping)

    def __hdel_mapping_data(self, *keys):
        return self.__redis_app.hdel(f"{self.__proj_name}." + 'MappingData', *keys)
