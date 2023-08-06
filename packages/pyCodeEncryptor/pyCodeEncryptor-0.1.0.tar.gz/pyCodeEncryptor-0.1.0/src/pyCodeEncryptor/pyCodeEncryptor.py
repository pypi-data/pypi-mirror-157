class wrongCodeFormat(Exception):
	pass

key={'a': 'c', 'b': 'ç', 'c': 'd', 'ç': 'e', 'd': 'f', 'e': 'g', 'f': 'ğ', 'g': 'h', 'ğ': 'ı', 'h': 'i', 'ı': 'j', 'i': 'k', 'j': 'l', 'k': 'm', 'l': 'n', 'm': 'o', 'n': 'ö', 'o': 'p', 'ö': 'r', 'p': 's', 'r': 'ş', 's': 'u', 'ş': 'ü', 'u': 'v', 'ü': 'y', 'v': 'z', 'y': 'a', 'z': 'b',
"\"":"~","~":"(","(":"\"",
")":"=","=":"?","?":")",
"\n":"&","&":":",":":"\n",
" ":"%","%":"$","$":" "}


def encrypt(file,out):
	"""
	Encrypt a py file!

	Use:
		pyEncryptor.encrypt("file.py","newFile.py")
	"""
	codeFile=open(file,"r")
	code=codeFile.read()
	codeFile.close()
	if type(code)!=str:
		raise wrongCodeFormat("The codes to be encrypted can only be in string form.")
	nc=""
	for i in code:
		try:
			nc=nc+key[i]
		except KeyError:
			nc=nc+i
	outFile=open(out,"w")
	outFile.write(nc)
	outFile.close()
def runCode(code):
	"""
	Run a encrypted code!

	Use:
		pyEncryptor.runCode(code)
	"""
	if type(code)!=str:
		raise wrongCodeFormat("The codes to be encrypted can only be in string form.")
	dc=""
	for i in code:
		try:
			dc=dc+list(key.keys())[list(key.values()).index(i)]
		except ValueError:
			dc=dc+i

	exec(dc)