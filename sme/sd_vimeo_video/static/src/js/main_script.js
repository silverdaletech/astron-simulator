odoo.define('sd_vimeo_video.fullscreen', function (require) {
    "use strict";
    
    var core = require('web.core');
    var QWeb = core.qweb;
    var Fullscreen = require('@website_slides/js/slides_course_fullscreen_player')[Symbol.for("default")];
    
    Fullscreen.include({
        
        /**
         * Extend the _renderSlide method so that slides of type "vimeovideo"
         * are also taken into account and rendered correctly
         *
         * @private
         * @override
         */
        _renderSlide: function (){
            var def = this._super.apply(this, arguments);
            
            var $content = this.$('.o_wslides_fs_content');
            var slide = this.get('slide');
            if (slide.type === 'vimeovideo') {
                this.videoPlayer = $(slide.embedCode);
                var vimeoplayer = new Vimeo.Player(this.videoPlayer);
                vimeoplayer.on('ended', function(){
                    slide.data = {};
                    slide.data.id = slide.id;
                    self._onSlideToComplete(slide);
                });
                return this.videoPlayer.appendTo($content);
            }
            return Promise.all([def]);
        },
    });
});
