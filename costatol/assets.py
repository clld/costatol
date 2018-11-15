from clld.web.assets import environment
from clldutils.path import Path

import costatol


environment.append_path(
    str(Path(costatol.__file__).parent.joinpath('static').resolve()), url='/costatol:static/')
environment.load_path = list(reversed(environment.load_path))
