from graphene import ObjectType, String, Schema, Int
from utils import *
import json

class Query(ObjectType):
    # this defines a Field `hello` in our Schema with a single Argument `name`
    get_data = String(ind=Int())

    # our Resolver method takes the GraphQL context (root, info) as well as
    # Argument (name) for the Field and returns data for the query Response
    def resolve_get_data(root, info, ind):
        return handleRead(ind)


