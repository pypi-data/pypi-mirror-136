

#from __future__ import annotations

import typing

import jk_typing
import jk_version

from .ComposerToken import ComposerToken





class _ComposerTokenPattern(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self, tokenType:str, text:str = None):
		self.__tokenType = tokenType
		self.__text = text
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

	def __str__(self):
		return "ComposerTokenPattern<{}, {}>".format(
			repr(self.__tokenType).replace("'", "\""),
			repr(self.__text).replace("'", "\"")
		)
	#

	def __repr__(self):
		return "ComposerTokenPattern<{}, {}>".format(
			repr(self.__tokenType).replace("'", "\""),
			repr(self.__text).replace("'", "\"")
		)
	#

	def tryMatch(self, token:ComposerToken) -> bool:
		assert isinstance(token, ComposerToken)

		if self.__tokenType != token.tokenType:
			return False
		if (self.__text is not None) and (self.__text != token.text):
			return False
		return True
	#

#







