# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from xsb.rasterfiles import sample

from shapely.geometry import AsShape


class CrossSection(object):
    def __init__(self, geometry, buffer_distance, label=''):
        self.geometry = geometry
        self.buffer_distance = buffer_distance
        self.label = label

        # geometric buffer with given distance
        self.buffer = self.shape.buffer(buffer_distance)

        # initialize data atttributes to empty lists
        self.boreholes = []
        self.piezometers = []
        self.points = []
        self.lines = []
        self.solids = []

    def __repr__(self):
        return ('{s.__class__.__name__:}(length={s.length:.2f}, '
                'buffer_distance={s.buffer_distance:.2f}, '
                'label={s.label:})').format(s=self)

    @property
    def shape(self):
        return AsShape(self.geometry)

    @property
    def length(self):
        return self.shape.length

    def discretize(self, res):
        '''discretize line to point coords with given distance'''
        d = 0.
        while d < self.shape.length:
            p = self.shape.interpolate(d)
            yield d, (p.x, p.y)
            d += res

    def add_boreholes(self, boreholes):
        '''add boreholes within buffer distance and project to line'''
        self._add_some_objects(boreholes, self.boreholes)

    def add_piezometers(self, piezometers):
        '''add piezometers within buffer distance and project to line'''
        self._add_some_objects(piezometers, self.piezometers)

    def add_points(self, points):
        '''add points within buffer distance and project to line'''
        self._add_some_objects(points, self.points)

    def _add_some_objects(self, some_objects, dst):
        for an_object in some_objects:
            if AsShape(an_object.geometry).within(self.buffer):
                the_distance = self.shape.project(AsShape(an_object.geometry))
                dst.append((the_distance, an_object))

    def sort(self):
        self.boreholes = [b for b in sorted(self.boreholes)]
        self.piezometers = [p for p in sorted(self.piezometers)]
        self.points = [p for p in sorted(self.points)]

    def add_lines(self, lines):
        for line in lines:
            logging.debug('sampling {}'.format(line['name']))
            distance, coords = zip(*self.discretize(line['res']))
            self.lines.append({
                'name': line['name'],
                'distance': [d for d in distance],
                'values': [v for v in sample(line['file'], coords)],
                })

    def add_solids(self, solids):
        for solid in solids:
            logging.debug('sampling {}'.format(solid['name']))
            distance, coords = zip(*self.discretize(solid['res']))
            self.solids.append({
                'name': solid['name'],
                'distance': [d for d in distance],
                'top': [t for t in sample(solid['topfile'], coords)],
                'base': [b for b in sample(solid['basefile'], coords)],
                })