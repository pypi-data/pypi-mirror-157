# tapyr-cmd

TAPyR-CMD is a bunch of command line tools to use with [TAPIR](https://github.com/tap-ir/tapir), based on on the [TAPyR](ttps://github.com/tap-ir/tapyr) python library.

The user documentation is available [here](https://tap-ir.github.io/#/?id=command-line).

## Installation

Install [TAPyR](ttps://github.com/tap-ir/tapyr) by following the instruction [installation](https://github.com/tap-ir/tapyr#installation) instruction.

Then :

```
git clone https://github.com/tap-ir/tapyr-cmd.git
cd tapyr-cmd
pip install .
```

To add bash completion support for the command : 

```
sudo cp tapyr-cmd-completion.bash /etc/bash_completion.d/ && sudo chmod 444 /etc/bash_completion.d/tapyr-cmd-completion.bash
```
