##### TRANSITIONS ##############################################################

# Each transition is represented by a class derived from impressive.Transition
# The interface consists of only two methods: the __init__ method may perform
# some transition-specific initialization, and render() finally renders a frame
# of the transition, using the global texture identifiers Tcurrent and Tnext.

class Transition(object):
    def render(self):
        pass

# an array containing all possible transition classes
AllTransitions = []


# Crossfade: one of the simplests transition you can think of :)
class Crossfade(Transition):
    """simple crossfade"""
    class CrossfadeShader(GLShader):
        vs = """
            attribute highp vec2 aPos;
            varying mediump vec2 vTexCoord;
            void main() {
                gl_Position = vec4(vec2(-1.0, 1.0) + aPos * vec2(2.0, -2.0), 0.0, 1.0);
                vTexCoord = aPos;
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
        uniforms = ['uTcurrent', ('uTnext', 1), 'uTime']
    def render(self,t):
        shader = self.CrossfadeShader.get_instance(False).use()
        gl.set_texture(gl.TEXTURE_2D, Tnext, 1)
        gl.set_texture(gl.TEXTURE_2D, Tcurrent, 0)
        gl.Uniform1f(shader.uTime, t)
        SimpleQuad.draw()
AllTransitions.append(Crossfade)


# the AvailableTransitions array contains a list of all transition classes that
# can be randomly assigned to pages;
# this selection normally only includes "unintrusive" transtitions, i.e. mostly
# crossfade variations
AvailableTransitions = [ # from coolest to lamest
    Crossfade
]
