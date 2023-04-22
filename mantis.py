import re
import uuid
import libcst
import argparse

from libcst import CSTTransformer, CSTVisitor

import colorama
from colorama import Fore


class VareDeobfuscator(CSTTransformer):

	def leave_FunctionDef(self, original_node, updated_node):
		label = original_node.name.value
		if re.match('saint[0-9]{5,7}', label):
			return libcst.RemoveFromParent()
		else:
			return original_node

	def leave_Assign(self, original_node, updated_node):
		label = original_node.targets[0].target.value
		if label == '__VareObfuscator__':
			return libcst.RemoveFromParent()
		else:
			return original_node

class DetectObfuscation(CSTVisitor):

	def __init__(self):
		self.obfuscator = None

	def visit_Assign(self, original_node):
		label = original_node.targets[0].target.value
		if label == '__VareObfuscator__':
			self.obfuscator = 'Vare'
			return original_node
			

if __name__ == "__main__":

	colorama.init()

	parser = argparse.ArgumentParser()

	parser.add_argument('-i', '--input', help = 'Name of file to deobfuscate', default = 'input')
	parser.add_argument('-o', '--output', help = 'Name of deobfuscated file', default = 'output')

	parsed_args = parser.parse_args()

	input_filename = f'{parsed_args.input}.py'
	output_filename = f'{parsed_args.output}.py'


	with open(input_filename, 'r') as file:
		print(f'{Fore.GREEN}[+] Reading {input_filename}')
		original_code = libcst.parse_module(file.read())


	detect = DetectObfuscation()
	transformers = []

	# Detect obfuscator used
	original_code = original_code.visit(detect)
	detected_obfuscator = detect.obfuscator

	if not detected_obfuscator:
		print(f'{Fore.RED}[-] No supported obfuscator found. Is the code obfuscated?')

	else:
		print(f'{Fore.GREEN}[+] Detected Obfuscator: {detected_obfuscator}')

	if detected_obfuscator == 'Vare':
		transformers = [VareDeobfuscator()]

	for transformer in transformers:
		original_code  = original_code.visit(transformer)

	with open(output_filename, 'w', encoding = 'utf-8') as file:
		file.write(original_code.code)
		print(f'{Fore.GREEN}[+] Deobfuscation has completed {output_filename}')
