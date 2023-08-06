"""
python3 -m pip install pycryptodome pretty_traceback

A simple implementation of Salsa20 along with a nonce+password based key and hash determination function. 
Multiple exposed functions to ease encryption and decryption to a single key based program. 



syntax: enc/dec_x2x
	where x: s -> Pickleable object; f-> File ; b -> Binary data
	enc/dec : enc -> Encryption , dec -> Decryption
	example: enc_s2f means encrypt from a standard object to a file
"""

BUFFER_SIZE  : int = 3*1024*1024													##3 MB
__version__ : str = '2.5.0'															##Optional Progress Bar Added for most functions
DEFAULT_OBFUSCATION_ROUNDS = DEFAULT_JPIC_ROUNDS  = 6					##N rounds of computation for key_decryptor and first_block_blender

password_to_bytes= lambda password : (password.encode('utf8')) if isinstance(password , str) else password
password_to_str = lambda password: (password.decode('utf8')) if isinstance(password , bytes) else password

"""Copy the following classes into self.password_generators script as well, this is copy pasted for more efficient albeit longer and dirtier code"""


import os, sys
from Crypto.Cipher import Salsa20
from hashlib import sha512 , sha256
import io 
import warnings

class PasswordError(ValueError):
	pass

class CorruptionError(ValueError):
	pass

def npdkf(nonce : bytes , password : bytes , rounds : int = DEFAULT_OBFUSCATION_ROUNDS):

	r = nonce
	password = password_to_bytes(password)

	for i in range(rounds):
		r = sha256(r + password).digest()

	return r

def jpic_gen(nonce : bytes , enc_password : bytes , user_password : bytes ,  rounds : int = DEFAULT_JPIC_ROUNDS):

	s = nonce
	major_pass = password_to_bytes(enc_password) + password_to_bytes(user_password)


	for i in range(rounds):
		s = sha512(s + major_pass).digest()

	return s

def key_maker( password : bytes ,nonce : bytes = None , 
              rounds : int = DEFAULT_OBFUSCATION_ROUNDS, jpic_rounds : int = DEFAULT_JPIC_ROUNDS , 
              redundant : bool = True):

	if nonce == None:

		nonce = os.urandom(8)

	password = password_to_bytes(password)

	r = npdkf(nonce , password , rounds = rounds)

	if redundant:
		s = jpic_gen(nonce , r , password  , rounds = jpic_rounds )
		return (nonce , r , s)

	return (nonce , r)

def SalsaMix(password:  bytes , nonce : bytes = None , rounds : int = DEFAULT_OBFUSCATION_ROUNDS , redundant : bool = True):	

	vals = key_maker(password  , nonce , rounds, redundant)

	return Salsa20.new(vals[1] , nonce = vals[0]  )

"""Function Classes Copy Stop Here"""

	
FULL_BLOCK , EMPTY_BLOCK , BLOCK_LENGTH = "🟢" , "🔴" , 10

def eprint(*args, **kwargs):


	print(*args, file=sys.stderr, **kwargs)

