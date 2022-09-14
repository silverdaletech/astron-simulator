from odoo.http import HttpRequest
from odoo.http import Response


# Odoo base module
def render(self, template, qcontext=None, lazy=True, **kw):
    """ Lazy render of a QWeb template.
    Save session to redirect in previous url
    The actual rendering of the given template will occur at then end of
    the dispatching. Meanwhile, the template and/or qcontext can be
    altered or even replaced by a static response.

    :param basestring template: template to render
    :param dict qcontext: Rendering context to use
    :param bool lazy: whether the template rendering should be deferred
                        until the last possible moment
    :param kw: forwarded to werkzeug's Response object
    """
    #Save url in session to redirect previous url
    if self.httprequest.full_path not in ['/web/login?', '/web/login', '/web/signup', '/web/signup?']:
        self.session['previous_url'] = self.httprequest.base_url

    response = Response(template=template, qcontext=qcontext, **kw)
    if not lazy:
        return response.render()
    return response

# Override python base function
HttpRequest.render = render