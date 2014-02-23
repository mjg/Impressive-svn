##### STOCK SHADERS ############################################################

class SimpleQuad(object):
    "vertex buffer singleton for a simple quad (used by various shaders)"
    vbuf = None
    @classmethod
    def draw(self):
        gl.set_enabled_attribs(0)
        if not self.vbuf:
            self.vbuf = gl.GenBuffers()
            gl.BindBuffer(gl.ARRAY_BUFFER, self.vbuf)
            gl.BufferData(gl.ARRAY_BUFFER, data=[0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0])
        else:
            gl.BindBuffer(gl.ARRAY_BUFFER, self.vbuf)
        gl.VertexAttribPointer(0, 2, gl.FLOAT, False, 0, 0)
        gl.DrawArrays(gl.TRIANGLE_STRIP, 0, 4)


class TexturedRectShader(GLShader):
    vs = """
        attribute highp vec2 aPos;
        uniform highp vec4 uPosTransform;
        uniform highp vec4 uScreenTransform;
        uniform highp vec4 uTexTransform;
        varying mediump vec2 vTexCoord;
        void main() {
            highp vec2 pos = uPosTransform.xy + aPos * uPosTransform.zw;
            gl_Position = vec4(uScreenTransform.xy + pos * uScreenTransform.zw, 0.0, 1.0);
            vTexCoord = uTexTransform.xy + aPos * uTexTransform.zw;
        }
    """
    fs = """
        uniform lowp vec4 uColor;
        uniform lowp sampler2D uTex;
        varying mediump vec2 vTexCoord;
        void main() {
            gl_FragColor = uColor * texture2D(uTex, vTexCoord);
        }
    """
    attributes = { 0: 'aPos' }
    uniforms = ['uPosTransform', 'uScreenTransform', 'uTexTransform', 'uColor']

    def draw(self, x0, y0, x1, y1, s0=0.0, t0=0.0, s1=1.0, t1=1.0, tex=None, color=None):
        self.use()
        if tex:
            gl.BindTexture(gl.TEXTURE_2D, tex)
        if not color:
            gl.Uniform4f(self.uColor, 1.0, 1.0, 1.0, 1.0)
        elif isinstance(color, float):
            gl.Uniform4f(self.uColor, color, color, color, 1.0)
        else:
            gl.Uniform(self.uColor, color)
        gl.Uniform(self.uPosTransform, x0, y0, x1 - x0, y1 - y0)
        gl.Uniform(self.uScreenTransform, ScreenTransform)
        gl.Uniform(self.uTexTransform, s0, t0, s1 - s0, t1 - t0)
        SimpleQuad.draw()
RequiredShaders.append(TexturedRectShader)


class ProgressBarShader(GLShader):
    vs = """
        attribute highp vec2 aPos;
        uniform highp vec4 uPosTransform;
        uniform lowp vec4 uColor0;
        uniform lowp vec4 uColor1;
        varying lowp vec4 vColor;
        void main() {
            gl_Position = vec4(uPosTransform.xy + aPos * uPosTransform.zw, 0.0, 1.0);
            vColor = mix(uColor0, uColor1, aPos.y);
        }
    """
    fs = """
        varying lowp vec4 vColor;
        void main() {
            gl_FragColor = vColor;
        }
    """
    attributes = { 0: 'aPos' }
    uniforms = ['uPosTransform', 'uColor0', 'uColor1']

    def draw(self, x0, y0, x1, y1, color0, color1):
        self.use()
        gl.Uniform(self.uPosTransform,
            -1.0 + 2.0 * x0,
            +1.0 - 2.0 * y0,
            2.0 * (x1 - x0),
            2.0 * (y0 - y1))
        gl.Uniform(self.uColor0, color0)
        gl.Uniform(self.uColor1, color1)
        SimpleQuad.draw()
RequiredShaders.append(ProgressBarShader)
