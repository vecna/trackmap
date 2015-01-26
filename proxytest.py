from pymiproxy import RequestInterceptorPlugin, ResponseInterceptorPlugin, AsyncMitmProxy
import sys

class DebugInterceptor(RequestInterceptorPlugin, ResponseInterceptorPlugin):

        def do_request(self, data):
            # print '>> %s' % repr(data[:100])
            return data

        def do_response(self, data):
            # print '<< %s' % repr(data[:100])
            return data


if __name__ == '__main__':
    proxy = AsyncMitmProxy()
    proxy.register_interceptor(DebugInterceptor)
    try:
        proxy.serve_forever()
    except KeyboardInterrupt:
        proxy.server_close()
