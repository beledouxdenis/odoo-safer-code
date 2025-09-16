import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("test_unsafe_stored_xss", {
    steps: () => [
        {
            content: "Give a call",
            trigger: ".o_safer_code_give_a_call",
            run: async function () {
                // Click the give a call link
                this.anchor.click();
                // Leave a bit of time to let a chance to the injected code to finish
                await new Promise((resolve) => setTimeout(resolve, 1000));
            },
        },
    ],
});

registry.category("web_tour.tours").add("test_unsafe_reflected_xss_forum", {
    steps: () => [
        {
            content: "Click the back button and wait a bit",
            trigger: "a:contains('Back')",
            run: async function () {
                // Click the back button link
                this.anchor.click();
                // Leave a bit of time to let a chance to the injected code to finish
                await new Promise((resolve) => setTimeout(resolve, 1000));
            },
        },
    ],
});
