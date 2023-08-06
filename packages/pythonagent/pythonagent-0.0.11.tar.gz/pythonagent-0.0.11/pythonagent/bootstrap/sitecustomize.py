"""Trick Python into loading the agent.

"""

from __future__ import unicode_literals
import os
import sys

try:
    sys.path.remove(os.path.dirname(__file__))
except ValueError:  # directory not in sys.path
    pass

try:
    import pythonagent.agent as agent
    agent.configure()
    agent.bootstrap()
except Exception as e:
    print('Exception in agent startup.', e)
finally:
    pass
