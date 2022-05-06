"""
Painless tranformation of subpackage modules into Databricks notebook.
"""

import ast
import os
import re
from pathlib import Path

import networkx as nx


class Module:
    def __init__(self, filename, subpackage_path):
        self.filename = filename
        self.name = self.filename.replace(".py", "")
        self.subpackage = Path(subpackage_path).stem
        self.filepath = os.path.join(subpackage_path, filename)
        with open(self.filepath, "r") as f:
            self.source = f.read()
        self.ast = ast.parse(self.source)
        self.dependencies = self._get_import_dependencies()

    def __repr__(self):
        return self.name

    def _get_import_dependencies(self):
        importfroms = [p for p in self.ast.body if isinstance(p, ast.ImportFrom)]
        dependencies = [
            i.module.split(".")[-1] for i in importfroms if self.subpackage in i.module
        ]

        return dependencies


class SubPackage:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.modules = self._get_ordered_modules()

    def _get_ordered_modules(self):
        self._ls = os.listdir(os.path.join(self.path, self.name))
        self._modules = [
            Module(f, os.path.join(self.path, self.name))
            for f in self._ls
            if f.split(".")[-1] == "py" and "DBNB" not in f
        ]
        g = nx.DiGraph()
        for m in self._modules:
            for d_name in m.dependencies:
                [d] = [m for m in self._modules if m.name == d_name]
                g.add_edge(d, m)
        self.modules = [m for m in nx.topological_sort(g)]
        self.modules.extend([m for m in self._modules if m not in self.modules])
        return self.modules

    def _get_databricks_notebook(self):
        db_nb = "# Databricks notebook source\n"
        for m in self.modules:
            db_nb += f"\n# {m.name}.py\n"
            db_nb += self._comment_out_subpackage_imports(m)
            db_nb += "\n# COMMAND ----------\n"
        return db_nb

    def _comment_out_subpackage_imports(self, module):
        commented_out_source = module.source
        import_lines = re.findall(
            rf"from data_science_common.{self.name}\..*", module.source
        )

        for line in import_lines:
            if line[-1] == "(":
                [line] = re.findall(
                    rf"{re.escape(line)}.*?\)", module.source, re.DOTALL
                )
            comment_out_for_db_nb = "#~DB~# "
            commented_out_lines = "\n".join(
                [comment_out_for_db_nb + l for l in line.split("\n")]
            )
            commented_out_source = commented_out_source.replace(
                line, commented_out_lines
            )

        return commented_out_source

    def save_as_databricks_notebook(self, path=os.getcwd()):
        db_nb = self._get_databricks_notebook()
        nb_fname = os.path.join(path, f"_DBNB_{self.name}.py")
        with open(nb_fname, "w") as f:
            f.write(db_nb)


def main(path=os.getcwd()):
    cwd = Path(path)
    sp = SubPackage(str(cwd.stem), str(cwd.parent))
    sp.save_as_databricks_notebook()


if __name__ == "__main__":
    main()
