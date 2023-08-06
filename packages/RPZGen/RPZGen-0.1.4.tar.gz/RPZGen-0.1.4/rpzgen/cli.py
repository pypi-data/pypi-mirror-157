import argparse
import sys
from .rpzlib import RPZLib, PolicyAction, RecordType
from signal import signal, SIGINT, SIGPIPE


def get_parser():
    parser = argparse.ArgumentParser(prog="rpzgen")

    parser.add_argument("-u", '--unique', dest='unique', action='store_true', default=False,
                        help="block unique domains instead of the whole zone")
    parser.add_argument("-z", "--zone", dest='zone', default="rpz.",
                        help="name of the rpz zone")
    parser.add_argument("-t", "--ttl", dest='ttl', default="300",
                        help="time to live for the DNS records")
    parser.add_argument("-i", "--input", dest='input', default=None,
                        help="path to input file (The default is stdin if omitted)")
    parser.add_argument("-o", "--output", dest='output', default=None,
                        help="path to output file (The default is stdout if omitted)")
    parser.add_argument("-a", "--action", dest='policy_action', default="nxdomain",
                        help=str({t.name.lower() for t in PolicyAction}))
    parser.add_argument("--local-data-type", dest='local_data_type', default="CNAME",
                        help="local data type (e.g. A, AAAA) for the 'local_data' policy action")
    parser.add_argument("--local-data", dest='local_data', default=None,
                        help="local data (e.g. example.org.) for the 'local_data' policy action")
    parser.add_argument("-m", "--mname", dest='mname', default=None,
                        help="primary master name server for this zone")
    parser.add_argument("-e", "--email", dest='email', default=None,
                        help="email address of the administrator responsible for this zone")
    parser.add_argument("--serial", dest='serial', default=None,
                        type=int, help="serial number for this zone")
    parser.add_argument("--refresh", dest='refresh', default=14400,
                        type=int, help="number of seconds after which secondary name servers should query the master for the SOA record")
    parser.add_argument("--retry", dest='retry', default=3600,
                        type=int, help="number of seconds after which secondary name servers should retry to request the serial number from the master if the master does not respond")
    parser.add_argument("--expire", dest='expire', default=1209600,
                        type=int, help="number of seconds after which secondary name servers should stop answering request for this zone if the master does not respond")
    parser.add_argument("--negative-ttl", dest='negative_ttl', default=3600,
                        type=int, help="time to live for purposes of negative caching")

    return parser


def run():
    def sigint_handler(signal_received, frame):
        sys.exit(130)

    def sigpipe_handler(signal_received, frame):
        output_stream.flush()
        sys.exit(0)

    signal(SIGINT, sigint_handler)
    signal(SIGPIPE, sigpipe_handler)

    parser = get_parser()
    args = parser.parse_args()

    input_stream = open(args.input) if args.input else sys.stdin
    output_stream = open(args.output, "w") if args.output else sys.stdout

    if input_stream.isatty():
        parser.print_help(sys.stderr)
        sys.exit(1)

    rpzlib = RPZLib(
        origin=args.zone,
        ttl=args.ttl,
        policy_action=PolicyAction[args.policy_action.upper()],
        policy_action_local_data_type=RecordType[args.local_data_type],
        policy_action_local_data=args.local_data,
        mname=args.mname,
        email=args.email,
        serial=args.serial,
        refresh=args.refresh,
        retry=args.retry,
        expire=args.expire,
        negative_ttl=args.negative_ttl
    )

    rpzlib.list2rpz_pipe(input_stream, output_stream, not args.unique)


if __name__ == "__main__":
    run()
