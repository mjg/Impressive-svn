##### PLATFORM-SPECIFIC PYGAME INTERFACE CODE ##################################

class Platform_PyGame(object):
    name = 'pygame'
    allow_custom_fullscreen_res = True

    def __init__(self):
        pass

    def Init(self):
        pygame.display.init()

    def GetScreenSize(self):
        return pygame.display.list_modes()[0]

    def StartDisplay(self):
        global ScreenWidth, ScreenHeight, Fullscreen, FakeFullscreen, WindowPos
        pygame.display.set_caption(__title__)
        flags = OPENGL | DOUBLEBUF
        if Fullscreen:
            if FakeFullscreen:
                print >>sys.stderr, "Using \"fake-fullscreen\" mode."
                flags |= NOFRAME
                if not WindowPos:
                    WindowPos = (0,0)
            else:
                flags |= FULLSCREEN
        if WindowPos:
            os.environ["SDL_VIDEO_WINDOW_POS"] = ','.join(map(str, WindowPos))
        pygame.display.set_mode((ScreenWidth, ScreenHeight), flags)

    def LoadOpenGL(self):
        try:
            sdl = CDLL(ctypes.util.find_library("SDL") or "SDL", RTLD_GLOBAL)
            get_proc_address = CFUNCTYPE(c_void_p, c_char_p)(('SDL_GL_GetProcAddress', sdl))
        except OSError:
            raise ImportError("failed to load the SDL library")
        except AttributeError:
            raise ImportError("failed to load SDL_GL_GetProcAddress from the SDL library")
        def loadsym(name, prototype):
            addr = get_proc_address(name)
            if not addr:
                return None
            return prototype(addr)
        return OpenGL(loadsym, desktop=True)

    def SwapBuffers(self):
        pygame.display.flip()

    def Done(self):
        pygame.display.quit()


class Platform_Win32(Platform_PyGame):
    name = 'pygame-win32'

    def GetScreenSize(self):
        if HaveWin32API:
            dm = win32api.EnumDisplaySettings(None, -1) #ENUM_CURRENT_SETTINGS
            return (int(dm.PelsWidth), int(dm.PelsHeight))
        return Platform_PyGame.get_screen_size(self)


