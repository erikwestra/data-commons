""" dataCommons.geolocator.management.commands.import_polygons

    This module defines the "import_polygons" management command used by the
    Data Commons system.  This imports the polygons from a given import file
    into the geolocator's database.
"""
import math
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from django.contrib.gis.geos import *

from dataCommons.geolocator.models import *
from dataCommons.shared.models     import Location

#############################################################################

DEFAULT_NUM_CELLS_WIDE = 10
MIN_CELL_WIDTH         = 0.01
MAX_CELL_WIDTH         = 1.00

DEFAULT_NUM_CELLS_HIGH = 10
MIN_CELL_HEIGHT        = 0.01
MAX_CELL_HEIGHT        = 1.00

#############################################################################

class Command(BaseCommand):
    """ Our "import_polygons" management command.
    """
    help        = "Imports a list of polygons into the geolocator's database"
    args        = "polygon_file"
    option_list = BaseCommand.option_list + (
        make_option("--nosplit",
                    action="store_true",
                    dest="nosplit",
                    default=False,
                    help="Store polygon unchanged rather than splitting it."),
    )

    def handle(self, *args, **options):
        """ Run the "import_polygons" management command.
        """
        no_split = options.get("nosplit", False)

        if len(args) == 0:
            raise CommandError("This command takes one parameter.")
        if len(args) > 1:
            raise CommandError("This command takes only one parameter.")

        f = file(args[0], "r")
        for line in f.readlines():
            loc_code,wkt = line.rstrip().split("\t", 1)
            self.stdout.write("Processing " + loc_code + "...\n")

            # Get the Location object associated with this polygon.

            try:
                location = Location.objects.get(code=loc_code)
            except Location.DoesNotExist:
                self.stdout.write("  Unknown location!\n")
                continue

            # Delete any existing matches against this location.

            LocationMatch.objects.filter(location=location).delete()

            # Parse the WKT to get the location's outline.

            outline = GEOSGeometry(wkt)

            if no_split:
                # We simply store the location's outline as a single matching
                # polygon in the database, rather than trying to split it into
                # smaller pieces.
                match = LocationMatch()
                match.location = location
                match.outline  = make_multiPolygon(outline)
                match.save()
                continue

            # Get the outline's bounds.

            min_long,min_lat,max_long,max_lat = outline.extent
            outline_width  = max_long - min_long
            outline_height = max_lat  - min_lat

            # Divide the outline into "cells" of a certain width and height.
            # We initially try to divide the outline into a given number of
            # cells, but adjust the cell size up or down to ensure it remains
            # reasonable.

            cell_width = float(outline_width) / float(DEFAULT_NUM_CELLS_WIDE)
            if cell_width < MIN_CELL_WIDTH: cell_width = MIN_CELL_WIDTH
            if cell_width > MAX_CELL_WIDTH: cell_width = MAX_CELL_WIDTH

            cell_height = float(outline_height) / float(DEFAULT_NUM_CELLS_HIGH)
            if cell_height < MIN_CELL_HEIGHT: cell_height = MIN_CELL_HEIGHT
            if cell_height > MAX_CELL_HEIGHT: cell_height = MAX_CELL_HEIGHT

            num_cells_wide = int(float(outline_width)/float(cell_width))+1
            num_cells_high = int(float(outline_height)/float(cell_height))+1

            self.stdout.write("  dividing location into %d by %d cells\n" %
                              (num_cells_wide, num_cells_high))
            self.stdout.write("  %d cells in total\n" %
                              (num_cells_wide * num_cells_high))

            # Calculate the "origin" on which to base our cells.  We shift the
            # lower-left corner cell down and to the left by half a cell, to
            # give us a buffer around the location's outline.

            origin_x = min_long - cell_width / 2.0
            origin_y = min_lat  - cell_height / 2.0

            # Process each cell in turn, building lists of partially and fully
            # enclosed cells.

            partly_enclosed_cells = []
            fully_enclosed_cells  = []

            self.stdout.write("  processing cells")
            self.stdout.flush()

            n = 0
            for cell_y in range(num_cells_high):
                for cell_x in range(num_cells_wide):
                    n = n + 1
                    if n % 100 == 0:
                        self.stdout.write(".")
                        self.stdout.flush()

                    # Calculate the lat/long bounds for this cell.

                    cell_left   = origin_x + (cell_x * cell_width)
                    cell_right  = cell_left + cell_width
                    cell_bottom = origin_y + (cell_y * cell_height)
                    cell_top    = cell_bottom + cell_height

                    cell_bounds = Polygon(((cell_left,  cell_bottom),
                                           (cell_left,  cell_top),
                                           (cell_right, cell_top),
                                           (cell_right, cell_bottom),
                                           (cell_left,  cell_bottom)))

                    # If the cell bounds fits partly or entirely in the
                    # location's outline, remember this cell.

                    if outline.contains(cell_bounds):
                        fully_enclosed_cells.append((cell_x, cell_y))
                    elif outline.intersects(cell_bounds):
                        partly_enclosed_cells.append((cell_x, cell_y))

            self.stdout.write("\n")
            self.stdout.write("  %d cells found with full matches\n" %
                              len(fully_enclosed_cells))
            self.stdout.write("  %d cells found with part matches\n" %
                              len(partly_enclosed_cells))

            # Merge the fully-enclosed cells into the smallest possible number
            # of contiguous rectangles, and store each rectangle as a location
            # match.

            num_matches = 0

            for merged_cell in merge_cells(fully_enclosed_cells,
                                           num_cells_wide, num_cells_high):
                left,bottom,width,height = merged_cell

                rect_left   = origin_x + left * cell_width
                rect_right  = rect_left + width * cell_width
                rect_bottom = origin_y + bottom * cell_height
                rect_top    = rect_bottom + height * cell_height

                rect_bounds = Polygon(((rect_left,  rect_bottom),
                                       (rect_left,  rect_top),
                                       (rect_right, rect_top),
                                       (rect_right, rect_bottom),
                                       (rect_left,  rect_bottom)))

                match = LocationMatch()
                match.location = location
                match.outline  = make_multiPolygon(rect_bounds)
                match.save()

                num_matches = num_matches + 1

            self.stdout.write("  %d fully-enclosed rectangles saved\n" %
                              num_matches)

            # Now do the same for the partly-enclosed cells.  The only
            # difference is that this time we intersect the rectangle bounds
            # with the location's outline to get the portion of the outline
            # that fits inside the desired rectangle.

            num_matches = 0

            for merged_cell in merge_cells(partly_enclosed_cells,
                                           num_cells_wide, num_cells_high):
                left,bottom,width,height = merged_cell

                rect_left   = origin_x + left * cell_width
                rect_right  = rect_left + width * cell_width
                rect_bottom = origin_y + bottom * cell_height
                rect_top    = rect_bottom + height * cell_height

                rect_bounds = Polygon(((rect_left,  rect_bottom),
                                       (rect_left,  rect_top),
                                       (rect_right, rect_top),
                                       (rect_right, rect_bottom),
                                       (rect_left,  rect_bottom)))

                try:
                    intersection = outline.intersection(rect_bounds)
                except GEOSException:
                    intersection = None

                if intersection != None:
                    if intersection.area > 0:
                        match = LocationMatch()
                        match.location = location
                        match.outline  = make_multiPolygon(intersection)
                        match.save()

                        num_matches = num_matches + 1

            self.stdout.write("  %d partly-enclosed rectangles saved\n" %
                              num_matches)

        # That's all, folks!

        f.close()

