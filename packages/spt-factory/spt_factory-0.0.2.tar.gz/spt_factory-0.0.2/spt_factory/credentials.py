from abc import ABC, abstractmethod


class Credentials(ABC):
    __slots__ = 'crede', 'crede_object', 'factory_params', 'custom_params'

    def __init__(self, crede_object, factory_params, custom_params):
        self.factory_params = factory_params
        self.custom_params = custom_params

    def get_credentials(self):
        return self.crede


class PostgresMongoCredentials(Credentials):

    def __init__(self, crede_object, factory_params, custom_params):
        super().__init__(crede_object, factory_params, custom_params)
        mongo_client = crede_object
        postgres_crede = mongo_client.spt.credentials.find_one({"type": "postgres"})
        postgres_crede['sslrootcert'] = factory_params['tlsCAFile']
        del postgres_crede['_id']
        del postgres_crede['type']
        self.crede = postgres_crede
        self.crede.update(custom_params)


class MongoMongoCredentials(Credentials):

    def __init__(self, crede_object, factory_params, custom_params):
        super().__init__(crede_object, factory_params, custom_params)
        self.crede = {
            'host': factory_params['mongo_url'],
            'tlsCAFile': factory_params['tlsCAFile']
        }
        self.crede.update(custom_params)


class AnyMongoCredentials(Credentials):
    def __init__(self, crede_object, factory_params, custom_params):
        super().__init__(crede_object, factory_params, custom_params)
        any_crede = crede_object.spt.credentials.find_one({"type": custom_params.get('type', "undefined")})
        if any_crede is None:
            self.crede = {'type': custom_params.get('type', "undefined")}
        else:
            del any_crede['_id']
            del custom_params['type']
            self.crede = any_crede
            self.crede.update(custom_params)
