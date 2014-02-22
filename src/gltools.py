##### RENDERING TOOL CODE ######################################################

# draw a fullscreen quad
def DrawFullQuad():
    XXXNOGLXXX.glBegin(GL_QUADS)
    XXXNOGLXXX.glTexCoord2d(    0.0,     0.0);  glVertex2i(0, 0)
    XXXNOGLXXX.glTexCoord2d(TexMaxS,     0.0);  glVertex2i(1, 0)
    XXXNOGLXXX.glTexCoord2d(TexMaxS, TexMaxT);  glVertex2i(1, 1)
    XXXNOGLXXX.glTexCoord2d(    0.0, TexMaxT);  glVertex2i(0, 1)
    XXXNOGLXXX.glEnd()

# draw a generic 2D quad
def DrawQuad(x0=0.0, y0=0.0, x1=1.0, y1=1.0):
    XXXNOGLXXX.glBegin(GL_QUADS)
    XXXNOGLXXX.glTexCoord2d(    0.0,     0.0);  glVertex2d(x0, y0)
    XXXNOGLXXX.glTexCoord2d(TexMaxS,     0.0);  glVertex2d(x1, y0)
    XXXNOGLXXX.glTexCoord2d(TexMaxS, TexMaxT);  glVertex2d(x1, y1)
    XXXNOGLXXX.glTexCoord2d(    0.0, TexMaxT);  glVertex2d(x0, y1)
    XXXNOGLXXX.glEnd()

# helper function: draw a translated fullscreen quad
def DrawTranslatedFullQuad(dx, dy, i, a):
    XXXNOGLXXX.glColor4d(i, i, i, a)
    XXXNOGLXXX.glPushMatrix()
    XXXNOGLXXX.glTranslated(dx, dy, 0.0)
    DrawFullQuad()
    XXXNOGLXXX.glPopMatrix()

# draw a vertex in normalized screen coordinates,
# setting texture coordinates appropriately
def DrawPoint(x, y):
    XXXNOGLXXX.glTexCoord2d(x *TexMaxS, y * TexMaxT)
    XXXNOGLXXX.glVertex2d(x, y)
def DrawPointEx(x, y, a):
    XXXNOGLXXX.glColor4d(1.0, 1.0, 1.0, a)
    XXXNOGLXXX.glTexCoord2d(x * TexMaxS, y * TexMaxT)
    XXXNOGLXXX.glVertex2d(x, y)

# a mesh transformation function: it gets the relative transition time (in the
# [0.0,0.1) interval) and the normalized 2D screen coordinates, and returns a
# 7-tuple containing the desired 3D screen coordinates, 2D texture coordinates,
# and intensity/alpha color values.
def meshtrans_null(t, u, v):
    return (u, v, 0.0, u, v, 1.0, t)
         # (x, y, z,   s, t, i,   a)

# draw a quad, applying a mesh transformation function
def DrawMeshQuad(time=0.0, f=meshtrans_null):
    line0 = [f(time, u * MeshStepX, 0.0) for u in xrange(MeshResX + 1)]
    for v in xrange(1, MeshResY + 1):
        line1 = [f(time, u * MeshStepX, v * MeshStepY) for u in xrange(MeshResX + 1)]
        XXXNOGLXXX.glBegin(GL_QUAD_STRIP)
        for col in zip(line0, line1):
            for x, y, z, s, t, i, a in col:
                XXXNOGLXXX.glColor4d(i, i, i, a)
                XXXNOGLXXX.glTexCoord2d(s * TexMaxS, t * TexMaxT)
                XXXNOGLXXX.glVertex3d(x, y, z)
        XXXNOGLXXX.glEnd()
        line0 = line1

def GenerateSpotMesh():
    global SpotMesh
    rx0 = SpotRadius * PixelX
    ry0 = SpotRadius * PixelY
    rx1 = (SpotRadius + BoxEdgeSize) * PixelX
    ry1 = (SpotRadius + BoxEdgeSize) * PixelY
    steps = max(MinSpotDetail, int(2.0 * pi * SpotRadius / SpotDetail / ZoomArea))
    SpotMesh=[(rx0 * sin(a), ry0 * cos(a), rx1 * sin(a), ry1 * cos(a)) for a in \
             [i * 2.0 * pi / steps for i in range(steps + 1)]]
