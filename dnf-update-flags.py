#!/usr/bin/env python3

import argparse
import logging
import shlex
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def run(cmd: list, **kwargs):
    logger.debug("Executing {}".format(shlex.join(cmd)))

    return subprocess.run(cmd, check=True, text=True, **kwargs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("output_file", type=Path)
    parser.add_argument("--var-prefix", default="")
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"),
        help="log level",
    )

    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)

    p = run(["podman", "pull", args.image])

    p = run(
        [
            "podman",
            "create",
            "--entrypoint",
            "sh",
            "-e",
            "VAR_PREFIX={}".format(args.var_prefix),
            args.image,
            "/get-dnf-update-flags.sh",
        ],
        stdout=subprocess.PIPE,
    )

    container_id = p.stdout.rstrip()

    run(["podman", "cp", "get-dnf-update-flags.sh", f"{container_id}:/"])

    run(["podman", "start", "-a", container_id])

    try:
        run(
            [
                "podman",
                "cp",
                f"{container_id}:/output/vars",
                str(args.output_file),
            ],
        )
    finally:
        run(["podman", "rm", container_id])


if __name__ == "__main__":
    main()
