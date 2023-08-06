from simple_ddl_parser import DDLParser
import logging

ddl = """create temp table tempevent(like event);

"""

result = DDLParser(ddl, log_level=logging.INFO).run(group_by_type=True)

import pprint
pprint.pprint(result) 
