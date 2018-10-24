import re

def format_str(s):
    '''
    去除字符串中的特殊字符
    '''
    return re.sub('[\r\t\n ]', '', s)
