# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jobbatch']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['jobbatch = jobbatch.main:main']}

setup_kwargs = {
    'name': 'jobbatch',
    'version': '1.0.4',
    'description': 'A utility for splitting tasks up into batches',
    'long_description': "# JobBatch: Run batches of commands\n\n## Background\n\nJobBatch is a simple tool for queuing up batches of commands and running N of them at a time.\n\nThe initial use case was scheduling software updates on a large number of remote devices, without getting all the support queries back in the same day! So we wanted to update 100 devices each night.  But you might want to send 10 emails per minute, transcode 5 videos per hour, or whatever.  You can set up a cron job or similar to run `jobbatch`, and it will split the tasks into these chunks for you and run them. \n\n## Here's how it works.\n\nThe flow is managed using the filesystem.  You have a set of subdirectories:\n\n* queue\n* batch\n* successes\n* failures\n* output\n\nYou can put all of the jobs you want to run as individual files into the 'queue' directory.   If you have them as lines in a single file, you can use `jobbatch split` to turn it into one file per job. Often, each job file is a shell script, but it doesn't have to be (see below).\n\nEach time you want to run the next chunk of jobs, you do `jobbatch select` to take a selection of the files in the `queue` directory and *move* them into the `batch` directory.  You can then take a look to check that things look right, and if you don't like what you see, you can just move all the files back into the queue directory.  If the `queue` directory is empty, this command will do nothing.\n\nThen you run `jobbatch run`, which will execute those the jobs in the `batch` directory one at a time.  After execution, each file is moved to either `successes` or `failures` depending on its exit code.   If the `batch` directory is empty, this command will do nothing.\n\nAny standard output or error output from a job will be put in a file with a '.stdout' or '.stderr'  extension within the `output` directory.\n\nSo, to summarise, each file eventually goes from:\n\n`queue` -> `batch` -> `successes` or `failures` (possibly plus `output`)\n\n## Not just for scripts\n\nTypically, each job file will be a shell script or program to be executed.  \n\nIf the file has the 'executable' flag bit set, it will be executed directly.  If it doesn't, it will be passed as the argument to a processor such as `/bin/bash`, but you can change this with a command-line option.\n\nThis means, therefore, that the jobs *do not have to be scripts*.  Suppose you had a script for emailing thumbnails of your photographs to your friends, you could put the photographs into the 'queue' directory and specify your script as the processor, and then send them eight thumbnails per day.\n\nFor some tasks, the job files may not even need to have any contents, because the filename itself is the parameter.  You might just created empty files named after the serial numbers of the devices to be updated.   Note that `jobbatch run` will normally send the full pathname of the file to the processor, but there is an option just to send the base name within the subdirectory, if you wish to use it this way.\n\n\n## Author\n\nQuentin Stafford-Fraser\nJune 2022",
    'author': 'Quentin Stafford-Fraser',
    'author_email': 'quentin@pobox.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
