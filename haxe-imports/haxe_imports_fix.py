#!/usr/bin/env python

'''
Attempt to automatically add missing imports given a list of src folders
'''
import argparse
import glob
import json
import os, os.path
import re
import string
import sys

#Caches
path_to_symbol_set = {} #[path][symbol] = True
path_to_package = {} #[path] = "package foo;"
symbol_to_path = {} #[symbol] = "/sfsf/sdfsdf/foo/Bar"
haxe_symbol_to_import_def = {} #[symbol] = 'package.foo.Bar'
haxe_files = {} #[partial path] = full path.
haxe_files_to_classname = {} #[partial path] = 'Foo'
haxe_files_to_base = {} #[partial path] = '/some/dir/src'
haxe_files_sorted = []
dryrun = False
src_paths_read_only = {}
existing_imports = {}
ignored_symbols = {'Void':True, 'Float':True, 'Int':True, 'String':True}

def appendLibraryPath(libDef, paths):
	tokens = libDef.split(':')
	library = tokens[0]
	version = None if len(tokens) <= 1 else tokens[1]
	if os.path.exists('.haxelib'):
		libPath = os.path.join('.haxelib', library)
		if version:
			libPath = os.path.join('.haxelib', library, version.replace('.', ','))

		libHaxelibPath = os.path.join(libPath, 'haxelib.json')
		if not os.path.exists(libHaxelibPath):
			libHaxelibPath = os.path.join(libPath, 'git', 'haxelib.json')

		if os.path.exists(libHaxelibPath):
			libPath = os.path.dirname(libHaxelibPath)
			with open(libHaxelibPath) as json_data:
				d = json.load(json_data)
			srcPath = os.path.join(libPath, d['classPath']) if 'classPath' in d else libPath
			paths.append({'p':srcPath, 'ro':True})

def getSourcePathBlob(sourcePath):
	blob = {'p':sourcePath, 'ro':False}
	gitCheckPath = sourcePath
	while len(gitCheckPath) > 2:
		if os.path.exists(os.path.join(gitCheckPath, '.git')):
			blob['ro'] = True
			break
		gitCheckPath = os.path.dirname(gitCheckPath)
	return blob

def appendHaxeSourcePaths(hxml, paths):
	with open(hxml, 'r') as hxmlFile:
		lines = hxmlFile.readlines()
	for line in lines:
		line = line.strip()
		if line.endswith('.hxml'):
			appendHaxeSourcePaths(line, paths)
		elif line.startswith('-cp'):
			sourcePath = line.replace('-cp', '').strip()
			blob = getSourcePathBlob(sourcePath)
			paths.append(blob)
		elif line.startswith('-lib'):
			appendLibraryPath(line.replace('-lib', '').strip(), paths)

def recursivelyGatherHaxeSourcePaths(hxml='build.hxml'):
	# paths = []
	paths = [{'p':'/usr/local/lib/haxe/std/', 'ro':True}]
	# if os.environ['HAXE_LIBRARY_PATH'] and os.path.exists(os.environ['HAXE_LIBRARY_PATH']):
	# 	paths.append({'p':os.environ['HAXE_LIBRARY_PATH'], 'ro':True})
	appendHaxeSourcePaths(hxml, paths)
	return paths

# It is more efficient to create a lot of cached maps
def createCaches(srcs):
	for srcBlob in srcs:
		src = srcBlob['p']
		readOnly = srcBlob['ro']
		dir_full_path = os.path.join(os.getcwd(), src)

		for root, dirs, files in os.walk(dir_full_path):
			if root.endswith('_std'):
				continue
			for file in files:
				if file.endswith(".hx") and not file.endswith('import.hx'):
					fullPath = os.path.join(root, file)
					# print('%s %s' % (root, fullPath))
					className = getClassNameFromPath(fullPath)
					#basePath is relative to the src path
					basePath = fullPath.replace(dir_full_path, '')
					if basePath.startswith('/'):
						basePath = basePath[1:len(basePath)]

					importDef = basePath.replace('.hx', '').replace('/', '.')
					if importDef.startswith('.'):
						importDef = importDef[1:len(importDef)]
					existing_imports[importDef] = True
					symbol = importDef.split('.')[len(importDef.split('.')) - 1]
					# if symbol in symbol_to_path:
					# 	continue
					haxe_symbol_to_import_def[symbol] = importDef
					if not (basePath in path_to_symbol_set):
						path_to_symbol_set[basePath] = {}
					path_to_symbol_set[basePath][symbol] = True
					haxe_files[basePath] = fullPath
					# Do not include library files for processing
					# But include them for other maps
					if not readOnly:
						haxe_files_sorted.append(basePath)
					symbol_to_path[symbol] = fullPath
					haxe_files_to_classname[basePath] = symbol
					haxe_files_to_base[basePath] = dir_full_path
					path_to_package[basePath] = "package " + importDef.replace("." + symbol, ";\n")
	haxe_files_sorted.sort()

