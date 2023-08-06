from graphene import Mutation, String, Boolean
from utils import *

class AppendData(Mutation):
	class Arguments:
		data = String()

	ok = Boolean()

	def mutate(root, info, data):
		res = handleAppend(data)
		return AppendData(ok = res == True)

