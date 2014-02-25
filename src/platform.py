##### PLATFORM-SPECIFIC PYGAME INTERFACE CODE ##################################

class Platform_PyGame(object):
    name = 'pygame'

    def __init__(self):
        pass

    def Init(self):
        pygame.display.init()

    def GetScreenSize(self):
        return pygame.display.list_modes()[0]

    def StartDisplay(self):
        global Fullscreen, FakeFullscreen, WindowPos, ScreenWidth, ScreenHeight
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


if os.name == "nt":
    Platform = Platform_Win32()
else:
    Platform = Platform_Unix()
