# Case Study: Bash Startup Profile
What's taking so long during shell startup?

Install the "profiler" by adding the following to your `~/.bashrc`:
https://github.com/felixhummel/configs/blob/543ed49ba8fb0710daa1387070c14f23e463f6ba/bash/bashrc#L1
Remember to restart the shell by running `exec $SHELL`.

Run the profiler and remember its output:
```
FH_BASH_PROFILE=1 bash -xic echo 2> ~/profile-bash.log
```

The contents of `~/profile-bash.log`. Look like this:
```
...
▬ .030573545	 source /etc/bash_completion
▬▬ .032003863	 . /usr/share/bash-completion/bash_completion
▬▬▬ .033734655	 BASH_COMPLETION_VERSINFO=(2 8)
...
```

Load this into a puddl schema:
```
./load.py ~/profile-bash.log
```

Run some queries:
```
puddl db shell bash_profile < query.sql
```
