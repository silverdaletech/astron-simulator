odoo.define('sd_website_slides_video.fullscreen', function (require) {
    "use strict";
    
    var core = require('web.core');
    var QWeb = core.qweb;
    var FullScreen = require('@website_slides/js/slides_course_fullscreen_player')[Symbol.for("default")];


    FullScreen.include({
        /**
             * Extend the _renderSlide method so that slides of type "doc_video"
             * are also taken into account and rendered correctly
             *
             * @private
             * @override
         */
        _renderSlide: async function (){
            var def = this._super.apply(this, arguments);
            this.videoEndedListener = () => this.stopStreams();

            var $content = this.$('.o_wslides_fs_content');
            var slide = this.get('slide');
            if (slide.type === 'doc_video') {
                const res = await this._rpc({
                    model: 'slide.slide',
                    method: 'get_binary_document_video',
                    args: [slide.id],
                });
                var src = "data:video/mp4;base64," + res
                var $html = $(`<video alt="test" controls>
                                <source src="${src}" type="video/mp4" />
                            </video>`)

                $html[0].addEventListener('ended', this.videoEndedListener);

                return $html.appendTo($content);
            }
            return Promise.all([def]);
        },

        /*
            * Stop the stream and continue the normal odoo flow.
        */
        stopStreams: function() {
            var slide = this.get('slide');
            slide.data = {};
            slide.data.id = slide.id;
            this._onSlideToComplete(slide);
            if (slide.hasNext) {
                this.trigger_up('slide_go_next');
            }
        }
    });
});
