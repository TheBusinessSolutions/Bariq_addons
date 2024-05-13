odoo.define('purchase.product_discount', function (require) {
    "use strict";

    const BasicFields = require('web.basic_fields');
    const FieldsRegistry = require('web.field_registry');

    /**
     * The purchase.product_discount widget is a simple widget extending FieldFloat
     *
     *
     * !!! WARNING !!!
     *
     * This widget is only designed for purchase_order_line creation/updates.
     * !!! It should only be used on a discount field !!!
     */
    const PurchaseProductDiscountWidget = BasicFields.FieldFloat.extend({

        /**
         * Override changes at a discount.
         *
         * @override
         * @param {OdooEvent} ev
         *
         */
        async reset(record, ev) {
            if (ev && ev.data.changes && ev.data.changes.discount >= 0) {
               this.trigger_up('open_discount_wizard');
            }
            this._super(...arguments);
        },
    });

    FieldsRegistry.add('purchase_product_discount', PurchaseProductDiscountWidget);

    return PurchaseProductDiscountWidget;

});
