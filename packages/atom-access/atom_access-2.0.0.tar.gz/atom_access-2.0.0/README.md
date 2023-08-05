`atom_access` is a python package for assessing the steric hindrance at any atom in a molecule or molecular fragment.

We request that any results obtained through the use of `atom_access` are accompanied by the following reference:
> A. J. McMillan, M. Sieńkowska, P. Di Lorenzo, G. K. Gransbury, N. F. Chilton, M. Salamone, A. Ruffoni, M. Bietti, D. Leonori, Angew. Chem. Int. Ed. **2021**, 60, 7132.

This code was developed under the ERC CoG-816268 grant with PI [David P. Mills](https://millsgroup.weebly.com/). We acknowledge Ken Gransbury for help conceptualising the `atom_access` logo. 

# Installation via `pip`

The easiest way to install atom_access is to use `pip`

```shell
pip install atom_access
```

some users, such as those on shared machines, may need to use the `--user` argument after `install`

# Updating via `pip`

Update the code using `pip` 

```shell
pip install --upgrade atom_access
```

some users, such as those on shared machines, may need to use the `--user` argument after `install`

# Usage

Use `atom_access -h` to see all available options

# Developers: Installation with `pip` editable install

Clone a copy of this repository, preferably while within a directory called git

```shell
mkdir -p git; cd git
git clone https://gitlab.com/jonkragskow/atom_access
```

Navigate to the package directory

```shell
cd atom_access
```

and install the package in editable mode

```shell
pip install -e .
```
some users, such as those on shared machines, may need to use the `--user` argument after `install`

To uninstall this editable copy, use

```shell
pip uninstall atom_access
```

# Building a `.whl` file (Advanced)

To build a copy of the `atom_access` `.whl` file, move to the `package` directory.

Now run

```shell
./build_binaries.sh
```

Then install the `.whl` file with `pip`

```shell
pip install dist/*.whl
```
some users, such as those on shared machines, may need to use the `--user` argument after `install`


# Documentation

The [documentation](https://jonkragskow.gitlab.io/atom_access/) for this package is hosted by gitlab, and is automatically generated whenever new code is committed to the `main` branch.

# Bugs

If you believe you have a bug, *please check that you are using the most up to date version of the code*. 

If that does not fix the problem, please create an issue on GitLab detailing the following:
 - The commands you entered
 - The error message

If possible, try to simplify the problem as much as possible, e.g. providing an example for a small molecule rather than one with 1000 atoms.
