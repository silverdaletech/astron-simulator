odoo.define('sd_widgets.field_registry_ext', function (require) {
"use strict";

var Registry = require('web.Registry');

return new Registry();
});

odoo.define('sd_widgets._field_registry_ext', function (require) {
"use strict";

var basic_fields = require('sd_widgets.basic_fields_ext');
var registry = require('web.field_registry');


// Basic fields
registry.add('kiosk_board', basic_fields.KioskNumpad);

});
