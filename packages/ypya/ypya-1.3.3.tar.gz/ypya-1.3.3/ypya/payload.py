'''
ypya.payload
'''
import json
import logging
import traceback


class GELFData(object):
    '''
    data type adapter for GELF
    '''
    SYSLOG_LEVELS = {
        logging.CRITICAL: 2,
        logging.ERROR: 3,
        logging.WARNING: 4,
        logging.INFO: 6,
        logging.DEBUG: 7,
    }

    SPECIAL_NAME_PREFIX = '_'
    GELF_VERSION_NUMBER = '1.1'

    BASIC_FIELDS = (
        'version',
        'timestamp',
        'host',
        'facility',
        'level',
        'short_message',
        'full_message',
    )
    OPTIONAL_FIELDS = (
        'level_name',
        '_logger',
        'file',
        'line',
        '_function',
        '_pid',
        '_thread_name',
        '_process_name',
    )

    def __init__(self, record, parent=None):
        '''
        :param record: (logging.LogRecord)
        :param parent: (obj)
        '''
        assert record is not None, 'invalid argument value'
        self.instance = record
        self.parent = parent

    @property
    def data(self):
        '''
        :return: (string/unicode)
        '''
        self.cache = dict()
        self.formatter = getattr(
            self.parent,
            'formatter',
            None
        )

        self.collect_basic_fields()
        self.add_optional_fields()

        # rval;
        rval = json.dumps(self.cache)
        return rval

    def collect_basic_fields(self):
        '''
        :return: (dict)
        '''
        self.cache['version'] = self.GELF_VERSION_NUMBER
        self.cache['timestamp'] = self.instance.created
        self.cache['level'] = self.SYSLOG_LEVELS.get(
            self.instance.levelno,
            self.instance.levelno
        )
        self.cache['host'] = self.parent.sender_host
        originator = self.parent.sender_name or self.instance.name
        self.cache['facility'] = originator

        self.cache['short_message'] = self.extract_short_message(
            self.instance
        )
        self.cache['full_message'] = self.extract_full_message(
            self.instance
        )

        return self.cache

    def add_optional_fields(self):
        '''
        :return: (dict)
        '''
        if self.parent.use_level_name:
            self.cache['level_name'] = logging.getLevelName(
                self.instance.levelno
            )

        if self.parent.sender_name is not None:
            self.cache['_logger'] = self.instance.name

        if self.parent.add_debug_field:
            self.cache['file'] = self.instance.pathname
            self.cache['line'] = self.instance.lineno
            self.cache['_function'] = self.instance.funcName
            self.cache['_pid'] = self.instance.process
            self.cache['_thread_name'] = self.instance.threadName

            pn = self.instance.processName
            if pn is not None:
                self.cache['_process_name'] = pn
        return self.cache

    def extract_short_message(self, obj):
        '''
        :param obj: (logging.LogRecord)
        :return: (string)
        '''
        if self.formatter is not None:
            msg = formatter.format(obj)
        else:
            msg = obj.getMessage()
        return msg

    def extract_full_message(self, obj):
        '''
        :param obj: (logging.LogRecord)
        :return: (string)
        '''
        if self.formatter is not None:
            msg = self.formatter.format(obj)
        else:
            if obj.exc_info:
                items = traceback.format_exception(*obj.exc_info)
                msg = '\n'.join(items)
            elif obj.exc_text:
                msg = obj.exc_text
            else:
                msg = obj.getMessage()
        return msg
