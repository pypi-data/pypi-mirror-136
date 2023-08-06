

#from __future__ import annotations

import typing

import jk_typing
import jk_version

from .ComposerToken import ComposerToken
from ._ComposerTokenPattern import _ComposerTokenPattern





class _ComposerTokenPatternSequence(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self, *patterns:typing.List[_ComposerTokenPattern]):
		assert len(patterns) > 0

		self.__patterns = patterns
		self.__patternLength = len(patterns)
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def tryMatch(self, tokens:typing.List[ComposerToken], pos:int) -> bool:
		selectedTokens = tokens[pos:pos+self.__patternLength]
		if len(selectedTokens) < self.__patternLength:
			return False
		for i in range(0, self.__patternLength):
			if not self.__patterns[i].tryMatch(selectedTokens[i]):
				return False
		return True
	#

#







