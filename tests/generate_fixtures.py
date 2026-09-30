"""Generated STEP fixtures for faces of any size (run.py writes them into the
scratch copy of tests/fixtures):

- star_face.step: one faceted FACE whose POLY_LOOP has 1000 corners, a star
  (radii 1 and 0.8 alternating, so every other corner is concave).
- star_prism.step: a closed B-rep prism over a 1000-corner star: two planar
  caps of 1000 edge uses each (luce-cad's B-rep faces take up to 1024) and
  1000 planar sides, all LINE edges.
"""
import math


def star(count):
    return [((1.0 if at % 2 == 0 else 0.8) * math.cos(2 * math.pi * at / count),
             (1.0 if at % 2 == 0 else 0.8) * math.sin(2 * math.pi * at / count)) for at in range(count)]


class Writer:
    def __init__(self):
        self.lines = []

    def add(self, text):
        self.lines.append(text)
        return len(self.lines)

    def text(self):
        body = "".join("#%d=%s;\n" % (at + 1, line) for at, line in enumerate(self.lines))
        return "ISO-10303-21;\nHEADER;ENDSEC;\nDATA;\n" + body + "ENDSEC;\nEND-ISO-10303-21;\n"


def point(writer, x, y, z):
    return writer.add("CARTESIAN_POINT('',(%.9f,%.9f,%.9f))" % (x, y, z))


def star_face():
    writer = Writer()
    corners = [point(writer, x, y, 0.0) for x, y in star(1000)]
    loop = writer.add("POLY_LOOP('',(%s))" % ",".join("#%d" % c for c in corners))
    bound = writer.add("FACE_OUTER_BOUND('',#%d,.T.)" % loop)
    writer.add("FACE('',(#%d))" % bound)
    return writer.text()


def star_prism(n=1000):
    writer = Writer()
    ring = star(n)
    points = [point(writer, x, y, z) for z in (0.0, 1.0) for x, y in ring]
    vertices = [writer.add("VERTEX_POINT('',#%d)" % p) for p in points]

    def line(a, b):
        ax, ay, az = ring[a % n] + ((0.0,) if a < n else (1.0,))
        bx, by, bz = ring[b % n] + ((0.0,) if b < n else (1.0,))
        dx, dy, dz = bx - ax, by - ay, bz - az
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        direction = writer.add("DIRECTION('',(%.12f,%.12f,%.12f))" % (dx / length, dy / length, dz / length))
        vector = writer.add("VECTOR('',#%d,%.12f)" % (direction, length))
        curve = writer.add("LINE('',#%d,#%d)" % (points[a], vector))
        return writer.add("EDGE_CURVE('',#%d,#%d,#%d,.T.)" % (vertices[a], vertices[b], curve))

    bottom = [line(at, (at + 1) % n) for at in range(n)]
    top = [line(n + at, n + (at + 1) % n) for at in range(n)]
    upright = [line(at, n + at) for at in range(n)]

    def oriented(edge, forward):
        return writer.add("ORIENTED_EDGE('',*,*,#%d,%s)" % (edge, ".T." if forward else ".F."))

    def plane(origin, axis, reference):
        o = point(writer, *origin)
        a = writer.add("DIRECTION('',(%.12f,%.12f,%.12f))" % axis)
        r = writer.add("DIRECTION('',(%.12f,%.12f,%.12f))" % reference)
        return writer.add("PLANE('',#%d)" % writer.add("AXIS2_PLACEMENT_3D('',#%d,#%d,#%d)" % (o, a, r)))

    def face(uses, surface, sense):
        loop = writer.add("EDGE_LOOP('',(%s))" % ",".join("#%d" % u for u in uses))
        bound = writer.add("FACE_OUTER_BOUND('',#%d,.T.)" % loop)
        return writer.add("ADVANCED_FACE('',(#%d),#%d,%s)" % (bound, surface, ".T." if sense else ".F."))

    faces = []
    # The caps' loops run counterclockwise about their outward normals.
    faces.append(face([oriented(bottom[at], False) for at in reversed(range(n))], plane((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0)), False))
    faces.append(face([oriented(top[at], True) for at in range(n)], plane((0.0, 0.0, 1.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0)), True))
    for at in range(n):
        following = (at + 1) % n
        (ax, ay), (bx, by) = ring[at], ring[following]
        length = math.hypot(bx - ax, by - ay)
        along = ((bx - ax) / length, (by - ay) / length, 0.0)
        outward = (along[1], -along[0], 0.0)
        uses = [oriented(bottom[at], True), oriented(upright[following], True), oriented(top[at], False), oriented(upright[at], False)]
        faces.append(face(uses, plane((ax, ay, 0.0), outward, along), True))
    shell = writer.add("CLOSED_SHELL('',(%s))" % ",".join("#%d" % f for f in faces))
    writer.add("MANIFOLD_SOLID_BREP('',#%d)" % shell)
    return writer.text()


def write_fixtures(directory):
    (directory / "star_face.step").write_text(star_face())
    (directory / "star_prism.step").write_text(star_prism())
