'''Exceptions definitions'''


class TestGroupNotSetError(Exception):
  '''Test group property is not set'''
  pass



class TestNotFoundError(Exception):
  '''Test was not found in test definition configuration'''
  pass



class TestGroupDoesNotExistError(Exception):
  '''Test group was not found in test definition configuration'''
  pass
