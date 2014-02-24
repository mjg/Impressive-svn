##### TRANSITIONS ##############################################################

# base class for all transitions
class Transition(object):

    # constructor: must instantiate (i.e. compile) all required shaders
    # and (optionally) perform some additional initialization
    def __init__(self):
        pass

    # called once at the start of each transition
    def start(self):
        pass

    # render a frame of the transition, using the relative time 't' and the
    # global texture identifiers Tcurrent and Tnext
    def render(self, t):
        pass

# smoothstep() makes most transitions better :)
def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)

# an array containing all possible transition classes
AllTransitions = []


class Crossfade(Transition):
    """simple crossfade"""
    class CrossfadeShader(GLShader):
        vs = """
            attribute highp vec2 aPos;
            uniform highp vec4 uTexTransform;
            varying mediump vec2 vTexCoord;
            void main() {
                gl_Position = vec4(vec2(-1.0, 1.0) + aPos * vec2(2.0, -2.0), 0.0, 1.0);
                vTexCoord = uTexTransform.xy + aPos * uTexTransform.zw;
            }
        """
        fs = """
            uniform lowp sampler2D uTcurrent;
            uniform lowp sampler2D uTnext;
            uniform lowp float uTime;
            varying mediump vec2 vTexCoord;
            void main() {
                gl_FragColor = mix(texture2D(uTcurrent, vTexCoord), texture2D(uTnext, vTexCoord), uTime);
            }
        """
        attributes = { 0: 'aPos' }
        uniforms = [('uTnext', 1), 'uTexTransform', 'uTime']
    def __init__(self):
        shader = self.CrossfadeShader.get_instance().use()
        gl.Uniform4f(shader.uTexTransform, 0.0, 0.0, TexMaxS, TexMaxT)
    def render(self, t):
        shader = self.CrossfadeShader.get_instance().use()
        gl.set_texture(gl.TEXTURE_2D, Tnext, 1)
        gl.set_texture(gl.TEXTURE_2D, Tcurrent, 0)
        gl.Uniform1f(shader.uTime, t)
        SimpleQuad.draw()
AllTransitions.append(Crossfade)


class FadeOutFadeIn(Transition):
    "fade out to black and fade in again"
    def render(self, t):
        if t < 0.5:
            tex = Tcurrent
            t = 1.0 - 2.0 * t
        else:
            tex = Tnext
            t = 2.0 * t - 1.0
        TexturedRectShader.get_instance().draw(
            0.0, 0.0, 1.0, 1.0,
            s1=TexMaxS, t1=TexMaxT,
            tex=tex,
            color=(t, t, t, 1.0)
        )
AllTransitions.append(FadeOutFadeIn)


class Slide(Transition):
    def render(self, t):
        t = smoothstep(t)
        x = self.dx * t
        y = self.dy * t
        TexturedRectShader.get_instance().draw(
            x, y, x + 1.0, y + 1.0,
            s1=TexMaxS, t1=TexMaxT,
            tex=Tcurrent
        )
        TexturedRectShader.get_instance().draw(
            x - self.dx,       y - self.dy,
            x - self.dx + 1.0, y - self.dy + 1.0,
            s1=TexMaxS, t1=TexMaxT,
            tex=Tnext
        )
class SlideUp(Slide):
    "slide upwards"
    dx, dy = 0.0, -1.0
class SlideDown(Slide):
    "slide downwards"
    dx, dy = 0.0, 1.0
class SlideLeft(Slide):
    "slide to the left"
    dx, dy = -1.0, 0.0
class SlideRight(Slide):
    "slide to the right"
    dx, dy = 1.0, 0.0
AllTransitions.extend([SlideUp, SlideDown, SlideLeft, SlideRight])


class Squeeze(Transition):
    def render(self, t):
        for tex, x0, y0, x1, y1 in self.getparams(smoothstep(t)):
            TexturedRectShader.get_instance().draw(
                x0, y0, x1, y1,
                s1=TexMaxS, t1=TexMaxT,
                tex=tex
            )
