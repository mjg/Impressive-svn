##### RENDERING TOOL CODE ######################################################

def GenerateSpotMesh():
    global SpotMesh
    rx0 = SpotRadius * PixelX
    ry0 = SpotRadius * PixelY
    rx1 = (SpotRadius + BoxEdgeSize) * PixelX
    ry1 = (SpotRadius + BoxEdgeSize) * PixelY
    steps = max(MinSpotDetail, int(2.0 * pi * SpotRadius / SpotDetail / ZoomArea))
    SpotMesh=[(rx0 * sin(a), ry0 * cos(a), rx1 * sin(a), ry1 * cos(a)) for a in \
             [i * 2.0 * pi / steps for i in range(steps + 1)]]
