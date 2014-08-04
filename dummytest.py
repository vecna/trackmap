import perform_analysis
import libtrackmap
import sys
import random

if len(sys.argv) > 1:
    dest = sys.argv[1]
    perform_analysis.do_trace("test_%d" % random.randint(0, 0xfff), dest)
else:
    perform_analysis.do_trace("test_%d" % random.randint(0, 0xffff), 'www.youtube.com')
