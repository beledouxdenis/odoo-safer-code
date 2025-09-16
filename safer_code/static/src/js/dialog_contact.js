import { Component, onMounted } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";

export class SaferCodeContactDialog extends Component {
    static components = { Dialog };
    static template = "safer_code.contact_dialog";
    static props = {
        close: Function,
        partner: Object,
    };

    setup() {
        super.setup();
        onMounted(() => {
            document.querySelector('div[role="alert"]').innerHTML =
                "<div>" + this.props.partner.name + "</div>" +
                "<div>" + this.props.partner.phone + "</div>";
        });
    }
}

export class SaferCodePartnerFormController extends FormController {
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        onMounted(() => {
            document.querySelector(".o_safer_code_give_a_call").addEventListener("click", () => {
                this.dialogService.add(SaferCodeContactDialog, {
                    partner: {
                        id: this.model.root.resId,
                        name: this.model.root.data.display_name,
                        phone: this.model.root.data.phone,
                    },
                });
            });
        });
    }
}

registry.category("views").add("res_partner_form", {
    ...formView,
    Controller: SaferCodePartnerFormController,
});
