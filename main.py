import re
import os
import sys

maillog_path = '/etc/transport_blocked/def.txt'
transport_path = '/etc/postfix/transport.cf'

#set argument
if(len(sys.argv) == 4):
    _regex = sys.argv[1]
    _print_flag = sys.argv[2].lower()
    _reload_flag = sys.argv[3].lower()
else:
    print('Please enter the input. The format is as below')
    print('python /etc/transport_blocked/main.py [find_regex] [print_flag] [reload_flag]')
    print("ex) python /etc/transport_blocked/main.py 'Server busy. Please try again later from' y n")
    quit()

#make maillog_file
def init_maillog():
    os.system("mailq > {}".format(maillog_path))

#read maillog and return recipient_domain_list
def read_maillog():
    result = []
    #read maillog
    f= open(maillog_path,'r')
    maillogs = f.readlines()
    f.close()

    for i in range(0, len(maillogs)):
        _line = maillogs[i]
        #find regex
        regex = _regex
        _find = _line.find(regex)
        #check email format
        if _find != -1:
            next_line = maillogs[i+1]
            #check email format
            email_regex = '^\s+[\w\-\.]+@((?:[\w-]+\.)+[\w\-]{2,4})$'
            _parsed = parse_maillog(email_regex, next_line)
            if _parsed:
                result.append(_parsed[0].lower())
                if _print_flag == 'y':
                    print(_parsed[0])
    #delete duplicate
    _result = list(set(result))
    return _result

#parse the log by regex
def parse_maillog(pattern, log):
    #set regex flags (Multiline, Case Insensitvie)
    p = re.compile(pattern, re.M | re.I)
    parsed_log = p.findall(log)
    return parsed_log

#read transport.cf and return transport_domain_list
def read_transport():
    result = []
    #read transport.cf
    fin= open(transport_path,'r')
    maillogs = fin.readlines()

    fout = open(transport_path,'w')
    for i in range(0, len(maillogs)):
        _line = maillogs[i]
        # replace '\r\n' to '\n'
        fout.write(_line.replace('\r','\n'))
        if _line and _line[0] != '#' and _line[0] != '\n':
            #find domain
            regex = '^((?:[\w-]+\.)+[\w\-]{2,4}) .+$'
            _parsed = parse_maillog(regex, _line)
            if _parsed:
                result.append(_parsed[0].lower())
    fin.close()
    fout.close()
    return result

#write transport.cf without duplicate domain
def write_transport(input_domain_list, transport_domain_list):
    for i in input_domain_list:
        if i in transport_domain_list:
            print('This Domain is already registered in transport.cf : {}'.format(i))
        else:
            f= open(transport_path,'a')
            f.write('{} smtp:[10.10.9.162]:25]\n'.format(i))
            f.close()

#reload transport.cf
def reload_transport():
    os.system('postmap /etc/postfix/transport.cf')
    os.system('postfix reload')

#=================start main()======================
#make maillog_file
#init_maillog()
#read maillog and return recipient_domain_list
maillog_result = read_maillog()
#read transport.cf and return transport_domain_list
transport_result = read_transport()
#write transport.cf without duplicate domain
write_transport(maillog_result, transport_result)
#reload transport.cf
if _reload_flag == 'y':
    reload_transport()
