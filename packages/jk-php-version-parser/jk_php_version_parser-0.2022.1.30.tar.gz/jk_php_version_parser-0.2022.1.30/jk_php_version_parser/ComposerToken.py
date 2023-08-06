

#from __future__ import annotations

import jk_version






class ComposerToken(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	def __init__(self, tokenType:str, text:str):
		self.tokenType = tokenType
		self.text = text
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
		return "ComposerToken<{}, {}>".format(
			repr(self.tokenType).replace("'", "\""),
			repr(self.text).replace("'", "\"")
		)
	#

	def __repr__(self):
		return "ComposerToken<{}, {}>".format(
			repr(self.tokenType).replace("'", "\""),
			repr(self.text).replace("'", "\"")
		)
	#

	def __eq__(self, other) -> bool:
		if not isinstance(other, ComposerToken):
			return False
		return (other.tokenType == self.tokenType) and (other.text == self.text)
	#

	def __ne__(self, other) -> bool:
		if not isinstance(other, ComposerToken):
			return True
		return (other.tokenType != self.tokenType) or (other.text != self.text)
	#

#







