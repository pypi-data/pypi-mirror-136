'''
ypya.base
'''


class YBase(object):
    '''
    basic declaration
    '''

    INCLUDE_DEBUG_FIELD = True
    INCLUDE_EXTRA_FIELD = True
    INCLUDE_FULLY_QUALIFIED_NAME = False
    INCLUDE_LEVEL_SYMBOLIC_NAME = False

    def makePickle(self, record):
        '''
        public method

        :param record: (logging.LogRecord)
        :return: (stringified JSON)
        '''
        obj = self.payload_cls(
            record,
            parent=self
        )
        return obj.data