#############################################################################

def merge_cells(cell_coords, num_cells_wide, num_cells_high):
    """ Merge adjacent cells into larger rectangles.

        The parameters are as follows:

            'cell_coords'

                A list of (cell_x, cell_y) tuples, defining the coordinates for
                the cells we are interested in.

            'num_cells_wide'

                The total number of cells across.

            'num_cells_high'

                The total number of cells high.

        We attempt to merge adjacent cells into larger rectangles, reducing the
        number of rectangles we need to process.

        Upon completion, we return a list of (left, bottom, width, height)
        tuples, where 'left' and 'bottom' define the cell coordinate for the
        bottom-left corner of a rectangle, and 'width' and 'height' define the
        size of the rectangle.
    """
    # Start by converting the cell coordinates into a set so we can find
    # matches easily.

    cells = set(cell_coords)

    # Keep building rectangles until we have no non-empty cells left.

    rectangles = []
    while len(cells) > 0:

        # Build a cell rectangle centred on each cell in turn, and expand that
        # rectangle as much as possible.  For each cell, we remember the bounds
        # of the rectangle and its associated area.

        cell_rects = {} # Maps (cell_x,cell_y) coordinate to CellRect object.

        for cell_x, cell_y in cells:
            rect = CellRect(cells, cell_x, cell_y, width=1, height=1)
            rect.expand_all()
            cell_rects[(cell_x, cell_y)] = rect

        # Choose the rectangle with the biggest area.

        biggest_cell_x = None
        biggest_cell_y = None
        biggest_area   = None

        for cell_x,cell_y in cell_rects:
            rect = cell_rects[(cell_x, cell_y)]
            area = rect.area()
            if biggest_area == None or area > biggest_area:
                biggest_cell_x = cell_x
                biggest_cell_y = cell_y
                biggest_area   = area

        # We now have the biggest possible rectangle we can build.  Remember
        # this rectangle.

        rect = cell_rects[(biggest_cell_x, biggest_cell_y)]
        rectangles.append(rect.bounds())

        # Finally, remove this rectangle's cells from the list of remaining
        # cells.

        for remove_x in range(rect.left, rect.left + rect.width):
            for remove_y in range(rect.bottom, rect.bottom + rect.height):
                cells.remove((remove_x, remove_y))

        # Keep going until we have no more cells left.

        continue

    # That's all, folks!

    return rectangles

