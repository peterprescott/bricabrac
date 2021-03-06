# bricabrac

Our Data Science team writes a lot of code in DataBricks notebooks,
which saves us having to waste too much time connecting our local
machines to the necessary data sources.

But it can be frustrating when trying to restructure notebook code as a
Python (sub)package.

Therefore I spent a Friday afternoon creating `bricabrac`, a simple CLI
tool to help make it painless to transfer Python packages to Databricks
notebooks.

`bricabrac` does three things:

1. It concatenates all the modules in a given folder into a
Databricks notebook (which is actually just a `.py` script, with
comments declaring it to be a Databricks notebook, and comments showing
where cells are separated). 

2. It also checks the dependencies between
modules, and does a graph `topological_sort` to make sure that when
treated just as cells in a notebook they are correctly ordered.

3. It also comments out any `import from` statements referring to other
modules in the same subpackage.

You can install it from this repo:

```
pip install git+https://github.com/peterprescott/bricabrac
```

Then navigate to the subpackage you and your team are working on, and
run `bricabrac` in your terminal.

```
cd $YOUR_SUBPACKAGE
bricabrac
```

and it will compile all the modules in that folder into a DataBricks
notebook named `_DBND_{subpackage_name}.py`.
