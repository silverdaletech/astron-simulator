odoo.define('sd_widgets.basic_fields_ext', function (require) {
"use strict";

var InputField = require('web.basic_fields').InputField;

KioskBoard.init({

  /*!
  * Required
  * An Array of Objects has to be defined for the custom keys. Hint: Each object creates a row element (HTML) on the keyboard.
  * e.g. [{"key":"value"}, {"key":"value"}] => [{"0":"A","1":"B","2":"C"}, {"0":"D","1":"E","2":"F"}]
  */
  keysArrayOfObjects: [
   {
      "0": "Q",
      "1": "W",
      "2": "E",
      "3": "R",
      "4": "T",
      "5": "Y",
      "6": "U",
      "7": "I",
      "8": "O",
      "9": "P"
   },
   {
      "0": "A",
      "1": "S",
      "2": "D",
      "3": "F",
      "4": "G",
      "5": "H",
      "6": "J",
      "7": "K",
      "8": "L"
   },
   {
      "0": "Z",
      "1": "X",
      "2": "C",
      "3": "V",
      "4": "B",
      "5": "N",
      "6": "M"
   }
],

  /*!
  * Required only if "keysArrayOfObjects" is "null".
  * The path of the "kioskboard-keys-${langugage}.json" file must be set to the "keysJsonUrl" option. (XMLHttpRequest to get the keys from JSON file.)
  * e.g. '/Content/Plugins/KioskBoard/dist/kioskboard-keys-english.json'
  */
  keysJsonUrl: null,

  /*
  * Optional: An Array of Strings can be set to override the built-in special characters.
  * e.g. ["#", "â¬", "%", "+", "-", "*"]
  */
  keysSpecialCharsArrayOfStrings: null,

  /*
  * Optional: An Array of Numbers can be set to override the built-in numpad keys. (From 0 to 9, in any order.)
  * e.g. [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
  */
  keysNumpadArrayOfNumbers: null,

  // Optional: (Other Options)

  // Language Code (ISO 639-1) for custom keys (for language support) => e.g. "de" || "en" || "fr" || "hu" || "tr" etc...
  language: 'all',

  // The theme of keyboard => "light" || "dark" || "flat" || "material" || "oldschool"
  theme: 'light',

  // Uppercase or lowercase to start. Uppercased when "true"
  capsLockActive: true,

  /*
  * Allow or prevent real/physical keyboard usage. Prevented when "false"
  * In addition, the "allowMobileKeyboard" option must be "true" as well, if the real/physical keyboard has wanted to be used.
  */
  allowRealKeyboard: false,

  // Allow or prevent mobile keyboard usage. Prevented when "false"
  allowMobileKeyboard: false,

  // CSS animations for opening or closing the keyboard
  cssAnimations: true,

  // CSS animations duration as millisecond
  cssAnimationsDuration: 120,

  // CSS animations style for opening or closing the keyboard => "slide" || "fade"
  cssAnimationsStyle: 'slide',

  // Enable or Disable Spacebar functionality on the keyboard. The Spacebar will be passive when "false"
  keysAllowSpacebar: true,

  // Text of the space key (Spacebar). Without text => " "
  keysSpacebarText: 'Space',

  // Font family of the keys
  keysFontFamily: 'sans-serif',

  // Font size of the keys
  keysFontSize: '42px',

  // Font weight of the keys
  keysFontWeight: 'normal',

  // Size of the icon keys
  keysIconSize: '45px',

  // Scrolls the document to the top or bottom(by the placement option) of the input/textarea element. Prevented when "false"
  autoScroll: true,
});

var KioskNumpad = InputField.extend({

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override _render from InputField
     Set attributes on input fields for the numpad and run KioskBoard.
     */
    _render: function () {
        this._super.apply(this, arguments);
        this.$el[0].setAttribute('data-kioskboard-type', 'numpad')
        this.$el[0].setAttribute('data-kioskboard-placement', 'bottom')

        var value = ''
        if (this.attrs.options){
            if (this.attrs.options.field_type){
                if (this.attrs.options.field_type === 'float' || this.attrs.options.field_type === 'integer'){
                    value = '0'
                }
            }
        }

        this.$el[0].value = value


//        if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Macintosh|Opera Mini/i.test(navigator.userAgent)){
        KioskBoard.run(this.$el[0]);
//        }

        /*var test = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Macintosh|Opera Mini/i.test(navigator.userAgent);
        this._rpc({
            model: "mrp.production",
            method: 'check_logs',
            args: [test],
        })*/

        /*if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent)
            || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) {
        }*/
    },

});

return {
    KioskNumpad: KioskNumpad,
};

});