#############################################################################

def make_multiPolygon(geometry):
    """ Convert an arbitrary geometry object into a MultiPolygon.

        Note that we only include polygons with a non-zero area.
    """
    def extract_polygons(geometry):
        """ Return a list of polygons within the given geometry.
        """
        polygons = []
        if geometry.geom_type == "Polygon":
            polygons.append(geometry)
        elif geometry.geom_type == "MultiPolygon":
            for child in geometry:
                polygons.append(child)
        elif geometry.geom_type == "GeometryCollection":
            for child in geometry:
                polygons.extend(extract_polygons(child))
        return polygons

    polygons_with_area = []
    for polygon in extract_polygons(geometry):
        if polygon.area > 0:
            polygons_with_area.append(polygon)

    return MultiPolygon(polygons_with_area)

#############################################################################

class CellRect:
    """ A rectangle within a collection of cells.

        A CellRect has an initial position, width and height, but supports the
        notion of "expanding" the rectangle as much as possible in a given
        direction.  For example, imagine that we have the following matrix of
        cells, where "~~~" represents a cell with data:

                 :---:---:---:---:---:
               4 :   :~~~:   :   :   :
                 :---:---:---:---:---:
               3 :   :~~~:~~~:~~~:   :
                 :---:---:---:---:---:
               2 :~~~:~~~:~~~:~~~:   :
                 :---:---:---:---:---:
               1 :   :~~~:~~~:~~~:~~~:
                 :---:---:---:---:---:
               0 :   :   :   :~~~:   :
                 :---:---:---:---:---:
                   0   1   2   3   4

        Also imagine that our CellRect has the following initial values:
            
            cell_x=2, cell_y=1, width=2, height=3

        Thus, the CellRect includes the following cells:

                 :---:---:---:---:---:
               4 :   :~~~:   :   :   :
                 :---:---:---:---:---:
               3 :   :~~~:#######:   :
                 :---:---:#######:---:
               2 :~~~:~~~:#######:   :
                 :---:---:#######:---:
               1 :   :~~~:#######:~~~:
                 :---:---:---:---:---:
               0 :   :   :   :~~~:   :
                 :---:---:---:---:---:
                   0   1   2   3   4

        If we expand this rectangle as much as possible to the left, the
        CellRect will now encompass the following cells:

                 :---:---:---:---:---:
               4 :   :~~~:   :   :   :
                 :---:---:---:---:---:
               3 :   :###########:   :
                 :---:###########:---:
               2 :~~~:###########:   :
                 :---:###########:---:
               1 :   :###########:~~~:
                 :---:---:---:---:---:
               0 :   :   :   :~~~:   :
                 :---:---:---:---:---:
                   0   1   2   3   4

        Similar logic is used to expand the rectangle in the other directions.
    """
    def __init__(self, cells, left, bottom, width, height):
        """ Standard initialiser.

            The parameters are as follows:

                A list or set of (cell_x, cell_y) coordinates for the non-empty
                cells we are processing.

            'left'

                The cell coordinate for the left side of the rectangle.

            'bottom'

                The cell coordinate for the bottom of the rectangle.

            'width'

                The width of the rectangle, measured in cell coordinates.

            'height'

                The height of the rectangle, measured in cell coordinates.
        """
        self.cells  = set(cells)
        self.left   = left
        self.bottom = bottom
        self.width  = width
        self.height = height


    def bounds(self):
        """ Return the current bounds for this CellRect.

            We return a (left, bottom, width, height) tuple, defining the
            CellRect's current bounds.
        """
        return (self.left, self.bottom, self.width, self.height)


    def area(self):
        """ Return the number of cells covered by this CellRect.
        """
        return self.width * self.height


    def save(self):
        """ Save the current state of this rectangle.

            We return an opaque data structure holding the current state of
            this rectangle.
        """
        return {'left'   : self.left,
                'bottom' : self.bottom,
                'width'  : self.width,
                'height' : self.height}


    def restore(self, state):
        """ Restore a previously-saved state of this rectangle.

            'state' is a value returned by a previous call to save(), above.
            We restore the rectangle to the state it was in when it was saved.
        """
        self.left   = state['left']
        self.bottom = state['bottom']
        self.width  = state['width']
        self.height = state['height']


    def expand_left(self):
        """ Expand this CellRect as much as possible to the left.
        """
        extra_width = 1
        rect        = set()
        while True:
            for y in range(self.height):
                rect.add((self.left - extra_width, self.bottom + y))

            if rect.issubset(self.cells):
                extra_width = extra_width + 1
            else:
                extra_width = extra_width - 1
                break

        self.left  = self.left  - extra_width
        self.width = self.width + extra_width


    def expand_right(self):
        """ Expand this CellRect as much as possible to the right.
        """
        extra_width = 1
        rect        = set()
        while True:
            for y in range(self.height):
                rect.add((self.left + self.width + extra_width - 1,
                          self.bottom + y))

            if rect.issubset(self.cells):
                extra_width = extra_width + 1
            else:
                extra_width = extra_width - 1
                break

        self.width = self.width + extra_width


    def expand_up(self):
        """ Expand this CellRect upwards as much as possible.
        """
        extra_height = 1
        rect         = set()
        while True:
            for x in range(self.width):
                rect.add((self.left + x,
                          self.bottom + self.height + extra_height - 1))

            if rect.issubset(self.cells):
                extra_height = extra_height + 1
            else:
                extra_height = extra_height - 1
                break

        self.height = self.height + extra_height


    def expand_down(self):
        """ Expand this CellRect downwards as much as possible.
        """
        extra_height = 1
        rect         = set()
        while True:
            for x in range(self.width):
                rect.add((self.left + x, self.bottom - extra_height))

            if rect.issubset(self.cells):
                extra_height = extra_height + 1
            else:
                extra_height = extra_height - 1
                break

        self.bottom = self.bottom - extra_height
        self.height = self.height + extra_height


    def expand_all(self):
        """ Expand the rectangle as much as possible in all directions.

            We first try expanding the rectangle left and right, and then up
            and down.  Then we try expanding the rectangle up and down, and
            then left and right.  We choose whichever final rectangle has the
            biggest area.
        """
        # Remember our state.

        orig_state = self.save()

        # Try expanding the rectangle left and right, and then up and down.

        self.expand_left()
        self.expand_right()
        self.expand_up()
        self.expand_down()

        area_1 = self.area()
        state_1 = self.save()

        # Now go back to the original state, and try expanding the rectangle up
        # and down, and then left and right.

        self.restore(orig_state)

        self.expand_up()
        self.expand_down()
        self.expand_left()
        self.expand_right()

        area_2 = self.area()
        state_2 = self.save()

        # Finally, keep the expansion that resulted in the biggest increase in
        # area.

        if area_1 > area_2:
            self.restore(state_1)
        else:
            self.restore(state_2)

