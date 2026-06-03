from rest_framework.renderers import BaseRenderer


class JPEGRenderer(BaseRenderer):
    media_type = "image/jpeg"
    format = "jpg"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data