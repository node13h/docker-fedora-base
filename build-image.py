#!/usr/bin/env python3

import argparse
import json
import logging
import os
import shlex
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def run(cmd: list, **kwargs):
    logger.debug("Executing {}".format(shlex.join(cmd)))

    return subprocess.run(cmd, check=True, text=True, **kwargs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_name")
    parser.add_argument("cache_name")
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"),
        help="log level",
    )

    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)

    cache_dir = Path("dnf-cache")

    cache_metadata_file = cache_dir.joinpath(f"{args.cache_name}.json")

    with open(cache_metadata_file, "r") as f:
        metadata = json.load(f)

    os.environ["SOURCE_DATE_EPOCH"] = str(metadata["epoch"])

    p = run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)

    vcs_ref = p.stdout.rstrip()

    cache_tarball_file = cache_dir.joinpath(f"{args.cache_name}.tar.gz")

    run(
        [
            "podman",
            "build",
            "--build-arg",
            "BASE_IMAGE={}".format(metadata["base-image"]),
            "--build-arg",
            "SOURCE_DATE_EPOCH={}".format(metadata["epoch"]),
            "--build-arg",
            "DNF_CACHE_TARBALL={}".format(cache_tarball_file),
            "--label",
            # https://github.com/opencontainers/image-spec/blob/main/annotations.md
            "com.alikov.image.ref={}".format(vcs_ref),
            "--label",
            "com.alikov.image.epoch={}".format(metadata["epoch"]),
            "--label",
            "com.alikov.image.base={}".format(metadata["base-image"]),
            "--label",
            "com.alikov.image.version={}".format(metadata["version"]),
            "--timestamp",
            str(metadata["epoch"]),
            "--format",
            "oci",
            "-t",
            "{}:{}-{}".format(args.image_name, metadata["version"], metadata["epoch"]),
            ".",
        ]
    )


if __name__ == "__main__":
    main()
