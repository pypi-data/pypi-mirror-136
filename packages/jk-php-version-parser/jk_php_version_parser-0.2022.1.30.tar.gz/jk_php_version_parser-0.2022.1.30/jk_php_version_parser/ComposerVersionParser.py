

#from __future__ import annotations

import os
import typing
import re

import jk_typing
import jk_version

from .ImplementationErrorException import ImplementationErrorException
from .ComposerToken import ComposerToken
from ._ComposerTokenPattern import _ComposerTokenPattern
from .ComposerTokenStream import ComposerTokenStream
from .ComposerVersionTokenizer import ComposerVersionTokenizer






class ComposerVersionParser(object):

	__TOKENIZER = ComposerVersionTokenizer()

	__MATCH_GT = (
		_ComposerTokenPattern("op", ">"),
		_ComposerTokenPattern("v", None),
	)

	__MATCH_GE = (
		_ComposerTokenPattern("op", ">="),
		_ComposerTokenPattern("v", None),
	)

	__MATCH_LT = (
		_ComposerTokenPattern("op", "<"),
		_ComposerTokenPattern("v", None),
	)

	__MATCH_LE = (
		_ComposerTokenPattern("op", "<="),
		_ComposerTokenPattern("v", None),
	)

	__MATCH_RANGE = (
		_ComposerTokenPattern("v", None),
		_ComposerTokenPattern("op", "-"),
		_ComposerTokenPattern("v", None),
	)

	__MATCH_CARET = (
		_ComposerTokenPattern("op", "^"),
		_ComposerTokenPattern("v", None),
	)

	__MATCH_TILDE = (
		_ComposerTokenPattern("op", "~"),
		_ComposerTokenPattern("v", None),
	)

	__MATCH_VERSION = _ComposerTokenPattern("v", None)

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	def __init__(self):
		pass
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	@jk_typing.checkFunctionSignature()
	def __eatOne(self, tokenStream:ComposerTokenStream) -> jk_version.BaseVersionConstraint:
		for patternList, clazz in (
				(	ComposerVersionParser.__MATCH_GE,	jk_version.VersionConstraintGE,		),
				(	ComposerVersionParser.__MATCH_GT,	jk_version.VersionConstraintGT,		),
				(	ComposerVersionParser.__MATCH_LE,	jk_version.VersionConstraintLE,		),
				(	ComposerVersionParser.__MATCH_LT,	jk_version.VersionConstraintLT,		),
			):

			tokens = tokenStream.tryMatchSequence(*patternList)
			if tokens:
				assert len(tokens) == 2
				tokenStream.advance(len(tokens))
				v = jk_version.Version(tokens[1].text)
				return clazz(v)

		# ----

		tokens = tokenStream.tryMatchSequence(*ComposerVersionParser.__MATCH_RANGE)
		if tokens:
			assert len(tokens) == 3
			tokenStream.advance(len(tokens))
			v1 = jk_version.Version(tokens[0].text)
			v2 = jk_version.Version(tokens[2].text)
			return jk_version.VersionConstraintAND(
				jk_version.VersionConstraintGE(v1),
				jk_version.VersionConstraintLT(v2),
			)

		# ----

		tokens = tokenStream.tryMatchSequence(*ComposerVersionParser.__MATCH_CARET)
		if tokens:
			assert len(tokens) == 2
			tokenStream.advance(len(tokens))
			v1 = jk_version.Version(tokens[1].text)
			_numbers2 = v1.numbers
			if _numbers2[0] == 0:
				_numbers2[1] += 1
				for i in range(2, len(_numbers2)):
					_numbers2[i] = 0
			else:
				_numbers2[0] += 1
				for i in range(1, len(_numbers2)):
					_numbers2[i] = 0
			v2 = jk_version.Version(_numbers2, _epoch=v1.epoch)
			return jk_version.VersionConstraintAND(
				jk_version.VersionConstraintGE(v1),
				jk_version.VersionConstraintLT(v2),
			)

		# ----

		tokens = tokenStream.tryMatchSequence(*ComposerVersionParser.__MATCH_TILDE)
		if tokens:
			assert len(tokens) == 2
			tokenStream.advance(len(tokens))
			v1 = jk_version.Version(tokens[1].text)
			_numbers2 = v1.numbers
			if len(_numbers2) <= 1:
				raise Exception("Parsing error: {} is not a valid tilde version.".format(repr(tokens[1].text)))
			_numbers2[-1] = 0
			_numbers2[-2] += 1
			v2 = jk_version.Version(_numbers2, _epoch=v1.epoch)
			return jk_version.VersionConstraintAND(
				jk_version.VersionConstraintGE(v1),
				jk_version.VersionConstraintLT(v2),
			)

		# ----

		t = tokenStream.tryMatch(ComposerVersionParser.__MATCH_VERSION)
		if t is not None:
			tokenStream.advance(1)
			if t.text.endswith(".*"):
				v1 = jk_version.Version(t.text[:-2] + ".0")
				_numbers2 = v1.numbers
				if len(_numbers2) <= 2:
					raise Exception("Parsing error: {} is not a valid wildcard version.".format(repr(tokens[1].text)))
				_numbers2[-2] += 1
				v2 = jk_version.Version(_numbers2, _epoch=v1.epoch)
				return jk_version.VersionConstraintAND(
					jk_version.VersionConstraintGE(v1),
					jk_version.VersionConstraintLT(v2),
				)
			else:
				v = jk_version.Version(t.text)
				return jk_version.VersionConstraintEQ(v)

		# ----

		raise Exception("Parsing error at: " + tokenStream.remainingStr)
	#

	@jk_typing.checkFunctionSignature()
	def __compileStream(self, tokenStream:ComposerTokenStream) -> jk_version.VersionConstraintAND:
		ret = []

		while tokenStream.hasMoreData:
			c = self.__eatOne(tokenStream)
			ret.append(c)

		return jk_version.VersionConstraintAND(*ret)
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def parse(self, text:str) -> jk_version.BaseVersionConstraint:
		tokenStream = ComposerVersionParser.__TOKENIZER.tokenize(text)

		# now we have a sequence of tokens. spaces have been removed already.

		# ----

		andGroups = tokenStream.splitMany(_ComposerTokenPattern("op", "||"))

		# now we have a list of elements that represent either a single condition or an AND condition.
		# these are all grouped and collected in 'orGroups'.

		# ----

		gOr = []
		for andGroup in andGroups:
			gOr.append(self.__compileStream(andGroup))
		ret = jk_version.VersionConstraintOR(*gOr)

		# ----

		return ret.simplify()
	#

#







