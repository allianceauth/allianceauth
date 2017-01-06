
# Alliance Auth

Alliance service auth to help large scale alliances manage services. Built for "The 99 Percent" open for anyone to use

# Installing

[Ubuntu Setup Guide](installation/auth/ubuntu.md)

For other distros, adapt the procedure and find distro-specific alternatives for the [dependencies](installation/auth/dependencies.md)

# Using

See the [Quick Start Guide](installation/auth/quickstart.md)

# Troubleshooting

Read the [list of common problems.](maintenance/troubleshooting.md)

# Upgrading

As AllianceAuth is developed, new features are added while old bugs are repaired. It’s good practice to keep your instance of AllianceAuth up to date.

Some updates require specific instructions. Refer to their entry in the [changelog](maintenance/changelog.md)

In general, the update process has 4 steps:
 - download the latest code
 - generate new models in the database
 - update current models in the database
 - rebuild web cache

To perform each of these steps, you’ll need to be working from the console in the AllianceAuth directory. Usually `cd ~/allianceauth`

Start by pulling the code changes:

    git pull

Modify settings.py according to the changelog.

For an automated upgrade, run the script:

    bash update.sh

For a manual upgrade, execute the commands in this order:

    sudo pip install -r requirements.txt

    python manage.py migrate

    python manage.py collectstatic


```eval_rst
.. toctree::
    :maxdepth: 3
    :caption: Contents

    features/index
    installation/index
    maintenance/index
    development/index
```