class Platform_Unix(Platform_PyGame):
    name = 'pygame-unix'

    def GetScreenSize(self):
        re_res = re.compile(r'\s*(\d+)x(\d+)\s+\d+\.\d+\*')
        res = None
        try:
            xrandr = subprocess.Popen(["xrandr"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in xrandr.stdout:
                m = re_res.match(line)
                if m:
                    res = tuple(map(int, m.groups()))
            xrandr.wait()
        except OSError:
            pass
        if res:
            return res
        return Platform_PyGame.get_screen_size(self)


class Platform_EGL(Platform_Unix):
    name = 'egl'

    def StartDisplay(self, display=None, window=None, width=None, height=None):
        global ScreenWidth, ScreenHeight
        width  = width  or ScreenWidth
        height = height or ScreenHeight

        # load the GLESv2 library before the EGL library (required on the BCM2835)
        try:
            self.gles = ctypes.CDLL(ctypes.util.find_library("GLESv2"))
        except OSError:
            raise ImportError("failed to load the OpenGL ES 2.0 library")

        # import all functions first
        try:
            egl = CDLL(ctypes.util.find_library("EGL"))
            def loadfunc(func, ret, *args):
                return CFUNCTYPE(ret, *args)((func, egl))
            eglGetDisplay = loadfunc("eglGetDisplay", c_void_p, c_void_p)
            eglInitialize = loadfunc("eglInitialize", c_uint, c_void_p, POINTER(c_int), POINTER(c_int))
            eglChooseConfig = loadfunc("eglChooseConfig", c_uint, c_void_p, c_void_p, POINTER(c_void_p), c_int, POINTER(c_int))
            eglCreateWindowSurface = loadfunc("eglCreateWindowSurface", c_void_p, c_void_p, c_void_p, c_void_p, c_void_p)
            eglCreateContext = loadfunc("eglCreateContext", c_void_p, c_void_p, c_void_p, c_void_p, c_void_p)
            eglMakeCurrent = loadfunc("eglMakeCurrent", c_uint, c_void_p, c_void_p, c_void_p, c_void_p)
            self.eglSwapBuffers = loadfunc("eglSwapBuffers", c_int, c_void_p, c_void_p)
        except OSError:
            raise ImportError("failed to load the EGL library")
        except AttributeError:
            raise ImportError("failed to load required symbols from the EGL library")

        # prepare parameters
        config_attribs = [
            0x3024, 8,      # EGL_RED_SIZE >= 8
            0x3023, 8,      # EGL_GREEN_SIZE >= 8
            0x3022, 8,      # EGL_BLUE_SIZE >= 8
            0x3021, 0,      # EGL_ALPHA_SIZE >= 0
            0x3025, 0,      # EGL_DEPTH_SIZE >= 0
            0x3040, 0x0004, # EGL_RENDERABLE_TYPE = EGL_OPENGL_ES2_BIT
            0x3033, 0x0004, # EGL_SURFACE_TYPE = EGL_WINDOW_BIT
            0x3038          # EGL_NONE
        ]
        context_attribs = [
            0x3098, 2,      # EGL_CONTEXT_CLIENT_VERSION = 2
            0x3038          # EGL_NONE
        ]
        config_attribs = (c_int * len(config_attribs))(*config_attribs)
        context_attribs = (c_int * len(context_attribs))(*context_attribs)

        # perform actual initialization
        eglMakeCurrent(None, None, None, None)
        self.egl_display = eglGetDisplay(display)
        if not self.egl_display:
            raise RuntimeError("could not get EGL display")
        if not eglInitialize(self.egl_display, None, None):
            raise RuntimeError("could not initialize EGL")
        config = c_void_p()
        num_configs = c_int(0)
        if not eglChooseConfig(self.egl_display, config_attribs, byref(config), 1, byref(num_configs)):
            raise RuntimeError("failed to get a framebuffer configuration")
        if not num_configs.value:
            raise RuntimeError("no suitable framebuffer configuration found")
        self.egl_surface = eglCreateWindowSurface(self.egl_display, config, window, None)
        if not self.egl_surface:
            raise RuntimeError("could not create EGL surface")
        context = eglCreateContext(self.egl_display, config, None, context_attribs)
        if not context:
            raise RuntimeError("could not create OpenGL ES rendering context")
        if not eglMakeCurrent(self.egl_display, self.egl_surface, self.egl_surface, context):
            raise RuntimeError("could not activate OpenGL ES rendering context")

    def LoadOpenGL(self):
        def loadsym(name, prototype):
            return prototype((name, self.gles))
        return OpenGL(loadsym, desktop=False)

    def SwapBuffers(self):
        self.eglSwapBuffers(self.egl_display, self.egl_surface)


class Platform_BCM2835(Platform_EGL):
    name = 'bcm2835'
    allow_custom_fullscreen_res = False
    DISPLAY_ID = 0

    def __init__(self, libbcm_host):
        self.libbcm_host_path = libbcm_host

    def Init(self):
        try:
            self.bcm_host = CDLL(self.libbcm_host_path)
            def loadfunc(func, ret, *args):
                return CFUNCTYPE(ret, *args)((func, self.bcm_host))
            bcm_host_init = loadfunc("bcm_host_init", None)
            graphics_get_display_size = loadfunc("graphics_get_display_size", c_int32, c_uint16, POINTER(c_uint32), POINTER(c_uint32))
        except OSError:
            raise ImportError("failed to load the bcm_host library")
        except AttributeError:
            raise ImportError("failed to load required symbols from the bcm_host library")
        bcm_host_init()
        x, y = c_uint32(0), c_uint32(0)
        if graphics_get_display_size(self.DISPLAY_ID, byref(x), byref(y)) < 0:
            raise RuntimeError("could not determine display size")
        self.screen_size = (int(x.value), int(y.value))

    def GetScreenSize(self):
        return self.screen_size

    def StartDisplay(self):
        global ScreenWidth, ScreenHeight, Fullscreen, FakeFullscreen, WindowPos
        class VC_DISPMANX_ALPHA_T(Structure):
            _fields_ = [("flags", c_int), ("opacity", c_uint32), ("mask", c_void_p)]
        class EGL_DISPMANX_WINDOW_T(Structure):
            _fields_ = [("element", c_uint32), ("width", c_int), ("height", c_int)]

        # first, import everything
        try:
            def loadfunc(func, ret, *args):
                return CFUNCTYPE(ret, *args)((func, self.bcm_host))
            vc_dispmanx_display_open = loadfunc("vc_dispmanx_display_open", c_uint32, c_uint32)
            vc_dispmanx_update_start = loadfunc("vc_dispmanx_update_start", c_uint32, c_int32)
            vc_dispmanx_element_add = loadfunc("vc_dispmanx_element_add", c_int32,
                c_uint32, c_uint32, c_int32,  # update, display, layer
                c_void_p, c_uint32, c_void_p, c_uint32,  # dest_rect, src, drc_rect, protection
                POINTER(VC_DISPMANX_ALPHA_T),  # alpha
                c_void_p, c_uint32)  # clamp, transform
            vc_dispmanx_update_submit_sync = loadfunc("vc_dispmanx_update_submit_sync", c_int, c_uint32)
        except AttributeError:
            raise ImportError("failed to load required symbols from the bcm_host library")

        # sanitize arguments
        width  = min(ScreenWidth,  self.screen_size[0])
        height = min(ScreenHeight, self.screen_size[1])
        if WindowPos:
            x0, y0 = WindowPos
        else:
            x0 = (self.screen_size[0] - width)  / 2
            y0 = (self.screen_size[1] - height) / 2
        x0 = max(min(x0, self.screen_size[0] - width),  0)
        y0 = max(min(y0, self.screen_size[1] - height), 0)

        # prepare arguments
        dst_rect = (c_int32 * 4)(x0, y0, width, height)
        src_rect = (c_int32 * 4)(0, 0, width << 16, height << 16)
        alpha = VC_DISPMANX_ALPHA_T(1, 255, None)  # DISPMANX_FLAGS_ALPHA_FIXED_ALL_PIXELS

        # perform initialization
        display = vc_dispmanx_display_open(self.DISPLAY_ID)
        update = vc_dispmanx_update_start(0)
        layer = vc_dispmanx_element_add(update, display, 0, byref(dst_rect), 0, byref(src_rect), 0, byref(alpha), None, 0)
        vc_dispmanx_update_submit_sync(update)
        self.window = EGL_DISPMANX_WINDOW_T(layer, width, height)
        Platform_EGL.StartDisplay(self, None, byref(self.window), width, height)
        pygame.display.set_mode((width, height), 0)


libbcm_host = ctypes.util.find_library("bcm_host")
if libbcm_host:
    Platform = Platform_BCM2835(libbcm_host)
elif os.name == "nt":
    Platform = Platform_Win32()
else:
    Platform = Platform_Unix()