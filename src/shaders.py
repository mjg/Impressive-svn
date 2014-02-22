##### STOCK SHADERS ############################################################

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

    _vbuf = None
    def draw(self, x0, y0, x1, y1, s1=1.0, t1=1.0, tex=None, color=None):
        self.use()
        if tex:
            gl.BindTexture(gl.TEXTURE_2D, tex)
        gl.set_enabled_attribs(0)
        if not self.__class__._vbuf:
            self.__class__._vbuf = gl.GenBuffers()
            gl.BindBuffer(gl.ARRAY_BUFFER, self.__class__._vbuf)
            gl.BufferData(gl.ARRAY_BUFFER, data=[0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0])
        else:
            gl.BindBuffer(gl.ARRAY_BUFFER, self.__class__._vbuf)
        gl.VertexAttribPointer(0, 2, gl.FLOAT, False, 0, 0)
        if not color:
            gl.Uniform(self.uColor, 1.0, 1.0, 1.0, 1.0)
        elif isinstance(color, float):
            gl.Uniform(self.uColor, color, color, color, 1.0)
        elif len(color) == 3:
            gl.Uniform(self.uColor, color + [1.0])
        else:
            gl.Uniform(self.uColor, color)
        gl.Uniform(self.uPosTransform, x0, y0, x1 - x0, y1 - y0)
        gl.Uniform(self.uScreenTransform, ScreenTransform)
        gl.Uniform(self.uTexTransform, 0.0, 0.0, s1, t1)
        gl.DrawArrays(gl.TRIANGLE_STRIP, 0, 4)
RequiredShaders.append(TexturedRectShader)