class SqueezeUp(Squeeze):
    "squeeze upwards"
    def getparams(self, t):
        return ((Tcurrent, 0.0, 0.0, 1.0, 1.0 - t),
                (Tnext,    0.0, 1.0 - t, 1.0, 1.0))
class SqueezeDown(Squeeze):
    "squeeze downwards"
    def getparams(self, t):
        return ((Tcurrent, 0.0, t, 1.0, 1.0),
                (Tnext,    0.0, 0.0, 1.0, t))
class SqueezeLeft(Squeeze):
    "squeeze to the left"
    def getparams(self, t):
        return ((Tcurrent, 0.0, 0.0, 1.0 - t, 1.0),
                (Tnext,    1.0 - t, 0.0, 1.0, 1.0))
class SqueezeRight(Squeeze):
    "squeeze to the right"
    def getparams(self, t):
        return ((Tcurrent, t, 0.0, 1.0, 1.0),
                (Tnext,    0.0, 0.0, t, 1.0))
AllTransitions.extend([SqueezeUp, SqueezeDown, SqueezeLeft, SqueezeRight])


class Wipe(Transition):
    band_size = 0.5    # relative size of the wiping band
    rx, ry = 16, 16    # mask texture resolution
    class_mask = True  # True if the mask shall be shared between all instances of this subclass
    class WipeShader(GLShader):
        vs = """
            attribute highp vec2 aPos;
            uniform highp vec4 uTexTransform;
            uniform highp vec4 uMaskTransform;
            varying mediump vec2 vTexCoord;
            varying mediump vec2 vMaskCoord;
            void main() {
                gl_Position = vec4(vec2(-1.0, 1.0) + aPos * vec2(2.0, -2.0), 0.0, 1.0);
                vTexCoord = uTexTransform.xy + aPos * uTexTransform.zw;
                vMaskCoord = uMaskTransform.xy + aPos * uMaskTransform.zw;
            }
        """
        fs = """
            uniform lowp sampler2D uTcurrent;
            uniform lowp sampler2D uTnext;
            uniform mediump sampler2D uMaskTex;
            uniform mediump vec2 uAlphaTransform;
            varying mediump vec2 vTexCoord;
            varying mediump vec2 vMaskCoord;
            void main() {
                mediump float mask = texture2D(uMaskTex, vMaskCoord).r;
                mask = (mask + uAlphaTransform.x) * uAlphaTransform.y;
                mask = smoothstep(0.0, 1.0, mask);
                gl_FragColor = mix(texture2D(uTnext, vTexCoord), texture2D(uTcurrent, vTexCoord), mask);
                // gl_FragColor = texture2D(uMaskTex, vMaskCoord);  // uncomment for mask debugging
            }
        """
        attributes = { 0: 'aPos' }
        uniforms = [('uTnext', 1), ('uMaskTex', 2), 'uTexTransform', 'uMaskTransform', 'uAlphaTransform']
        def __init__(self):
            GLShader.__init__(self)
            self.mask_tex = gl.make_texture(gl.TEXTURE_2D, gl.CLAMP_TO_EDGE, gl.LINEAR)
    mask = None
    def __init__(self):
        shader = self.WipeShader.get_instance().use()
        gl.Uniform4f(shader.uTexTransform, 0.0, 0.0, TexMaxS, TexMaxT)
        if not self.class_mask:
            self.mask = self.prepare_mask()
        elif not self.mask:
            self.__class__.mask = self.prepare_mask()
    def start(self):
        shader = self.WipeShader.get_instance().use()
        gl.Uniform4f(shader.uMaskTransform,
            0.5 / self.rx, 0.5 / self.ry,
            1.0 - 1.0 / self.rx,
            1.0 - 1.0 / self.ry)
        gl.BindTexture(gl.TEXTURE_2D, shader.mask_tex)
        gl.TexImage2D(gl.TEXTURE_2D, 0, gl.LUMINANCE, self.rx, self.ry, 0, gl.LUMINANCE, gl.UNSIGNED_BYTE, self.mask)
    def render(self, t):
        shader = self.WipeShader.get_instance().use()
        gl.set_texture(gl.TEXTURE_2D, shader.mask_tex, 2)
        gl.set_texture(gl.TEXTURE_2D, Tnext, 1)
        gl.set_texture(gl.TEXTURE_2D, Tcurrent, 0)
        gl.Uniform2f(shader.uAlphaTransform,
            self.band_size - t * (1.0 + self.band_size),
            1.0 / self.band_size)
        SimpleQuad.draw()
    def prepare_mask(self):
        scale = 1.0 / (self.rx - 1)
        xx = [i * scale for i in xrange((self.rx + 3) & (~3))]
        scale = 1.0 / (self.ry - 1)
        yy = [i * scale for i in xrange(self.ry)]
        return ''.join(chr(max(0, min(255, int(self.f(x, y) * 255.0 + 0.5)))) for y, x in itertools.product(yy, xx))
    def f(self, x, y):
        return 0.5
