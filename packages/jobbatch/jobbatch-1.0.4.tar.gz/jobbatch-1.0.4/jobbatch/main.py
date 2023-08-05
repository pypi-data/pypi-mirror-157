#! /usr/bin/env python3

import argparse
import os
import random
import shutil
import subprocess


verbosity = 1
base_dir = "."


def _dir_path(path: str) -> str:
    "Return the full pathname of the given working dir"
    return os.path.join(base_dir, path)


def _dir_list() -> list[str]:
    # Return a list of all our working directories
    return [_dir_path(d) for d in ["queue", "batch", "successes", "failures", "output"]]


def init(args):
    """
    Create our working directories if they don't exist.
    """
    for d in _dir_list():
        if verbosity:
            print(f"Checking/creating directory {d}")
        os.makedirs(d, exist_ok=True)


def split(args):
    """
    Read lines from one or more source files and create jobs
    in the queue.
    """
    count = 0
    prev_base = None
    for src in args.source_file:
        base, _ = os.path.splitext(os.path.basename(src))
        if base != prev_base:
            count = 0
        if verbosity:
            print(f"Reading {src}")
        with open(src, "r") as fp:
            for line in fp.readlines():
                job_file = os.path.join(_dir_path("queue"), f"{base}_{count}")
                with open(job_file, "w") as outfp:
                    outfp.write(line)
                if verbosity > 1:
                    print(f"Creating {job_file}")
                count += 1


def select(args):
    """
    Move a subset into the 'batch' directory
    """
    queue_dir = _dir_path("queue")
    batch_dir = _dir_path("batch")
    queue_files = sorted(os.listdir(queue_dir))
    queue_size = len(queue_files)
    if verbosity:
        print(f"Selecting up to {args.batch_size} jobs from the queue of {queue_size}.")
    actual_number = min(args.batch_size, queue_size)

    if args.random:
        if verbosity > 1:
            print(f"Using a randomly-selected batch of {actual_number}.")
        selection = random.sample(queue_files, actual_number)
    else:
        if verbosity > 1:
            print(f"Selecting the first {actual_number} jobs alphabetically.")
        selection = queue_files[:actual_number]

    if verbosity:
        print(f"Moving {len(selection)} jobs.")
    for job in selection:
        full_src = os.path.join(queue_dir, job)
        if verbosity > 1:
            print(f"Move {full_src} to {batch_dir}")
        shutil.move(full_src, batch_dir)


def run(args):
    """
    Execute the jobs in the batch
    """
    batch_dir = _dir_path("batch")
    success_dir = _dir_path("successes")
    failure_dir = _dir_path("failures")
    output_dir = _dir_path("output")
    batch_files = sorted(os.listdir(batch_dir))
    batch_size = len(batch_files)
    if verbosity:
        print(f"Running {len(batch_files)} jobs from the batch.")
    for job in batch_files:
        full_src = os.path.join(batch_dir, job)
        if verbosity > 1:
            print(f"Running {full_src}")
        # if job is executable, it can be run directly, 
        # otherwise use the slected or default argument processor
        cmd = [full_src] if os.access(full_src, os.X_OK) else [args.processor, full_src]
        cp = subprocess.run(cmd, capture_output=True)

        # Save the output
        if cp.stdout:
            with open(os.path.join(output_dir, f"{job}.stdout"), "wb") as fp:
                fp.write(cp.stdout)
        if cp.stderr:
            with open(os.path.join(output_dir, f"{job}.stderr"), "wb") as fp:
                fp.write(cp.stderr)
        
        # And file the job away to the appropriate directory
        success = (cp.returncode == 0)
        shutil.move(full_src, success_dir if success else failure_dir)
        if verbosity > 1:
            if success:
                print(f"{full_src} executed successfully and moved to {success_dir}")
            else:
                print(f"{full_src} had a non-zero exit code; moved to {failure_dir}")


def clean(args):
    for d in _dir_list():
        if verbosity:
            print(f"Emptying directory {d}")
        for files in os.listdir(d):
            path = os.path.join(d, files)
            try:
                shutil.rmtree(path)
            except OSError:
                os.remove(path)


# The majority of the following is argument-parsing and help info.

def main():
    parser = argparse.ArgumentParser(
        description="Split jobs up into batches, and run them."
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        type=int,
        default=1,
        help="specify output verbosity [0-3, default %(default)s]",
    )
    parser.add_argument(
        "-d",
        "--directory",
        default=".",
        help="specify an alternative to the current directory to use as a base",
    )
    subparsers = parser.add_subparsers(
        title="commands", help="Command help available: use -h after command.",
        required=True
    )


    parser_init = subparsers.add_parser(
        "init", 
        description="Create the standard subdirectories if they don't already exist.",
        help="set up the standard subdirectories"
    )
    parser_init.set_defaults(func=init)


    parser_split = subparsers.add_parser(
        "split", 
        description="Split the lines of a single file into multiple job files in 'queue'.",
        help="split a single file into multiple job files in 'queue'"
    )
    parser_split.add_argument("source_file", nargs="+")
    parser_split.set_defaults(func=split)


    parser_select = subparsers.add_parser(
        "select",
        description="Choose a subset of the jobs in 'queue' and move them into 'batch'",
        help="choose a subset of the jobs in 'queue' and move them into 'batch'",
    )
    parser_select.add_argument(
        "-r",
        "--random",
        action="store_true",
        help="pick a random batch, rather than the first alphabetically",
    )
    parser_select.add_argument("batch_size", type=int, help="size of batch")
    parser_select.set_defaults(func=select)


    parser_run = subparsers.add_parser(
        "run", 
        description="Run the jobs in 'batch', moving them to 'successes' or 'failures' based on exit code.", 
        help="run the jobs in 'batch'"
    )
    parser_run.add_argument(
        "-p",
        "--processor",
        default="/bin/bash",
        help="specify a program to which the jobs will be given as arguments if not executable",
    )
    parser_run.set_defaults(func=run)


    parser_clean = subparsers.add_parser(
        "clean", 
        description="Empty all the working directories without prompting (use with care!)",
        help="empty all the directories (use with care)"
    )
    parser_clean.set_defaults(func=clean)

    args = parser.parse_args()

    global verbosity, base_dir
    verbosity = args.verbosity
    base_dir = args.directory

    args.func(args)


if __name__ == "__main__":
    main()
