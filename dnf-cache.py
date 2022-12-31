#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from subprocess import PIPE, run
from time import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("new", "extract"))
    parser.add_argument(
        "image"
    )  # Base image for "new", or existing image for "extract"
    parser.add_argument("name")
    parser.add_argument("--version")
    args = parser.parse_args()

    p = run(
        ["skopeo", "inspect", f"docker://{args.image}"],
        stdout=PIPE,
        check=True,
        text=True,
    )

    image_metadata = json.loads(p.stdout)
    digest = image_metadata["Digest"]

    immutable_image = f"{args.image}@{digest}"

    do_refresh_flag = "1" if args.command == "new" else "0"

    if args.command == "new":
        metadata = {
            "base-image": immutable_image,
            "version": args.version,
            "epoch": int(time()),
        }
    elif args.command == "extract":
        metadata = {
            "base-image": image_metadata["Labels"]["com.alikov.image.base"],
            "version": image_metadata["Labels"]["com.alikov.image.version"],
            "epoch": int(image_metadata["Labels"]["com.alikov.image.epoch"]),
        }
    else:
        RuntimeError(f"Unsupported command {args.command}")

    p = run(
        [
            "podman",
            "create",
            "-e",
            "DO_REFRESH={}".format(do_refresh_flag),
            "-e",
            "SOURCE_DATE_EPOCH={}".format(metadata["epoch"]),
            "--entrypoint",
            "sh",
            immutable_image,
            "/get-dnf-cache.sh",
        ],
        stdout=PIPE,
        check=True,
        text=True,
    )

    container_id = p.stdout.rstrip()

    run(["podman", "cp", "get-dnf-cache.sh", f"{container_id}:/"], check=True)

    run(["podman", "start", "-a", container_id], check=True)

    try:
        cache_dir = Path("dnf-cache")

        cache_dir.mkdir(exist_ok=True)

        tarball_file = cache_dir.joinpath(f"{args.name}.tar.gz")

        run(
            [
                "podman",
                "cp",
                f"{container_id}:/build/dnf-cache.tar.gz",
                tarball_file,
            ],
            check=True,
        )
    finally:
        run(["podman", "rm", container_id], check=True)

    metadata_file = cache_dir.joinpath(f"{args.name}.json")

    with open(metadata_file, "w") as f:
        f.write(json.dumps(metadata, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