make_block = lambda processed , total , blocks = 25 : \
			FULL_BLOCK*(-(processed*blocks)//-total) + EMPTY_BLOCK*(((total-processed)*blocks)//total)
							##Ceiling												##Floor 

pbar_func = lambda running_size , total_size : eprint(f'{100*running_size//total_size}% |{make_block(running_size, total_size)}| {running_size}/{total_size} B' , end = '\r')
comp_func = lambda size : eprint(f'Completed:: 100% |{make_block(100 , 100)}| {size}/{size} B' , end = '\n')

def enc_redundant_warning():

	warnings.warn("Encryption being executed using non-redundant mode. This is risky and has no mode of verification/check in decryption.\
	Use this mode only if you understand what you're doing" , Warning)

def dec_redundant_warning():
    
	warnings.warn("Decryption being conducted using non-redundant mode. Make sure the file was definitely encrypted using \
	non-redundant mode" , Warning)

def enc_b2b(data : bytes , password: bytes , redundant: bool = True , **kwargs ):

	if not redundant:
		enc_redundant_warning() 

	vals= key_maker(password, redundant = redundant)
	cipher = Salsa20.new(vals[1] , vals[0])

	if redundant:
		return vals[0] + vals[-1] + cipher.encrypt(data)

	return vals[0] + cipher.encrypt(data)

def dec_b2b(data : bytes , password: bytes , redundant : bool = True , **kwargs):

	if not redundant:
		dec_redundant_warning()

	counter = 0 
	n = len(data)

	if n < 8:
		raise CorruptionError("The input data is corrupted, since it does not contain nonce")

	counter +=8 
	nonce = data[:8]

	vals = key_maker(password, nonce = nonce , redundant = redundant)
	cipher = Salsa20.new(vals[1] , vals[0])

	if redundant:

		if n < 72 : 
			raise CorruptionError("The input data is corrupted, does not possess JPIC block")

		if  vals[-1] != data[8:72]:
			raise PasswordError("Incorrect password inputted")

		counter += 64

	
	return cipher.decrypt(data[counter:])

def subroutine_major(	cipher, function : str  , i_handle , o_handle, size : int = 0 , 
						progress_bar : bool = True , buffer_size : int = BUFFER_SIZE , **kwargs) :

	func_ = getattr(cipher , function)
	running_size = 0 
	size = max(size , 1)			##All files must at least be one byte. This is only for cases of error. 
 
	if progress_bar : 
		
		pbar = pbar_func
		cbar = comp_func 
  
	else:
     
		pbar = lambda *args, **kwargs: None
		cbar = lambda *args, **kwargs : None 

	input_line = i_handle.read(buffer_size)


	while input_line != b'':

		o_handle.write(func_(input_line))
		running_size += buffer_size 
		pbar (running_size , size )
		input_line = i_handle.read(buffer_size)

	cbar(size)
	return None 
	
def enc_major(	i_handle , o_handle , size : int  , password : bytes , 
				redundant : bool = True , progress_bar : bool = False , buffer_size = BUFFER_SIZE , 
				**kwargs):

	if not redundant:
		enc_redundant_warning() 

	vals = key_maker(password , redundant = redundant)
	cipher = Salsa20.new(vals[1] , vals[0] ) 

	o_handle.write(vals[0])

	if redundant:
		o_handle.write(vals[-1])

	return subroutine_major(cipher , 'encrypt' , 
							i_handle , o_handle, size , 
							progress_bar, buffer_size , **kwargs)

def dec_major(	i_handle , o_handle, size: int , password : bytes , 	
				redundant: bool = True , progress_bar : bool = False , buffer_size : int = BUFFER_SIZE , **kwargs):

	if not redundant:
		dec_redundant_warning()

	nonce = i_handle.read(8)
	size -=8 

	if len(nonce) < 8:
		raise CorruptionError("The input source is corrupted as it doesnt even contain nonce")

	vals = key_maker(password , nonce = nonce, redundant = redundant )
	cipher = Salsa20.new(vals[1] , vals[0])

	if redundant:

		f_block = i_handle.read(64)

		if len(f_block) < 64:
			raise CorruptionError("The input source is corrupted as it doesnt contain enough data for JPIC")

		if f_block != vals[-1]:

			raise PasswordError("Incorrect Password input by user")
		
		size -= 64 

	return subroutine_major(cipher , 'decrypt' , 
							i_handle , o_handle, size , 
							progress_bar , buffer_size , **kwargs)

def enc_b2f(data : bytes , filename : str , password: str , redundant : bool = True , progress_bar : bool = False , 
			buffer_size : int = BUFFER_SIZE ):

	i_handle = io.BytesIO(data)
	size = len(data)
	
	with open(filename , 'wb') as o_handle:

		enc_major(i_handle , o_handle , size , password , redundant, progress_bar , buffer_size )

	return True 

def enc_f2f(input_file : str , output_file : str , password : bytes , redundant : bool = True, progress_bar : bool = False , buffer_size : int = BUFFER_SIZE):

	size = os.stat(input_file).st_size

	with open(input_file  , 'rb' ) as i_handle:
		with open(output_file , 'wb' ) as o_handle:

			enc_major(i_handle , o_handle , size , password , redundant , progress_bar , buffer_size)
	
	return True 

def enc_f2b(input_file : str , password: bytes , redundant : bool = True, progress_bar : bool = False , buffer_size : int = BUFFER_SIZE):

	size = os.stat(input_file).st_size 
	o_handle = io.BytesIO()

	with open(input_file  , 'rb' ) as i_handle:

		enc_major(	i_handle , o_handle , size, 
					password , redundant , progress_bar , buffer_size )

	return o_handle.getvalue() 

def dec_f2f(input_file : str , output_file : str , password : bytes , redundant : bool = True, progress_bar : bool = False , buffer_size : int = BUFFER_SIZE):

	size = os.stat(input_file).st_size

	with open(input_file, 'rb') as i_handle:
		with open(output_file, 'wb') as o_handle:

			dec_major(	i_handle , o_handle , size , 
						password, redundant , progress_bar , buffer_size)

	return True 
 
def dec_f2b(input_file : str , password: bytes , redundant : bool = True, progress_bar : bool = False , buffer_size : int = BUFFER_SIZE):

	size = os.stat(input_file).st_size 
	o_handle = io.BytesIO()  

	with open(input_file , 'rb') as i_handle:

		dec_major(	i_handle , o_handle , size , 
					password , redundant , progress_bar , buffer_size ) 

	return o_handle.getvalue() 

def dec_b2f(data : bytes , password: bytes , output_file : str , redundant : bool = True , progress_bar : bool = False , buffer_size : int = BUFFER_SIZE):

	size = len(data)
	i_handle = io.BytesIO(data)
	
	with open(output_file , 'wb') as o_handle:

		dec_major(	i_handle , o_handle , size ,
					password , redundant , progress_bar , buffer_size)

	return True 

"""Dependent Functions"""

def load_pickle():
    
    try:
        import _pickle as pickle
    except ImportError:
        import pickle 
        
    return pickle 

#enc_b2f
def enc_s2f(data : bytes , filename : str , password: str , redundant : bool = True , progress_bar : bool = False , buffer_size : int = BUFFER_SIZE):

	pickle = load_pickle()
	data = pickle.dumps(data)

	return enc_b2f(	data = data , filename = filename , password = password , 
					redundant = redundant , progress_bar = progress_bar , buffer_size = buffer_size)

#enc_b2b
def enc_s2b(data : bytes , password : bytes, redundant : bool = True):

	pickle = load_pickle()
	data = pickle.dumps(data)

	return enc_b2b(data = data , password = password , redundant = redundant)

#dec_f2b
def dec_f2s(input_file : str , password: bytes , redundant : bool = True, progress_bar : bool = False , buffer_size : int = BUFFER_SIZE):

	pickle = load_pickle()
	return pickle.loads(dec_f2b(input_file = input_file, 
								password = password , redundant = redundant , progress_bar = progress_bar , buffer_size = buffer_size ))

#dec_b2b
def dec_b2s(data : bytes, password: bytes , redundant : bool = True):

	pickle = load_pickle()
	return pickle.loads(dec_b2b(data = data , password = password , redundant = redundant))
