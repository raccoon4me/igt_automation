from optparse import OptionParser


def parser():
    usage_array = []
    usage_array.append("python main_expire-tapes.py [-e environement] [-s server] [-d days] [-x password]")
    print usage_array
    print "".join(usage_array)
    parser = OptionParser(usage="".join(usage_array), version="0.1-1")
    print parser
    parser.add_option("-e", "--environement",
                      dest="environement",)
    parser.add_option("-s", "--servers",
                      dest="servers",)
    parser.add_option("-d", "--days",
                      dest="days")
    parser.add_option("-x", "--password",
                      dest="password")
    ## check not empty parser.add_options
    (opts, args) = parser.parse_args()
    return opts

def main():
    # Parser inputs
    opts = parser()
    print opts
    print opts.password

if __name__ == '__main__':
    main()
