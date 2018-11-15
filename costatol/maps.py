from clld.web.maps import Map, ParameterMap


def options(req):
    return dict(tile_layer=dict(
        url_pattern=req.static_url('costatol:static/map_tiles/') + '{z}/{x}/{y}.png',
        options={
            'minZoom': 0,
            'maxZoom': 2,
            'attribution': '',
            'tms': True}))


class TreeOfLife(Map):
    def get_options(self):
        return options(self.req)


class CapacityMap(ParameterMap):
    def get_options(self):
        return options(self.req)


def includeme(config):
    config.register_map('parameter', CapacityMap)
    config.register_map('languages', TreeOfLife)