def getHaxeFilePackage(fullpath):
	with open(fullpath, 'r') as haxeSrcFile:
		sourceLines = haxeSrcFile.readlines()

	for i in range(len(sourceLines)):
		line = sourceLines[i]
		if line.startswith('package '):
			return line.replace('package', '').replace(';', '').strip()

def getClassNameFromPath(classPath):
	classPath = classPath.replace('.hx', '').replace('/', '.')
	nameTokens = classPath.split('.')
	classname = nameTokens[len(nameTokens) - 1]
	return classname

def isSymbolInDir(symbol, directory):
	# print('isSymbolInDir %s %s' % (symbol, directory))
	files = os.listdir(directory)
	symbolFile = symbol + '.hx'
	return symbolFile in files

getImportHxFilesCache = {}
def getImportHxFiles(rootDir, baseDir):
	if os.path.join(rootDir, baseDir) in getImportHxFilesCache:
		return getImportHxFilesCache[os.path.join(rootDir, baseDir)]
	currentDir = baseDir
	importHxFiles = []
	while currentDir != None:
		files = os.listdir(os.path.join(rootDir, currentDir))
		if 'import.hx' in files:
			importHxFiles.append(os.path.join(currentDir, 'import.hx'))
		if currentDir == '':
			currentDir = None
		else:
			currentDir = os.path.dirname(currentDir)
	getImportHxFilesCache[os.path.join(rootDir, baseDir)] = importHxFiles
	return importHxFiles

cacheHxImportToContent = {}
cacheHxImportToSymbolExistsMap = {}
def checkImportHxForImport(importHxPath, importString):
	if not (importHxPath in cacheHxImportToSymbolExistsMap):
		cacheHxImportToSymbolExistsMap[importHxPath] = {}
	if importString in cacheHxImportToSymbolExistsMap[importHxPath]:
		return cacheHxImportToSymbolExistsMap[importHxPath][importString]

	if not (importString in cacheHxImportToContent):
		with open(importHxPath, 'r') as importFile:
			importContentString = importFile.read()
		cacheHxImportToContent[importHxPath] = importContentString

	importContent = cacheHxImportToContent[importHxPath]
	pattern = re.compile(importString)
	exists = pattern.search(importContent) != None

	if exists:
		cacheHxImportToSymbolExistsMap[importHxPath][importString] = exists
		return exists

	#Check for wildcard versions e.g. promhx.*
	importString = importString.split('.')
	importString.pop()
	importString = string.join(importString, '.') + '.*'
	pattern = re.compile(importString)
	exists = pattern.search(importContent) != None

	if exists:
		cacheHxImportToSymbolExistsMap[importHxPath][importString] = exists
		return exists

	cacheHxImportToSymbolExistsMap[importHxPath][importString] = exists
	return exists

#For example, in an import.hx, or the class is in the same dir, or parent dir
def isSymbolImportedInParent(symbol, srcPath, sourceString):
	#First check for the class in this and parent directories
	#since these are available to the class
	baseDir = haxe_files_to_base[srcPath]
	currentDir = os.path.dirname(srcPath)
	while currentDir != None:
		if isSymbolInDir(symbol, os.path.join(baseDir, currentDir)):
			return True
		if currentDir == '':
			currentDir = None
		else:
			currentDir = os.path.dirname(currentDir)

	#Then check that the symbol isn't already imports
	existingImportPattern = re.compile(haxe_symbol_to_import_def[symbol])
	match = existingImportPattern.search(sourceString)
	if match:
		return True

	#Then check the symbol isnt' imported in a import.hx file
	for importHx in getImportHxFiles(baseDir, os.path.dirname(srcPath)):
		if checkImportHxForImport(os.path.join(baseDir, importHx), haxe_symbol_to_import_def[symbol]):
			return True

	return False

