

from __future__ import annotations

import enum
import typing

import jk_version
import jk_prettyprintobj

from .ComposerToken import ComposerToken
from ._ComposerTokenPattern import _ComposerTokenPattern






class ComposerTokenStream(jk_prettyprintobj.DumpMixin):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	def __init__(self, tokens:typing.Sequence[ComposerToken]):
		self.__tokens = list(tokens)
		self.__pos = 0
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def isEOS(self) -> bool:
		return self.__pos >= len(self.__tokens)
	#

	@property
	def hasMoreData(self) -> bool:
		return self.__pos < len(self.__tokens)
	#

	@property
	def pos(self) -> int:
		return self.__pos
	#

	@property
	def remaining(self) -> int:
		return len(self.__tokens) - self.__pos
	#

	@property
	def remainingStr(self) -> str:
		_temp = []
		for t in self.__tokens[self.__pos:]:
			_temp.append(t.text)
		return " ".join(_temp)
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _dump(self, ctx:jk_prettyprintobj.DumpCtx):
		_lastLen = 0
		for i, t in enumerate(self.__tokens):
			m = i == self.__pos
			_sPrefix = ">" if m else " "
			_s1 = "{} token[{}]".format(_sPrefix, i)
			_lastLen = len(_s1)
			ctx.dumpVar(
				_s1,
				self.__tokens[i],
			)

		if self.__pos >= len(self.__tokens):
			ctx.dumpVar(
				"> " + " "*_lastLen,
				None,
			)
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __len__(self) -> int:
		return len(self.__tokens)
	#

	def __getitem__(self, ii:int) -> ComposerToken:
		return self.__tokens[ii]
	#

	def getRemaining(self, ii:int) -> ComposerToken:
		i = self.__pos + ii
		return self.__tokens[i]
	#

	def iterRemaining(self):
		return self.__tokens[self.__pos:].__iter__()
	#

	def __iter__(self):
		return self.__tokens.__iter__()
	#

	def splitMany(self, p:_ComposerTokenPattern) -> typing.List[ComposerTokenStream]:
		ret = []

		buffer = []
		for token in self.__tokens[self.__pos:]:
			if p.tryMatch(token):
				if buffer:
					ret.append(ComposerTokenStream(buffer))
				buffer.clear()
			else:
				buffer.append(token)
		if buffer:
			ret.append(ComposerTokenStream(buffer))

		return ret
	#

	def tryMatch(self, p:_ComposerTokenPattern) -> typing.Union[ComposerToken,None]:
		assert isinstance(p, _ComposerTokenPattern)

		# ----

		if self.__pos >= len(self.__tokens):
			return None

		t = self.__tokens[self.__pos]
		if p.tryMatch(t):
			return t
		return None
	#

	def tryMatchSequence(self, *pList:typing.List[_ComposerTokenPattern]) -> typing.Union[typing.List[ComposerToken],None]:
		assert isinstance(pList, tuple)
		for p in pList:
			assert isinstance(p, _ComposerTokenPattern)

		# ----

		if len(pList) == 0:
			raise ValueError("pList")

		tList = self.__tokens[self.__pos:]
		if len(tList) < len(pList):
			return None

		for i, p in enumerate(pList):
			t = tList[i]
			if not p.tryMatch(t):
				return None

		return tList[:len(pList)]
	#

	def advance(self, n:int):
		assert isinstance(n, int)
		assert n > 0

		self.__pos += n
	#

#







