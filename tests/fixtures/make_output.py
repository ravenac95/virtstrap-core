"""
A file that outputs!
====================

This is simply a tool for testing. All it does is alternate output from 
'abcdef' to '123456'. It does this 2 times.
"""

def main():
    for x in xrange(2):
        print 'abcdef'
        print '123456'

if __name__ == '__main__':
    main()