def ensureImports(srcPath, symbols):
	print('[%s] Ensuring missing imports: [%s]' % (srcPath, symbols))
	srcFullPath = haxe_files[srcPath]
	for symbol in symbols:
		importDef = haxe_symbol_to_import_def[symbol]
		importLine = 'import %s;\n' % (importDef)
		importHxPath = os.path.join(os.path.dirname(srcFullPath), 'import.hx')
		if os.path.exists(importHxPath):
			print('[%s]        Added to [%s] [%s] NOT YEEEET' % (srcPath, importHxPath, importLine.strip()))
		else:
			#Actually add it to the source file in question
			#Try put the import in a sensible place (with other imports, sorted)
			with open(srcFullPath, 'r') as haxeSrcFile:
				sourceLines = haxeSrcFile.readlines()
			packageLine = -1
			importStartLine = -1
			importEndLine = -1
			for i in range(len(sourceLines)):
				line = sourceLines[i]
				if line.startswith('package'):
					packageLine = i
				if line.startswith('import') or line.startswith('using '):
					if importStartLine == -1:
						importStartLine = i
					importEndLine = i
			if importStartLine > -1:
				added = False
				for i in range(importStartLine, importEndLine + 1):
					if sourceLines[i] > importLine:
						sourceLines.insert(i, importLine)
						added = True
						break
				if not added:
					sourceLines.insert(importEndLine + 1, importLine)

			elif packageLine > -1:
				sourceLines.insert(packageLine + 1, importLine)
			else:
				sourceLines.insert(0, importLine)

			if not dryrun:
				with open(srcFullPath, 'w') as haxeSrcFile:
					haxeSrcFile.writelines(sourceLines)

			print('[%s]        Added directly to the src [%s]' % (srcPath, importLine.strip()))

def getSymbolFromImport(importString):
	importString = importString.replace('import', '').replace('using', '').replace(';', '').strip()
	importTokens = importString.split('.')
	return importTokens[len(importTokens) - 1]

def getPackageFromImport(importString):
	return importString.replace('import', '').replace('using', '').replace(';', '').strip()

commentRegex = re.compile(r'\s*[\*[\/]')
def addMissingHaxeImports():
	for srcPath in haxe_files_sorted:
		fullpath = haxe_files[srcPath]
		with open(fullpath, 'r') as haxeSrcFile:
			sourceLines = haxeSrcFile.readlines()
		className = haxe_files_to_classname[srcPath]
		#Search file for any occurances of the symbols
		required_imports = {}
		imported_symbols = {}
		for symbol, importDef in haxe_symbol_to_import_def.iteritems():
			if className == symbol:
				continue
			if symbol in ignored_symbols:
				continue
			# print('Looking for %s in %s' % (symbol, fullpath))
			pattern = re.compile(r"((.*[<>\s:]+)|(^))\s*" + symbol + r"[<>\.\s;:].*", re.MULTILINE)
			for line in sourceLines:
				if line.startswith('import') or line.startswith('using '):
					imported_symbols[getSymbolFromImport(line)] = True
					continue
				if commentRegex.search(line):
					continue
				if pattern.search(line):
					required_imports[symbol] = True

		if required_imports.keys():
			required_imports = [s for s in required_imports.keys() if not isSymbolImportedInParent(s, srcPath, string.join(sourceLines, ''))]
			required_imports = [s for s in required_imports if not s in imported_symbols]
			if required_imports:
				ensureImports(srcPath, required_imports)

def fixExistingHaxeImports():
	for srcPath in haxe_files_sorted:
		fullpath = haxe_files[srcPath]
		with open(fullpath, 'r') as haxeSrcFile:
			sourceLines = haxeSrcFile.readlines()
		className = haxe_files_to_classname[srcPath]
		#Search for existing imports
		with open(fullpath, 'r') as haxeSrcFile:
			sourceLines = haxeSrcFile.readlines()

		changed = False
		for i in range(len(sourceLines)):
			line = sourceLines[i]
			if line.startswith('import ') or line.startswith('using '):
				package = getPackageFromImport(line)
				if not package in existing_imports:
					importpackage = package
					importTokens = importpackage.split('.')
					# Since we do not (yet) look at the std lib,
					# for now assume that haxe imports are valid
					# since they won't be in your local src folders
					if importTokens[0] != 'haxe':
						importSymbol = importTokens[len(importTokens) - 1]
						if not (importSymbol in ignored_symbols):
							if importSymbol in haxe_symbol_to_import_def and haxe_symbol_to_import_def[importSymbol] != importpackage:
								changed = True
								sourceLines[i] = 'import %s;\n' % haxe_symbol_to_import_def[importSymbol]
								print('[%s] import fixed:  [%s] -> [%s]' % (srcPath, line.strip(), sourceLines[i].strip()))

		if changed and not dryrun:
			with open(fullpath, 'w') as haxeSrcFile:
				haxeSrcFile.writelines(sourceLines)

