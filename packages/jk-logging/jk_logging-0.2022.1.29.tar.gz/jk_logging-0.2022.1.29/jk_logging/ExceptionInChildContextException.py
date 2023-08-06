


#
# This class is used to provide an orderly retreat from nested log contexts.
#
class ExceptionInChildContextException(Exception):
	
	def __init__(self, originalExeption:Exception, exitCode:int = None):
		self.originalExeption = originalExeption
	#

#





