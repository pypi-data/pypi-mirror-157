"""Type definitions
"""


import collections


# A move vector, i.e. what heap is to be reduced and by how many straws
Move = collections.namedtuple('Move', 'heapnumber removecount')

# The error rate percentages can be defined for parties separately
ErrorRate = collections.namedtuple('ErrorRate', 'Computer Player')
