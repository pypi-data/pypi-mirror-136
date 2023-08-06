

#from __future__ import annotations

import os
import typing
import re

import jk_typing
import jk_version

from .ImplementationErrorException import ImplementationErrorException
from .ComposerToken import ComposerToken

from .ComposerTokenStream import ComposerTokenStream





class ComposerVersionTokenizer(object):

	__PATTERNS = [
		">=",
		"<=",
		"||",
		">",
		"<",
		"~",
		"^",
		" ",
		"\t",
	]

	__REGEX_PATTERN = re.compile("^(\s+-\s+)")

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

	#
	# Break into fragments. Space characters are skipped entirely.
	#
	def __tokenize(self, text:str) -> typing.Sequence[ComposerToken]:
		iLast = 0
		i = 0
		while i < len(text):
			textSpan = text[i:]

			# ----

			m = ComposerVersionTokenizer.__REGEX_PATTERN.match(textSpan)
			if m:
				if i > iLast:
					yield ComposerToken("v", text[iLast:i])

				sMatch = m.group(1)
				yield ComposerToken("op", "-")

				i += len(sMatch)
				iLast = i
				continue

			# ----

			bFound = False
			for p in ComposerVersionTokenizer.__PATTERNS:
				if textSpan.startswith(p):
					if i > iLast:
						yield ComposerToken("v", text[iLast:i])

					bThisIsSpace = p.isspace()
					if bThisIsSpace:
						pass
					else:
						yield ComposerToken("op", p)

					i += len(p)
					iLast = i
					bFound = True
					break
			if bFound:
				continue

			# ----

			i += 1

		if iLast < len(text):
			yield ComposerToken("v", text[iLast:])
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def tokenize(self, text:str) -> ComposerTokenStream:
		assert isinstance(text, str)

		text = text.strip()
		return ComposerTokenStream(self.__tokenize(text))
	#

#