def fixPackageDefinition():
	for srcPath in haxe_files_sorted:
		fullpath = haxe_files[srcPath]
		with open(fullpath, 'r') as haxeSrcFile:
			sourceLines = haxeSrcFile.readlines()

		changed = False
		for i in range(len(sourceLines)):
			line = sourceLines[i]
			if line.startswith('package '):
				if line != path_to_package[srcPath]:
					sourceLines[i] = path_to_package[srcPath]
					changed = True
					print('[%s] package fixed:  [%s] -> [%s]' % (srcPath, line.strip(), path_to_package[srcPath].strip()))
					break

		if changed and not dryrun:
			with open(fullpath, 'w') as haxeSrcFile:
				haxeSrcFile.writelines(sourceLines)

# Guess where the src paths are based on finding haxe src
# and looking at the package
def findHaxeSrcPaths():
	rootSrcPaths = {}
	for root, dirs, files in os.walk(os.getcwd()):
		for file in files:
			if root in rootSrcPaths:
				break
			if file.endswith(".hx") and not file.endswith('import.hx'):
				fullPath = os.path.join(root, file)
				package = getHaxeFilePackage(fullPath)
				dirPath = os.path.dirname(fullPath)
				if package:
					packageTokens = package.split('.')
					while len(packageTokens) > 0:
						dirPath = os.path.dirname(dirPath)
						packageTokens.pop()

				rootSrcPaths[dirPath.replace(os.getcwd() + '/', '')] = True
				break

	rootSrcPathsList = rootSrcPaths.keys()
	rootSrcPathsList.sort()
	return rootSrcPathsList

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Fix imports in haxe source files')
	parser.add_argument('-x', '--hxml',
		help='Root hxml file [build.hxml]')
	parser.add_argument('-s', '--src',
		help='haxe source path',
		action='append')
	parser.add_argument('-d', '--dryrun',
		dest='dryrun',
		action='store_true',
		help='Dry run, no files modified')
	parser.add_argument('-v', '--verbose',
		dest='verbose',
		action='store_true',
		help='Verbose logs')
	parser.add_argument('-f', '--file',
		help='Check only listed haxe classes',
		action='append')
	parser.add_argument('-i', '--ignoresymbol',
		help='Ignore imports for given symbol',
		action='append')
	parser.add_argument('-p', '--packagesonly',
		dest='packagesonly',
		action='store_true',
		help='Fix package statements only')
	parser.add_argument('-n', '--nolib',
		dest='nolib',
		action='store_true',
		help='Ignore symbols in libraries (This speeds up processing when doing local refactors')

	parser.set_defaults(dryrun=False)
	parser.set_defaults(dryrun=False)
	parser.set_defaults(hxml='build.hxml')

	args = parser.parse_args()
	dryrun = args.dryrun
	if dryrun:
		print('DRYRUN: not modifying any files')
	srcs = recursivelyGatherHaxeSourcePaths(args.hxml)
	if args.src:
		for s in args.src:
			srcs.append(getSourcePathBlob(s))

	if args.nolib:
		srcs = [s for s in srcs if not s['ro']]
	if args.verbose:
		print('Sources:')
		for s in srcs:
			print('    %s\t\t\t%s' % ('writable' if not s['ro'] else '        ', s['p']))

	if args.ignoresymbol:
		for i in args.ignoresymbol:
			ignored_symbols[i] = True

	createCaches(srcs)

	if args.file:
		def mapFileToExistingHaxeFile(f):
			for h in haxe_files_sorted:
				if h.replace('.hx', '').endswith(f.replace('.hx', '')):
					return h
			print('Could not find haxe file %s' % (f))
			sys.exit(1)
		haxe_files_sorted = map(mapFileToExistingHaxeFile, args.file)

	if args.packagesonly:
		fixPackageDefinition()
	else:
		addMissingHaxeImports()
		fixExistingHaxeImports()
		fixPackageDefinition()
