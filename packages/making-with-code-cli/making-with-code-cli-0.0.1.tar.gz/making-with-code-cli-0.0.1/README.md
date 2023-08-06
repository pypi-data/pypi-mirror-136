# MWC CLI

## Development


From the project root, create a virtual environment and install the
dependencies. Then follow 
[Click's documentation](https://click.palletsprojects.com/en/8.0.x/#documentation), 
and install the cli as an editable distribution.

```
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ pip install --editable mwc_cli
$ mwc ---help
```

Initial proposed flow:

In the flow below:

- MWC is initialized with a name and email address. These will be used with git,
  and git credentials are used as defaults. Since no host is given, localhost is
  assumed as the server URL.
- Create a new course and populate with student info from a CSV file. The
  `--distribute` flag means also create a distribution of the course.
- 

```
$ mwc init --username chris --email chris@chrisproctor.net
$ mwc course new cs9 --roster students.csv --distribute
$ mwc course list
cs9:
 - cs9-0
$ mwc assignment new drawing --repo https://github.com/the-isf-academy/drawing --course cs9-0 --distribute
$ mwc assignment init drawing-0
$ mwc assignment status drawing
Name    Repo                                                Commits    Milestones
------  ------------------------------------------------  ---------  ------------
Jacob   https://github.com/the-isf-academy/drawing-jacob          5             3
Jenny   https://github.com/the-isf-academy/drawing-jenny          6             2
Chris   https://github.com/the-isf-academy/drawing-chris          2             0
$
```

## WIP 2021-08-11

The next thing I need to do is build a way to import course, unit, and
assignment data. To do this, I need to get the MWC hugo site building its json
correctly. 

Then I can work on deploying an assignment

Cloning student repos with the right permissions
Pushing updates to student repos
Organizing the backlog of repos and the backlog of labs

mwc assignment import http://cs.fablearn.org/courses/cs9/unit00/project/networking.yaml

mwc assignment deploy --name Networking --section CS10.A --dryrun

mwc assignment status --name Networking
