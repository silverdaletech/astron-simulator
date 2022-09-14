odoo.define('sd_widgets.ModelFieldSelector', function (require) {
    'use strict';

    var AbstractField = require('web.AbstractField');
    var DomainSelectors = require('web.DomainSelectors');
    const field_registry = require('web.field_registry');
    const basic_fields = require('web.basic_fields');
    var DomainSelectorDialogs = require('web.DomainSelectorDialogs');
    var core = require('web.core');
    var config = require('web.config');
    var qweb = core.qweb;
    var current_model_is = ""
    const FieldDomain = basic_fields.FieldDomain;

    const ModelFieldSelector = FieldDomain.extend({
        resetOnAnyFieldChange: true,
        events: _.extend({}, AbstractField.prototype.events, {
            "click .o_domain_show_selection_button": "_onShowSelectionButtonClick",
            "click .o_field_domain_dialog_button": "_onDialogEditButtonClick",
            "click .o_refresh_count": "_onRefreshCountClick",
        }),
        _onShowSelectionButtonClick: function (e) {
            e.preventDefault();
            new view_dialogs.SelectCreateDialog(this, {
                title: _t("Selected records"),
                res_model: this._domainModel,
                context: this.record.getContext({ fieldName: this.name, viewType: this.viewType }),
                domain: this.value || "[]",
                no_create: true,
                readonly: true,
                disable_multiple_selection: true,
            }).open();
        },

        on_attach_callback() {
            if (this.domainSelectors && !this.inDialog) {
                this.domainSelectors.on_attach_callback();
            }
        },
        isValid: function () {
            return (
                this._super.apply(this, arguments)
                && (!this.domainSelectors || this.domainSelectors.isValid())
                && this._isValidForModel
            );
        },

        _render: async function () {
            // If there is no model, only change the non-domain-selector content
            if (!this._domainModel) {
                this._replaceContent();
                return Promise.resolve();
            }

            // Convert char value to array value
            var value = this.value || "[]";

            // Create the domain selector or change the value of the current one...
            var def;
            if (!this.domainSelectors) {
                this.domainSelectors = new DomainSelectors(this, this._domainModel, value, {
                    readonly: this.mode === "readonly" || this.inDialog,
                    filters: this.fsFilters,
                    debugMode: config.isDebug(),
                });
                def = this.domainSelectors.prependTo(this.$el);
            } else if (!this.debugEdition) {
                // do not update web.DomainSelectorthe domainSelector if we edited the domain with the textarea
                // as we don't want it to format what we just wrote
                def = this.domainSelectors.setDomain(value);
            }

            // ... then replace the other content (matched records, etc)
            await Promise.resolve(def);
            this._replaceContent();

            // Finally, fetch the number of records matching the domain, but do not
            // wait for it to render the field widget (simply update the number of
            // records when we know it)
            if (!this.debugEdition) {
                // do not automatically recompute the count if we're editing the
                // domain with the textarea
                this._fetchCount().then(() => this._replaceContent());
            }
        },

        _reset: function (record, ev) {
            this._super.apply(this, arguments);
            var oldDomainModel = this._domainModel;
            this._setState();
            if (this.domainSelector && this._domainModel !== oldDomainModel) {
                // If the model has changed, destroy the current domain selector
                this.domainSelectors.destroy();
                this.domainSelector = null;
            }
            if (!ev || ev.target !== this) {
                this.debugEdition = false;
            }
        },

        _onDialogEditButtonClick: function (e) {
            current_model_is = this.model
            e.preventDefault();
            new DomainSelectorDialogs(this, this._domainModel, this.value || "[]", {
                readonly: this.mode === "readonly",
                //filters: this.fsFilters,
                //debugMode: config.isDebug(),
            }).open();
        },

        async _onRefreshCountClick(ev) {
            ev.stopPropagation();
            ev.currentTarget.setAttribute("disabled", "disabled");
            await this._fetchCount(true);
            this._replaceContent();
        },
        _replaceContent: function () {
            //        debugger;
            if (this._$content) {
                this._$content.remove();
            }
            this._$content = $(qweb.render("is_having.model", {
                hasModel: !!this._domainModel,
                isValid: !!this._isValidForModel,
                nbRecords: this.nbRecords,
                inDialog: this.inDialog,
                editMode: this.mode === "edit",
                isDebug: config.isDebug(),
            }));
            this._$content.appendTo(this.$el);
        },

    });

    field_registry.add('model_field_selector', ModelFieldSelector);
    return {
        ModelFieldSelector: ModelFieldSelector,
    };

});
