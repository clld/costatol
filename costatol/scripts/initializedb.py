from __future__ import unicode_literals
import sys
import re

from clldutils.misc import slug
from clld.scripts.util import initializedb, Data, bibtex2source
from clld.db.meta import DBSession
from clld.db.models import common
from csvw.dsv import reader
from clld.lib.bibtex import Database

import costatol
from costatol import models


source_pattern = re.compile('(?P<key>[^\[]+)(\[(?P<pages>[^\]]+)\])?')


def main(args):
    data = Data()

    dataset = common.Dataset(
        id=costatol.__name__,
        name="COSTATOL",
        description="Cognitive Structures across the Tree of Life",
        publisher_name="Max Planck Institute for the Science of Human History",
        publisher_place="Jena",
        publisher_url="http://www.shh.mpg.de",
        license="http://creativecommons.org/licenses/by/4.0/",
        domain='cognition.clld.org',
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'})

    DBSession.add(dataset)

    #
    # TODO: add editors!
    #

    for rec in Database.from_file(args.data_file('sources.bib')):
        data.add(common.Source, rec.id, _obj=bibtex2source(rec))

    contrib = common.Contribution(id='costatol', name='COSTATOL')
    for datapoint in reader(args.data_file('values.csv'), delimiter=',', dicts=True):
        param = data['Parameter'].get(datapoint['cognitive capacity'])
        if not param:
            name = datapoint['cognitive capacity']
            param = data.add(common.Parameter, name, id=slug(name), name=name)

        species = data['Language'].get(datapoint['species'])
        if not species:
            name = datapoint['species']
            species = data.add(common.Language, name, id=slug(name), name=name)

        vid = '%s-%s' % (species.id, param.id)
        vs = data.add(
            common.ValueSet,
            vid,
            id=vid,
            language=species,
            parameter=param,
            contribution=contrib)
        data.add(common.Value, vid, id=vid, name=datapoint['value'], valueset=vs)
        match = source_pattern.match(datapoint['source'])
        if match:
            DBSession.add(common.ValueSetReference(
                valueset=vs,
                source=data['Source'][match.group('key')],
                description=match.group('pages')))

    for species in reader(args.data_file('species.csv'), delimiter=',', namedtuples=True):
        data['Language'][species.name].longitude = species.longitude
        data['Language'][species.name].latitude = species.latitude


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
