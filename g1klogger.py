import argparse

import simdata
import simdata.formats


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", action="store")
    parser.add_argument("--g1000", action="store")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.raw:
        out_raw = open(args.raw, "wb")

    if args.g1000:
        out_g1000 = open(args.g1000, "w")

    g1000 = simdata.formats.G1000()
    status = simdata.formats.SimpleDict()

    if args.g1000:
        out_g1000.write(f"{g1000.header}\n")

    dumper = simdata.Dumper()
    for msg in dumper.dumper(proplist=g1000.proplist):
        print(status.parse(msg))
        if args.raw:
            out_raw.write(msg)
        if args.g1000:
            out_g1000.write(g1000.parse(msg))


if __name__ == "__main__":
    main()
