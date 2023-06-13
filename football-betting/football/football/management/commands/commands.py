import hashlib, os, sys, time, traceback, threading
from io import StringIO

from django.conf import settings
from django.core.management.base import BaseCommand

def clamp(minimum, x, maximum):
	return max(minimum, min(x, maximum))

def td_to_milliseconds(td):
	ms = 0
	ms += td.seconds * 1000
	ms += td.microseconds / 1000
	return ms

class OutputWrapper:
	def __init__(self, out):
		self.out = out
		self.buf = StringIO()
	def write(self, msg, *args, **kwargs):
		self.out.write(msg, *args, **kwargs)
		self.buf.write(msg, *args, **kwargs)
	def getvalue(self):
		return self.buf.getvalue()

class LogCommand(BaseCommand):
	"""
	An extension of BaseCommand which stores the standard output (stdout, stderrr)
	in the database via the CommandLog model
	"""
	#instance of either LogCommand() or LogCommandParent()
	log = None

	#instance of LogCommandLookup()
	log_lookup = None

	#insance of CommandAccount()
	log_account = None

	# this is the name of the command that apppears in the command log
	name = ""

	# this is the start time the command
	time_start = 0

	# this is written to file
	# if you want to handle custom print out puts based on your Command or class, update this in your handle_client/handle_client_prompt func
	cmd_file_text = ""

	# current account we're running on (not always present)
	account = None

	# slack api
	send_slack = False
	slack_msgs = []

	# this cool stores is the command is responsible for calling other commands or not.
	is_parent_command = False
	is_child_command = False

	# this is the primary key of entery in attrib_log_parent (if one was sent)
	command_item_parent_id = None

	# this is the primary key of this commands entry in attrib_log
	attrib_log_id = None

	command_item = None

	# similar to the log_id's each command will have it's own hash to use to tokenize filenames.
	# parents and children will have seperate hashes.
	cmd_hash = None
	child_cmd_hash = None

	def add_arguments(self, parser):
		parser.add_argument("--parallel", dest="parallel", action="store_true", default=None)
		parser.add_argument("--do_not_log", dest="nolog", action="store_true", default=False)
		parser.add_argument("--warn_only", dest="warn_only", action="store_true", default=False)


		super(LogCommand, self).add_arguments(parser)

	def dictfetchall(self, cursor):
		"Returns all rows from a cursor as a dict"
		desc = cursor.description
		return [
			dict(zip([col[0] for col in desc], row))
			for row in cursor.fetchall()
		]

	def print_out(self, text):
		text = str(text)
		print_type = 'out'
		self.update_print_log(text, print_type)

	def print_info(self, text, base=None):
		text = str(text)
		print_type = 'info'		
		self.update_print_log(text, print_type)

	def print_warning(self, text):
		text = str(text)
		print_type = 'warning'		
		self.update_print_log(text, print_type)

	def print_success(self, text):
		text = str(text)
		print_type = 'success'		
		self.update_print_log(text, print_type)

	def print_failure(self, text):
		text = str(text)
		print_type = 'failure'		
		self.update_print_log(text, print_type)

	def print_no_change(self, text):
		text = str(text)
		print_type = 'no_change'		
		self.update_print_log(text, print_type)

	def print_deletion(self, text):
		text = str(text)
		print_type = 'deletion'		
		self.update_print_log(text, print_type)

	def print_addition(self, text):
		text = str(text)
		print_type = 'addition'		
		self.update_print_log(text, print_type)

	def print_ssh(self, text):
		text = str(text)
		print_type = 'ssh'		
		self.update_print_log(text, print_type)

	def print_command(self, text):
		text = str(text)
		print_type = 'command'		
		self.update_print_log(text, print_type)

	def print_silent(self, text, print_type):
		print_type = print_type
		if text != '':
			self.update_print_log(text, print_type)

	def update_print_log(self, text, print_type, thread_id=None):
		if self.do_not_log:
			self.stdout.write(text)
			return
	
	def execute(self, *args, **kwargs):
		if kwargs['warn_only']:
			assert kwargs['threading'], "to use --warn_only you must also be using --threading"
		
		if kwargs['nolog']:
			print("****\n\n\nWARNING \n\n\n****\n\n\nNothing will be logged in the DB\nThese prints are all you have.\n\n\n*****")
			self.do_not_log = True
		else:
			self.do_not_log = False