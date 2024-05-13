odoo.define('purchase.PurchaseOrderView', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const FormView = require('web.FormView');
    const viewRegistry = require('web.view_registry');
    const Dialog = require('web.Dialog');
    const core = require('web.core');
    const _t = core._t;

    const PurchaseOrderFormController = FormController.extend({
        custom_events: _.extend({}, FormController.prototype.custom_events, {
            open_discount_wizard: '_onOpenDiscountWizard',
        }),

        // -------------------------------------------------------------------------
        // Handlers
        // -------------------------------------------------------------------------

        /**
         * Handler called if user changes the discount field in the purchase order line.
         * The wizard will open only if
         *  (1) purchase order line is 3 or more
         *  (2) First purchase order line is changed to discount
         *  (3) Discount is the same in all purchase order line
         */
        _onOpenDiscountWizard(ev) {
            const orderLines = this.renderer.state.data.order_line.data.filter(line => !line.data.display_type);
            const recordData = ev.target.recordData;
            const isEqualDiscount = orderLines.slice(1).every(line => line.data.discount === recordData.discount);
            if (orderLines.length >= 3 && recordData.sequence === orderLines[0].data.sequence && isEqualDiscount) {
                Dialog.confirm(this, _t("Do you want to apply this discount to all order lines?"), {
                    confirm_callback: () => {
                        orderLines.slice(1).forEach((line) => {
                            this.trigger_up('field_changed', {
                                dataPointID: this.renderer.state.id,
                                changes: {order_line: {operation: "UPDATE", id: line.id, data: {discount: orderLines[0].data.discount}}},
                            });
                        });
                    },
                });
            }
        },
    });

    const PurchaseOrderView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: PurchaseOrderFormController,
        }),
    });

    viewRegistry.add('purchase_discount_form', PurchaseOrderView);

    return PurchaseOrderView;

});
