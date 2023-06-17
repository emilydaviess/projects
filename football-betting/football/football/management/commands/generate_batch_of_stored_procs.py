
from django.core import management
from django.conf import settings
from django.core.management.base import BaseCommand
import mysql.connector
from django.db import connection
import os
# from football.management.commands.commands import LogCommand

class Command(BaseCommand):
	name = 'Batch generate commands to build stored procs()'
	query = ""
	help = 'Runs all commands needed to generate stored procs() if needed.'

	def find_path(self, filename):
		for app_name in settings.INSTALLED_APPS:
			path = app_name + "/sql/" + filename + ".sql"
			if os.path.exists(path):
				return path
		raise Exception("Unable to find SQL file '" + filename + "'")


	def handle(self, *args, **kwargs):
		query = ""
		self.queries = []
		for filename in settings.CLIENT_STORED_PROCEDURES:
			f = self.find_path(filename)
			
			with open (f, "r") as myfile:
				txt = myfile.read()
				self.queries.append(txt)
				query += "\n\n" + txt
		self.query = query
		self.handle_prompt()
		#super(Command, self).handle(*args, **kwargs)

	def handle_prompt(self):
		make_file = False
		if make_file:
			text_file = open("gen_batch_query.sql", "w+")
			text_file.write(self.query)
			text_file.close()

		newconnection = mysql.connector.connect(
				user='root', 
				password='Caketin1', 
				host='localhost', 
				database='football',
				port=3306)
		newcursor = newconnection.cursor()
		try:
			print("Executing generated sql for all stored procs")	
			# We need to run execute for each query
			for query in self.queries:
				for result in newcursor.execute(query, multi=True):					
					pass
			newconnection.commit()
			print('Finished generating batch of procs.')
		except Exception as ex:
			print("whoops", ex)
			raise ex
		finally:
			newcursor.close()
			newconnection.close()