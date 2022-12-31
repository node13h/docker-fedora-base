#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
from subprocess import PIPE, run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_name")
    parser.add_argument("cache_name")
    args = parser.parse_args()

    cache_dir = Path("dnf-cache")

    cache_metadata_file = cache_dir.joinpath(f"{args.cache_name}.json")

    with open(cache_metadata_file, "r") as f:
        metadata = json.load(f)

    os.environ["SOURCE_DATE_EPOCH"] = str(metadata["epoch"])

    p = run(["git", "rev-parse", "HEAD"], stdout=PIPE, check=True, text=True)

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
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
