import logging

logger = logging.getLogger(__name__)

class _Debug:
    COLORS = {
        "DEBUG": "\033[94m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
    }
    STAT2COL = {
        "SOURCE": COLORS["DEBUG"],
        "PARSING": COLORS["WARNING"],
        "SUCCEEDED": COLORS["INFO"],
        "FAILED": COLORS["ERROR"]
    }
    CALLSTACK_WIDTH = 120
    counter = 0
    @classmethod
    def color(cls, s, c):
        return f"{c}{s}\033[0m"
    @classmethod
    def debug(cls, status: str, source: str, callstack: list = None):
        cls.counter += 1
        callstack = callstack or []
        callstack_str = ""
        if callstack:
            page = 0
            callstack_str = str(callstack[0])
            for call in callstack[1:]:
                callstack_str += f" -> {str(call)}"
                if len(callstack_str) > cls.CALLSTACK_WIDTH:
                    page += 1
                    callstack_str = f"({page})".ljust(4) + "-> " + str(call)
        logger.debug(str(cls.counter).ljust(6) + str(len(callstack)).ljust(4) + cls.color(f'{status.ljust(20)} {callstack_str.ljust(cls.CALLSTACK_WIDTH)[:cls.CALLSTACK_WIDTH]} "{source}"', cls.STAT2COL[status]))

def init(Parser, Source):
    logging.basicConfig(level=logging.DEBUG)
    _debug = _Debug.debug
    
    si = Source.__init__
    
    def source_init(self, source, offset=0):
        si(self, source, offset)
        _Debug.counter = 0
        _debug("SOURCE", source)
        self.callstack = []
    
    Source.__init__ = source_init
    
    p = Parser.parse
    
    # we inject the following code into the parser
    def parse(self, source: Source):
        # if self.name is None: return self._parse(source)
        source.callstack.append(self)
        offset = source.offset
        _debug("PARSING", source.source[offset:].replace("\n", " ")[:30], source.callstack)
        parse_result = p(self, source)
        if parse_result is not None:
            _debug("SUCCEEDED", source.source[offset:source.offset], source.callstack)
        else:
            _debug("FAILED", source.source[offset:source.offset], source.callstack)
        source.callstack.pop()
        return parse_result
    
    Parser.parse = parse
