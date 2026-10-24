import argparse

from chainbreaker.scenarios.generator import write_central_district


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["seed-demo"])
    parser.add_argument("--directory", default="data/examples/central_district")
    args = parser.parse_args()
    if args.command == "seed-demo": write_central_district(args.directory)


if __name__ == "__main__":
    main()
