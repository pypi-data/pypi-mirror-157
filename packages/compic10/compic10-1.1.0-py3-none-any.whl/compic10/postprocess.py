# -*- coding: utf-8 -*-
import re
from collections import defaultdict

DEBUG_EMULATOR = False
MAX_REGISTER_NUM = 14

WRITE_REG_COMMANDS = {'l', 'lb', 'ls', 'lr', 'move', 'peek', 'pop',
		'add', 'sub', 'mul', 'div', 'mod', 'sqrt', 'round',
		'trunc', 'ceil', 'floor', 'max', 'min', 'abs',
		'log', 'exp', 'rand', 'sin', 'cos', 'tan', 'asin',
		'acos', 'atan', 'slt', 'sltz', 'sgt', 'sgtz', 'sle',
		'slez', 'sge', 'sgez', 'seq', 'seqz', 'sne', 'snez',
		'sap', 'sapz', 'sna', 'snaz', 'sdse', 'sdns', 'and',
		'or', 'xor', 'nor', 'sdse'}

def is_regwrite(reg, cmd, params):
	return cmd in WRITE_REG_COMMANDS and params and reg == params[0]

def is_regread(reg, cmd, params):
	return len(params) > 1 and reg in params[1:]

class PostProcessor:
	# TODO: remove 'totalsteps' from 'emulate' method results and from 'fnccall' params in 'emulate', maybe not be used in future
	class SimpleVM:
		class EmulationError(Exception): pass
		class Stats:
			_collected = defaultdict(list)
			@staticmethod
			def _(s, v): PostProcessor.SimpleVM.Stats._collected[s].append(v)
			@staticmethod
			def max(s): return max(PostProcessor.SimpleVM.Stats._collected[s])
			@staticmethod
			def avg(s): return sum(PostProcessor.SimpleVM.Stats._collected[s]) / len(PostProcessor.SimpleVM.Stats._collected[s])
			@staticmethod
			def min(s): return min(PostProcessor.SimpleVM.Stats._collected[s])

		def __init__(self, pp):
			self.address = 0
			self.pp = pp
			self.code = self.pp._code.split("\n")
			self.max_call_depth = 4
			self.branch_max_steps = 24
			self._ra_stack = []
			self._second_candidate = None
			self._save_and_look_branches = False
			self._is_final_candidate = False

		def set_final_candidate(self):
			"""Set is_final candidate flag"""
			self._is_final_candidate = True

		def set_save_and_look_branches(self):
			"""Set save_and_look_branches flag"""
			self._save_and_look_branches = True

		def is_next_reg_usage_write(self, reg, address=-1):
			"""Return emulate results where will be write in reg"""
			faddress, cmd, params, steps, slen = self.find_next_reg_usage(reg, address)
			if not cmd:
				return False, False
			if is_regwrite(reg, cmd, params):
				return True, True
			return True, False

		def is_next_reg_usage_read(self, reg, address=-1):
			"""Return emulate results where will be read from reg"""
			def checker(a, c, p, s):
				nonlocal nocond_jump
				if reg in p:
					if is_regwrite(reg, c, p) and not is_regread(reg, c, p):
						if nocond_jump:
							# should be already final candidate because zero depth result
							return True
						# with zero depth will be final candidate
						self.set_save_and_look_branches()
						return True
					# read reg, any depth override final candidate
					self.set_final_candidate()
					return True
				if c in ("beqz", "beqzal", "bnez"):
					nocond_jump = False

			nocond_jump = True
			if address >= 0:
				self.update_code(address)
			r = self.emulate(checker)
			# recheck final candidate
			if not r[1] or (is_regwrite(reg, r[1], r[2]) and not is_regread(reg, r[1], r[2])):
				return False
			return True

		def find_next_reg_usage(self, reg, address = -1):
			"""Return emulate results where reg is accessed"""
			if address >= 0:
				self.update_code(address)
			a, c, p, s = self.emulate(lambda a, c, p, s: reg in p)
			return a, c, p, s, len(self._ra_stack)

		def get_code_line(self, line):
			"""Return code by line number"""
			return self.code[line]

		def update_code(self, address):
			"""Update code from associated PostProcessor and set new address for emulation"""
			self.code = self.pp._code.split("\n")
			self._ra_stack = []
			self.address = address

		def emulate(self, fnc, maxsteps=64, reverse=False, rareturn=False):
			"""Make simple emulation and return result marked by fnc"""
			def subemulate(maxsteps, rareturn=False, depth=0, cursteps=0, curstops=None):
				if DEBUG_EMULATOR:
					def dbg(s):
						print(f"DBG({totalsteps}-{depth}-{localsteps}): {s}")
				else:
					def dbg(s): pass

				def default_result():
					if DEBUG_EMULATOR and not depth:
						print(f"DBG: Total lines analyzed {len(stops)}")
					if candidate[0]:
						return candidate
					PostProcessor.SimpleVM.Stats._("localsteps-fail", localsteps)
					return self.address, "", [], totalsteps

				totalsteps = cursteps
				localsteps = 0
				candidate = self.address, "", [], totalsteps
				self._second_candidate = None
				stops = [] if curstops is None else curstops
				PostProcessor.SimpleVM.Stats._("depth", depth)

				dbg(f"EMULATE START {self.address} {maxsteps} {rareturn} {depth}")

				if depth > self.max_call_depth:
					return default_result()

				code = self.code
				while maxsteps > 0:
					if self.address >= len(code):
						if not depth and self._ra_stack:
							dbg(f"EMULATE INTERRUPTED(out of code, trying another ways) adr: {self.address}")
							self.address = self._ra_stack.pop()
							dbg(f"STACK=>{self.address}")
							dbg(f"NEWADDR=>{self.address}")
						else:
							dbg(f"EMULATE STOP(out of code) adr: {self.address}")
							return default_result()

					if self.address in stops:
						if not depth:
							while self.address in stops and self._ra_stack:
								dbg(f"EMULATE INTERRUPTED(current branching way already processed, trying another ways) {self.address}\t{code[self.address]}")
								self.address = self._ra_stack.pop()
								dbg(f"STACK=>{self.address}")
								dbg(f"NEWADDR=>{self.address}")
							if self.address in stops:
								dbg(f"EMULATE STOP(current branching way already processed) {self.address}\t{code[self.address]}")
								return default_result()
						else:
							dbg(f"EMULATE STOP(current branching way already processed) {self.address}\t{code[self.address]}")
							return default_result()
					stops.append(self.address)

					curaddress = self.address
					line = code[self.address]
					self.address += -1 if reverse else 1
					if not line:
						continue
					if line.endswith(":"):
						continue
					if line.startswith("#"):
						continue

					maxsteps -= 1
					localsteps += 1
					totalsteps += 1

					tokens = line.split()
					cmd = tokens[0]
					params = tokens[1:]
					dbg(f"{curaddress}\t{cmd}\t{params}")

					self._save_and_look_branches = False
					self._is_final_candidate = False
					if fnc(curaddress, cmd, params, totalsteps):
						candidate = curaddress, cmd, params, totalsteps
						dbg(f"EMULATE STOP(found) {candidate}")
						PostProcessor.SimpleVM.Stats._("localsteps-found", localsteps)
						return default_result()

					#TODO: need to refactor that
					if cmd in ("j", "jal"):
						if params[0] == "ra":
							if not self._ra_stack:
								dbg(f"EMULATE STOP(!ra_stack)")
								return default_result()
							self.address = self._ra_stack.pop()
							dbg(f"STACK=>{self.address}")
							dbg(f"NEWADDR=>{self.address}")
							if rareturn:
								dbg(f"EMULATE STOP(rareturn)")
								return default_result()
						else:
							try:
								idx = code.index(params[0]+":")
							except:
								raise PostProcessor.SimpleVM.EmulationError(f"Cant find label '{params[0]}' for jump")

							if cmd == 'jal':
								self._ra_stack.append(self.address)
								dbg(f"STACK<={self.address}")
							dbg(f"NEWADDR=>{idx}")
							self.address = idx
					elif cmd in ("beqz", "beqzal", "bnez"):
						if params[1] == "ra":
							if not self._ra_stack:
								dbg(f"EMULATE STOP(!ra_stack)")
								return default_result()
							self.address = self._ra_stack.pop()
							dbg(f"STACK=>{self.address}")
							dbg(f"NEWADDR=>{self.address}")
							if rareturn:
								dbg(f"EMULATE STOP(rareturn)")
								return default_result()
						else:
							try:
								idx = code.index(params[1]+":")
							except:
								raise PostProcessor.SimpleVM.EmulationError(f"Cant find label '{params[1]}' for jump")

							if cmd == 'beqzal':
								self._ra_stack.append(self.address)
								dbg(f"STACK<={self.address}")
							dbg(f"NEWADDR=>{idx}")
							adr = self.address
							self.address = idx
							res = subemulate(self.branch_max_steps, True, depth + 1, totalsteps, stops)
							dbg(f"SUBEMULATE EXIT {depth} {res}")
							if res[1]:
								dbg(f"FOUND CANDIDATE INSIDE COND JUMP {res}")
								if self._is_final_candidate:
									return res
								if candidate[1]:
									if candidate[:-1] != res[:-1]:
										self._second_candidate = res
										if not self._save_and_look_branches:
											return candidate
								else:
									# replace only empty candidate
									candidate = res

							totalsteps = res[3]
							self.address = adr
							dbg(f"NEWADDR=>{self.address}")

				dbg(f"EMULATE STOP(out of steps) {localsteps} {self.address}")
				return default_result()

			result = subemulate(maxsteps, rareturn)
			if result[1]:
				PostProcessor.SimpleVM.Stats._("totalsteps-found", result[3])
			else:
				PostProcessor.SimpleVM.Stats._("totalsteps-fail", result[3])
			return result

	def __init__(self, pd, asm_code):
		self.pd = pd
		self.asm_code = asm_code
		self._code = self.asm_code
		self._initialized = False
		self._finalized = False

	def initialize(self):
		self._pre_optimize()
		self._initialized = True

	def iterate(self):
		if not self._initialized:
			self.initialize()
		clen = len(self._code)
		self._code = "\n" + self._code + "\n"
		self._optimize()
		return clen != len(self._code)

	def finalize(self):
		r = self._post_optimize()
		self._finalized = True
		return r

	def get_lines_count(self):
		return self._code.count("\n") - 1

	def get_final_code(self):
		if not self._finalized:
			self.finalize()
		return self._code

	def _pre_optimize(self):
		# fix all infinite while loops
		self.resub("(while_\d+_start:\n)move (r\d+) 1.\nbeqz \\2 while_\d+_end\n", "\\1")

		# fix main loop looking in common case
		c = self._code = "\n" + self._code
		if c.split("\n")[-1] == "while_0_end:":
			self.repl("\nwhile_0_end:", "\n") # remove unused line
			if c.find("\nmain:\n") < 0:
				# main not exists, do main loop as main
				self.repl("\nwhile_0_start:\n", "\nmain:\n")
				self.repl("\nj while_0_start\n", "\nj main\n")
			elif c.find("\nmain:\nwhile_0_start:\n") >= 0:
				# main exists, but same label as while_0_start
				self.repl("\nmain:\nwhile_0_start:\n", "\nmain:\n")
				self.repl("\nj while_0_start\n", "\nj main\n")
			else:
				self.repl("while_0_start", "mainloop")
				self.repl("j while_0_start", "j mainloop")
		self._code = self._code[1:]

		# replace to correct unconditional jump, need for other checks
		self.repl("beqz 0 ra", "j ra")

	def _optimize(self):
		def regcheck(reg, replace, codelen=2):
			def wrapper(match):
				if not vm.is_next_reg_usage_read(reg, self.get_address_from_pos(match.regs[0][0]) + codelen):
					if callable(replace):
						return replace(match)
					return match.expand(replace)
				return match.group()
			return wrapper

		vm = PostProcessor.SimpleVM(self)

		# fix double jumps
		# j for_0_iter
		# j end_if_0
		self.resub("(\nj .+\n)j .+\n", "\\1")

		# fix duble labels
		# end_if_0_block_0:
		# end_if_0:
		for match in re.finditer("\n.+:\n.+:\n", self._code, re.MULTILINE):
			labels = match.group(0).replace(':', '').split("\n")
			if labels[1].find(labels[2]) == 0:
				self.repl(f" {labels[2]}\n", f" {labels[1]}\n")
				self.repl(match.group(0), f"\n{labels[1]}:\n")
			else:
				new_label = labels[1] + "_" + labels[2]
				self.repl(f" {labels[1]}\n", f" {new_label}\n")
				self.repl(f" {labels[2]}\n", f" {new_label}\n")
				self.repl(match.group(0), f"\n{new_label}:\n")

		# fix jumps in next line
		# j end_if_1_block_0
		# end_if_1_block_0:
		self.resub("\nj (.+)\n\\1:\n", "\n\\1:\n")

		# clear not used labels
		for match in re.finditer("\n[\w\d_]+:\n", self._code, re.MULTILINE):
			label = match.group().replace(":", "").split("\n")[1]
			if self._code.find(f" {label}\n") < 0:
				self.repl(match.group(), "\n")

		# !!! do not join loops to single loop, replaces should be processed in that order for success
		for r in range(MAX_REGISTER_NUM):
			for rr in range(r, MAX_REGISTER_NUM):  # start from r
				# fix assign same reg
				# move r3 r4
				# move r4 r3
				# ------------
				# nor r4 0 r4
				# move r4 r4
				self.repl(f"\nmove r{r} r{rr}\nmove r{rr} r{r}\n", f"\nmove r{r} r{rr}\n")

				# fix or+and can be evaluated easily
				# or r6 r1 r7
				# move r1 r6
				self.resub(f"\n(or|and|nor) r{rr} r{r} (r\d+)\nmove r{r} r{rr}\n", f"\n\\1 r{r} r{r} \\2\n")

				# nor r4 0 r1
				# move r3 r4
				# disable that because have mistakes
				# self.resub(f"\nnor r{rr} 0 r{r}\nmove (r\d+) r{rr}\n", f"\nnor \\1 0 r{r}\n")
				#for match in re.finditer(f"\nnor r{rr} 0 r{r}\nmove (r\d+) r{rr}\n", self._code, re.MULTILINE):
				#	self.mrepl(match, f"\nnor {match.group(1)} 0 r{r}\n")

				# move r3 r4
				# sleep r4
				self.resub(f"(\nmove r{r} r{rr}\n[\d \w-]+) r{rr}\n", f"\\1 r{r}\n")

		# optimize code like this:
		# move r1 0.
		# move r0 r1
		# move r2 0.
		# move r1 r2
		# move r3 0.
		# move r2 r3
		for r in range(MAX_REGISTER_NUM):
			self.resub(f"\nmove r{r} ([\d.-]+)\n(move[\w\d -]+) r{r}\n", regcheck(f"r{r}", "\n\\2 \\1\n"))

		for r in range(MAX_REGISTER_NUM):
			# move r4 2.
			# sleep r4
			self.resub(f"\nmove r{r} ([\d.-]+)\n([\w\d -]+) r{r}\n", regcheck(f"r{r}", "\n\\2 \\1\n"))

		# optimize code like this:
		# move r3 r0
		# sb 1514476632 On r3
		# move r3 r0
		# sb 1436121888 On r3
		for r in range(MAX_REGISTER_NUM):
			for rr in range(0, r):  # max = r
				self.resub(f"\nmove r{r} r{rr}\n(.*) r{r}\n", regcheck(f"r{r}", f"\n\\1 r{rr}\n"))

		for r in range(MAX_REGISTER_NUM):
			for rr in range(0, r + 1):  # max = r
				# optimize check condition:
				# nor r3 0 r3
				# beqz r3 end_if_0_block_0
				self.resub(f"\nnor r{r} 0 r{rr}\nbeqz r{r} (end_if_\d+_block_\d+)\n", f"\nbnez r{rr} \\1\n")

				# l r2 d4 On
				# move r1 r2
				self.resub(f"\n(l? )r{r}( d[b\d] [\w\d]+)\nmove r{rr} r{r}\n", regcheck(f"r{r}", f"\n\\1r{rr}\\2\n"))

				# abs r4 r4
				# move r3 r4
				self.resub(f"\n([\w\d]+ )r{r} r{r}\nmove r{rr} r{r}\n", regcheck(f"r{r}", f"\n\\1 r{rr} r{r}\n"))

				# sgt r5 0.67 r2
				# move r4 r5
				# lb r5 -2113838091 Pressure Maximum
				self.resub(f"\n([\w\d]+ )r{r} ([r\d.-]+ [r\d.-]+)\nmove r{rr} r{r}\n", regcheck(f"r{r}", f"\n\\1r{rr} \\2\n"))

				# lb r2 -1252983604 RatioNitrogen Maximum
				# move r1 r2
				self.resub(f"\nlb r{r} ([\w\d -]+)\nmove r{rr} r{r}\n", regcheck(f"r{r}", f"\nlb r{rr} \\1\n"))

				# move r4 r0
				# beqz r4 end_if_4_block_0
				self.resub(f"\nmove r{r} r{rr}\n(beqz|bnez) r{r} (.+)\n", regcheck(f"r{r}", f"\n\\1 r{rr} \\2\n"))


		# ===========================================
		# emulator based optimizations
		# remove garbage push ra-pop ra due call proc\func
		for match in re.finditer("\ncallable_\d+:\n", self._code, re.MULTILINE):
			addr = self.get_address_from_pos(match.regs[0][0])
			vm.update_code(addr)
			pushra = vm.emulate(lambda a, c, p, s: "ra" in p or c in ("jal", "beqzal", "bnezal"))
			if pushra[1] != "push":
				continue
			saveaddr = vm.address

			# check for ra changed inside proc, continue emulation
			popra = vm.emulate(lambda a, c, p, s: "ra" in p or c in ("jal", "beqzal", "bnezal"))
			if popra[1] != "pop":
				continue

			# check for another pop ra inside proc, continue emulation from saveaddr
			# if function have multiply returns its also have multiply 'pop ra', but find all problematic
			# also that problem appears in recursive funcs\procs
			# next problem is sometimes compiler return result of func in RA
			# so now just skip functions like this
			# TODO: I cant solve that now, need new logic there for that ( example1.ic10lang in tests can be used for investigate)
			vm.address = saveaddr
			popra2 = vm.emulate(lambda a, c, p, s: "ra" in p and c == "pop" and a != popra[0])
			if popra2[1] == "pop":
				continue

			self.repl_line(pushra[0])  # remove push line
			self.repl_line(popra[0]) # remove pop line

		# remove garbage push rX pop rX due call
		for match in re.finditer("\npush r\d+(\n(jal|beqzal|bnezal) callable_\d+\n)", self._code, re.MULTILINE):
			addr = self.get_address_from_pos(match.regs[0][0])

			# collect pushed regs
			pushregs = {}
			def addpushreg(a, c, p, s):
				if c == "push":	pushregs[p[0]] = min(a, pushregs.get(p[0], 1000000))
				else:			return True
			vm.update_code(addr)
			vm.emulate(addpushreg, reverse=True)

			# collect saved registers
			savereg = {}
			def checkreg(a, c, p, s):
				if a == addr + 2:
					return True
				if p and p[0] in pushregs and is_regwrite(p[0], c, p):
					#del pushregs[p[0]]
					savereg[p[0]] = a
			vm.update_code(addr + 1)
			vm.emulate(checkreg)

			popregs = {}
			def addpopreg(a, c, p, s):
				if c == 'pop' and p[0] in pushregs:
					popregs[p[0]] = a
				elif c != 'pop':
					return True
			vm.update_code(addr + 2)
			vm.emulate(addpopreg)

			#exclude: by saved regs readed after func call
			for reg in savereg:
				if reg in popregs and vm.is_next_reg_usage_read(reg, popregs[reg] + 1):
					del pushregs[reg]

			if not pushregs:
				continue

			# removecode
			for reg in pushregs:
				if reg not in popregs:
					continue
				# !remove only pairs!
				self.repl_line(popregs[reg])  # remove pop line
				self.repl_line(pushregs[reg])  # remove push line

		# remove garbage move rX digit push rX pre call
		for match in re.finditer("\npush r\d+(\n(jal|beqzal|bnezal) callable_\d+\n)", self._code, re.MULTILINE):
			addr = self.get_address_from_pos(match.regs[0][0])

			# collect pushed regs
			pushregs = {}
			moves = {}
			def addreg(a, c, p, s):
				if c == "push":
					pushregs[p[0]] = a
				elif c == "move":
					if p[0] in pushregs and p[0] not in moves and p[1][0].isdigit():
						moves[p[0]] = a, f"push {p[1]}"
				else:
					return True
			vm.update_code(addr)
			vm.emulate(addreg, reverse=True)

			# exclude: check regs for reading after func
			for r in list(pushregs.keys()):
				if vm.is_next_reg_usage_read(r, addr + 2):
					del pushregs[r]

			# exclude: check reg have pop after call (move r6 10; push r6; ...call.. ; pop r6)
			def checkreg(a, c, p, s):
				if c == 'pop' and p[0] in pushregs:
					del pushregs[p[0]]
				elif c != 'pop':
					return True
			if pushregs and moves:
				vm.update_code(addr + 2)
				vm.emulate(checkreg)

			for r in pushregs:
				if r not in moves:
					continue
				self.repl_line(pushregs[r], moves[r][1])
				self.repl_line(moves[r][0])

		# cleanup removes (\n\n... => \n)
		self.remove_empty()

	def _post_optimize(self):
		return True

	def repl(self, f, t):
		self._code = self._code.replace(f, t)

	def resub(self, p, r, flags=re.MULTILINE):
		self._code = re.sub(p, r, self._code, 0, flags)

	def get_address_from_pos(self, pos):
		return self._code[:pos].count("\n") + 1

	def repl_line(self, index, s=""):
		lines = self._code.split('\n')
		lines[index] = s
		self._code = "\n".join(lines)

	def remove_empty(self):
		self._code = "\n".join(filter(None, self._code.split('\n')))




