from sessions import Session, Sessions
from session_config import SessionConfig


if __name__ == '__main__':
    sc = SessionConfig()
    ss = Sessions(sc)
    print('{} sessions found'.format(len(ss)))
    if sc.long:
    	print(ss.print_long())
    elif sc.bare:
    	print(ss.print_bare())
    else:
    	print(ss)
