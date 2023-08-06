#!/usr/bin/env python3

import os, sys
PROG_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(PROG_PATH))

from .. import jihyocrypt as jihyo
from argparse import ArgumentParser, Namespace


ALL_ENC_OPS = {	'f2f' : "Encrypt Input File to an Output File" ,
				'f2b' : "Encrypt Input File to output binary stream on the stdout stream"}

ALL_DEC_OPS = {	'f2f' : "Decrypt Input File to an Output File" ,
 				'f2b' : "Decrypt Input File to a binary stream on the stdout stream",
				'f2s' : "Decrypt Input File Data to a standard python serializable object(.pickle object)"}


def bool_from_int(val):

	val  = int(val)

	if val not in (0,1):
		raise ValueError(f'Value should be 0/1')

	if val == 0:
		return False

	return True

def arguments(args : list = None ):

	parser = ArgumentParser(prog = 'jihyo' ,
	description = 'JihyoCrypt Command Line Tool. Uses Salsa20 backend with JPIC[Jihyocrypt Password Integrity Check]' ,
	epilog = f'Program stored @ "{os.path.abspath(os.path.dirname(__file__))}"')

	subparsers = parser.add_subparsers(dest = 'action')

	enc_parser = subparsers.add_parser('enc' )
	dec_parser = subparsers.add_parser('dec')

	enc_parser.add_argument(dest = 'file' , metavar = '<FILE>' , type = os.path.abspath ,
	 						help = 'File to encrypt using JihyoCrypt')

	dec_parser.add_argument(dest = 'file' , metavar = '<FILE>', type = os.path.abspath ,
							help = 'File to decrypt using JihyoCrypt')

	dec_options = dec_parser.add_argument_group(title = 'decryption mode' ,
	 											description = "Decryption Mode to be used by JihyoCrypt. Defaults to `f2f`")
	for option, htext in ALL_DEC_OPS.items():

		dec_options.add_argument(f'--{option}' ,
								action = 'store_const' , dest = 'mode' ,
								const = option , default = 'f2f' , help  = htext )

	enc_options = enc_parser.add_argument_group(title = 'encryption mode' ,
												description = "Encryption Mode to be used by JihyoCrypt. Defaults to `f2f`")

	for option, htext in ALL_ENC_OPS.items():

		enc_options.add_argument(f'--{option}' ,
								action = 'store_const' , const = option ,
								dest = 'mode' ,  default = 'f2f' , help = htext)

	for spec_parser in [enc_parser , dec_parser]:


		spec_parser.add_argument('-o' , '--output' , default = None , type = os.path.abspath , metavar = '<OUTPUT>' ,
								dest = 'output_dest' , help = 'Output file/stream')

		spec_parser.add_argument('-r' , '--redundant' , type = bool_from_int  , default = True , metavar = '<r>' ,
									dest = 'red'  , help = 'Redundancy required or not. Use 1 for true, 0 for false. TRUE by default')

		spec_parser.add_argument('-P' , '--progress_bar' , '--progress' , '--show-progress' ,
									dest = 'p_bar' , action = 'store_true' ,
									help = 'Shows progress of enc/dec. OFF by default')

		spec_parser.add_argument('-p' , '--password' ,
									dest = 'password' , action = 'store' , default = None,
									help = 'Password to encrypt/decrypt. Note: Masked input will be taken if not provided')

	if args == None:
		return parser.parse_args()

	return parser.parse_args(args)

def pretty_print(obj , indent : int = 4 , stream = sys.stdout):

	import pprint
	content = pprint.PrettyPrinter(indent = indent , stream = stream)
	content.pprint(obj)
	
def obtain_password():
    
	from .getpass import getpass
	return getpass("Enter Password: " , colored = True)
 
def MainDriver(opts : Namespace):

	# jihyo.BUFFER_SIZE = opts.buffer

	if opts.password is None:
		opts.password = obtain_password 

	if opts.mode.endswith('f') and opts.output_dest is None:
		opts.output_dest = f'{opts.file}.{"encrypted" if (opts.action == "enc") else "decrypted"}'

	if opts.file is None:
		raise ValueError(f'File to {"encrypt" if (opts.action == "enc") else "decrypt"} is not provided')

	if opts.action == 'enc':

		if opts.mode == 'f2f':

			jihyo.enc_f2f(input_file = opts.file , output_file = opts.output_dest , password = opts.password , redundant = opts.red, progress_bar = opts.p_bar)
			return None 

		elif opts.mode == 'f2b':

			r = jihyo.dec_f2b(input_file = opts.file , password = opts.password, redundant = opts.red , progress_bar = opts.p_bar)

			pretty_print(r)
			return None 

		else:
      
			raise ValueError(f'Other modes of encryption need to be done via script. Cannot be done via command line')

	elif opts.action == 'dec':

		if opts.mode == 'f2f':

			jihyo.dec_f2f(input_file = opts.file , output_file = opts.output_dest , password = opts.password , redundant = opts.red , progress_bar = opts.p_bar)
			return None 

		else:
      
			if opts.output_dest is None:
				opts.output_dest = sys.stdout 
    
			else:
				opts.ouput_dest = open(opts.output_dest , 'wb')

			if opts.mode == 'f2b':
				r = jihyo.dec_f2b(input_file = opts.file , password = opts.password , redundant = opts.red , progress_bar = opts.p_bar)

			elif opts.mode == 'f2s':
				r = jihyo.dec_f2s(input_file = opts.file , password = opts.password , redundant = opts.red , progress_bar = opts.p_bar)

			pretty_print(r , stream = opts.output_dest)
			opts.output_dest.close()

	else:
     
		raise ValueError(f'Action can only be enc/dec. Not `{opts.action}`')

if __name__ == '__main__':

	import pretty_traceback
	pretty_traceback.install()

	import colorama
	colorama.init(autoreset=True)

	opts = arguments()
	MainDriver(opts)

	colorama.deinit()
