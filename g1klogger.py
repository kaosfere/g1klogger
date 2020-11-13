import argparse
import sys
import time

import simdata


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outfile", action="store")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.outfile:
        handle = open(args.outfile, "w")
    else:
        handle = sys.stdout

    conn = simdata.Connection(0)

    handle.write(
        '#airframe_info, log_version="1.00", airframe_name="Beechcraft A36/G36", unit_software_part_number="006-B0319-9C", unit_software_version="11.12", system_software_part_number="006-B0858-08", system_id="", mode=NORMAL,\n'
    )
    handle.write(", ".join([x.unit.rjust(x.width) for x in conn.variables]) + "\n")
    handle.write(", ".join([x.name.rjust(x.width) for x in conn.variables]) + "\n")
    while True:
        last = time.time()
        try:
            handle.write(
                ", ".join([x.value.rjust(x.width) for x in conn.variables]) + "\n"
            )
        except (TypeError, AttributeError):
            pass
        duration = time.time() - last
        if duration < 1:
            sleeptime = 1 - duration
            time.sleep(sleeptime)


if __name__ == "__main__":
    main()
