import math
import random
import time

#merenje.izmeri(True, (suma_prvih,994),(suma_prvih_binarno,1,100000))

def izmeri(print_result, *args):
	for arg in args:
		prvo = time.time()
		#print(arg)
		argumenti = list(arg)
		argumenti.pop(0)
		#print(argumenti)
		if print_result:
			print(arg[0](*argumenti))
		else:
			arg[0](*argumenti)
		#print(arg[0])
		#print(arg[0].__name__)
		print('Funkciji {} je trebalo {:.20f}s'.format(arg[0].__name__, time.time() - prvo))

	
def izmeri_i_pozive(koliko, *args):
	print(f"Za {koliko} poziva:")
	for arg in args:
		prvo = time.time()
		#print(arg)
		argumenti = list(arg)
		argumenti.pop(0)
		#print(argumenti)
		for i in range(koliko):
			arg[0](*argumenti)
		#print(arg[0])
		#print(arg[0].__name__)
		print('-  Funkciji {}({}) je trebalo {:.20f}s'.format(arg[0].__name__, arg[1], time.time() - prvo))