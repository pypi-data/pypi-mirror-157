import json

import werkzeug


class Middleware:
    def __init__(self, next_app, path, *_args, **_kwargs):
        self._next_app = next_app
        self._path = path
        self._json_encoder = json.JSONEncoder()
        self._json_decoder = json.JSONDecoder()

    def __call__(self, environ, start_response):
        request = werkzeug.wrappers.Request(environ)

        if request.path.startswith(self._path):
            path_postfix = request.path[len(self._path) :]

            if path_postfix == "" or path_postfix[0] == "/":
                return self.serve(request, path_postfix)(environ, start_response)

        return self._next_app(environ, start_response)

    def error_response(self, status_code, msg):
        return werkzeug.wrappers.Response(
            self._json_encoder.encode({"error": msg}),
            mimetype="application/json",
            status=status_code,
        )

    def serve(self, request, path_postfix):
        return werkzeug.wrappers.Response(
            self._json_encoder.encode({"some": "response"}),
            mimetype="application/json",
            status=200,
        )
