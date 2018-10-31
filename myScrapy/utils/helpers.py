import re

def format_str(s):
    '''
    去除字符串中的特殊字符
    '''
    if not s:
        return ''
    return re.sub('[\r\t\n\u3000 ]', '', s)
