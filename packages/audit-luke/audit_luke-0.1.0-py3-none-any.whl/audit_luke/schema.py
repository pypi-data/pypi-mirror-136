from graphene import Schema, ObjectType
from query import *
from append import *

class Mutation(ObjectType):
	append_data = AppendData.Field()

schema = Schema(query = Query, mutation = Mutation)

queryTest = '{ getData(ind: 2)}'
print(schema.execute(queryTest))

appendTest = 'mutation { appendData(data: "more data") { ok }  }'
print(schema.execute(appendTest))

queryAfterAppendTest = '{ getData(ind: 3)}'
print(schema.execute(queryAfterAppendTest))