class WipeLeft(Wipe):
    "wipe from right to left"
    def f(self, x, y):
        return 1.0 - x
class WipeRight(Wipe):
    "wipe from left to right"
    def f(self, x, y):
        return x
class WipeUp(Wipe):
    "wipe upwards"
    def f(self, x, y):
        return 1.0 - y
class WipeDown(Wipe):
    "wipe downwards"
    def f(self, x, y):
        return y
class WipeUpLeft(Wipe):
    "wipe from the lower-right to the upper-left corner"
    def f(self, x, y):
        return 1.0 - 0.5 * (x + y)
class WipeUpRight(Wipe):
    "wipe from the lower-left to the upper-right corner"
    def f(self, x, y):
        return 0.5 * (1.0 - y + x)
class WipeDownLeft(Wipe):
    "wipe from the upper-right to the lower-left corner"
    def f(self, x, y):
        return 0.5 * (1.0 - x + y)
class WipeDownRight(Wipe):
    "wipe from the upper-left to the lower-right corner"
    def f(self, x, y):
        return 0.5 * (x + y)
class WipeCenterOut(Wipe):
    "wipe from the center outwards"
    rx, ry = 64, 32
    def __init__(self):
        self.scale = 1.0
        self.scale = 1.0 / self.f(0.0, 0.0)
        Wipe.__init__(self)
    def f(self, x, y):
        return hypot((x - 0.5) * DAR, y - 0.5) * self.scale
class WipeCenterIn(Wipe):
    "wipe from the corners inwards"
    rx, ry = 64, 32
    def __init__(self):
        self.scale = 1.0
        self.scale = 1.0 / (1.0 - self.f(0.0, 0.0))
        Wipe.__init__(self)
    def f(self, x, y):
        return 1.0 - hypot((x - 0.5) * DAR, y - 0.5) * self.scale
AllTransitions.extend([WipeLeft, WipeRight, WipeUp, WipeDown, WipeUpLeft, WipeUpRight, WipeDownLeft, WipeDownRight, WipeCenterOut, WipeCenterIn])


# the AvailableTransitions array contains a list of all transition classes that
# can be randomly assigned to pages;
# this selection normally only includes "unintrusive" transtitions, i.e. mostly
# crossfade variations
AvailableTransitions = [ # from coolest to lamest
    WipeCenterOut,
    WipeDownRight, WipeRight, WipeDown,
    Crossfade
]


"""
missing transitions in gl2 branch so far:
  PagePeel      - an unrealistic, but nice page peel effect
  PageTurn      - another page peel effect, slower but more realistic than PagePeel
  SpinOutIn     - spins the current page out, and the next one in.
  SpiralOutIn   - flushes the current page away to have the next one overflow
* WipeBlobs     - wipe using nice "blob"-like patterns
  ZoomOutIn     - zooms the current page out, and the next one in.
"""
#AvailableTransitions = [AllTransitions[-1]]
