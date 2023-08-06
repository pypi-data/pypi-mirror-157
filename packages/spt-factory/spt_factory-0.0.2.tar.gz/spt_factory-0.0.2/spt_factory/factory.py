from spt_factory.resources import Postgres, Mongo, AnyCreds
from spt_factory.credentials import PostgresMongoCredentials, MongoMongoCredentials, AnyMongoCredentials
from spt_factory.resources import Postgres, Mongo
from spt_factory.credentials import PostgresMongoCredentials, MongoMongoCredentials
from functools import partial
from copy import deepcopy


class Factory:

    resources = (
        (Postgres, PostgresMongoCredentials),
        (Mongo, MongoMongoCredentials),
        (AnyCreds, AnyMongoCredentials)
    )

    def get_crede_object(self, **factory_params):
        pass

    def __init__(self, **factory_params):
        self.factory_params = factory_params
        self.crede_object = self.get_crede_object(**factory_params)
        self.resources = {}
        for resource, credentials in Factory.resources:

            def get_resource(**params):
                custom_params = deepcopy(params)
                del custom_params['credentials']
                del custom_params['resource']
                c = params['credentials'](
                    crede_object=self.crede_object,
                    factory_params=self.factory_params,
                    custom_params=custom_params
                )
                return params['resource'](c).get_object()

            def get_credentials(**params):
                custom_params = deepcopy(params)
                del custom_params['credentials']
                return params['credentials'](
                    crede_object=self.crede_object,
                    factory_params=self.factory_params,
                    custom_params=custom_params
                ).get_credentials()

            setattr(self, f'get_{resource.get_name()}', partial(get_resource, resource=resource, credentials=credentials))
            setattr(self, f'get_{resource.get_name()}_credentials', partial(get_credentials, credentials=credentials))


class MongoFactory(Factory):

    def __init__(self, mongo_url, tlsCAFile):
        super().__init__(mongo_url=mongo_url, tlsCAFile=tlsCAFile)

    def get_crede_object(self, **factory_params):
        return Mongo(
            MongoMongoCredentials(
                crede_object=None,
                factory_params=factory_params,
                custom_params={}
            )
        ).get_object()
