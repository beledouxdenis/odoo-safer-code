# Introduction
A training module to raise awareness to good security coding practices in Odoo.

The goal of this module is:
1. Play the attacker side, exploit the vulnerabilities
2. Play the developer side, correct the code to remove the vulnerabilities while keeping the features
3. Be more attentive to keywords when you do code reviews, to make your Odoo modules code safer

# Installation

```sh
git clone git@github.com:beledouxdenis/odoo-safer-code.git
```

Then, add the folder in the addons path, install the module **with demo data** in a database called **safer_db**

```sh
./odoo-bin \
--addons-path=./addons,../enterprise,~/src/odoo-safer-code \
--with-demo \
-d safer_db \
-i safer_code
```

# How to use

This module contains examples of vulnerabilities inspired from real past vulnerabilities that have been solved in Odoo.

The structure of the module follows the guidelines of a regular module, with the folder `/models`, `/views`, `/security` and so on.

There is one additional folder: `/leaks`. All the vulnerabilities are within this folder, one file per chapter / subject.

There is also a file `/rpc.py` at the root of the module. It contains pre-made RPC calls and explanations in the goal to exploit the vulnerabilities of the module.
It is used as an executable to do the RPC calls to your local Odoo server and exploit the vulnerabilities.

e.g.
```sh
./rpc.py sql_1
```

Exploits the 1st vulnerability contained in the file `/safer_code/leaks/leak_1_sql_injection.py`.
It does a SQL injection to return the hashed password of users.

The first exercice is to fill the blank inside the method `leak_sql_2` of `/safer_code/rpc.py` to exploit the second SQL injection vulnerability of `/safer_code/leaks/leak_1_sql_injection.py`.

Then, correct the code in `/safer_code/leaks/leak_1_sql_injection.py` to remove the 2 SQL injections.

To test your code correction, you can either re-run `./rpc.py sql_1` and `./rpc.py sql_2` or use the unit tests provided.

For instance `--test-tags .test_unsafe_cr_execute` and `--test-tags .test_unsafe_query_order`.

The name / command argument of the unit tests are in the docstrings/comment of `rpc.py` and repeated in the `/leaks` code files.

Then, progressively move on to the other vulnerabilities by exploring the `rpc.py` file and the files in the `/leaks` folder.
