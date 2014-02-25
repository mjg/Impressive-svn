##### INITIALIZATION ###########################################################

def main():
    global gl, ScreenWidth, ScreenHeight, TexWidth, TexHeight, TexSize
    global TexMaxS, TexMaxT, EdgeX, EdgeY, PixelX, PixelY, LogoImage
    global OverviewGridSize, OverviewCellX, OverviewCellY
    global OverviewOfsX, OverviewOfsY, OverviewBorder, OverviewImage, OverviewPageCount
    global OverviewPageMap, OverviewPageMapInv, FileName, FileList, PageCount
    global DocumentTitle, PageProps, LogoTexture, OSDFont
    global Pcurrent, Pnext, Tcurrent, Tnext, InitialPage
    global CacheFile, CacheFileName, BaseWorkingDir
    global PAR, DAR, TempFileName
    global BackgroundRendering, FileStats, RTrunning, RTrestart, StartTime
    global CursorImage, CursorVisible, InfoScriptPath
    global HalfScreen, AutoAdvance, WindowPos
    global BoxFadeDarknessBase, SpotRadiusBase
    global GLVendor, GLRenderer, GLVersion
    global BoxIndexBuffer, UseBlurShader

    # allocate temporary file
    TempFileName = tempfile.mktemp(prefix="impressive-", suffix="_tmp")

    # some input guesswork
    BaseWorkingDir = os.getcwd()
    if not(FileName) and (len(FileList) == 1):
        FileName = FileList[0]
    if FileName and not(FileList):
        AddFile(FileName)
    if FileName:
        DocumentTitle = os.path.splitext(os.path.split(FileName)[1])[0]

    # early graphics initialization
    Platform.Init()

    # detect screen size and compute aspect ratio
    if Fullscreen and UseAutoScreenSize:
        size = Platform.GetScreenSize()
        if size:
            ScreenWidth, ScreenHeight = size
            print >>sys.stderr, "Detected screen size: %dx%d pixels" % (ScreenWidth, ScreenHeight)
    if DAR is None:
        PAR = 1.0
        DAR = float(ScreenWidth) / float(ScreenHeight)
    else:
        PAR = DAR / float(ScreenWidth) * float(ScreenHeight)

    # fill the page list
    if Shuffle:
        random.shuffle(FileList)
    PageCount = 0
    for name in FileList:
        ispdf = name.lower().endswith(".pdf")
        if ispdf:
            # PDF input -> try to pre-parse the PDF file
            pages = 0
            out = [(ScreenWidth + Overscan, ScreenHeight + Overscan),
                   (ScreenWidth + Overscan, ScreenHeight + Overscan)]
            res = [(72.0, 72.0), (72.0, 72.0)]

            # phase 1: internal PDF parser
            try:
                pages, pdf_width, pdf_height = analyze_pdf(name)
                out = [ZoomToFit((pdf_width, pdf_height * PAR)),
                       ZoomToFit((pdf_height, pdf_width * PAR))]
                res = [(out[0][0] * 72.0 / pdf_width, out[0][1] * 72.0 / pdf_height),
                       (out[1][1] * 72.0 / pdf_width, out[1][0] * 72.0 / pdf_height)]
            except KeyboardInterrupt:
                raise
            except:
                pass

            # phase 2: use pdftk
            try:
                assert 0 == subprocess.Popen([pdftkPath, name, "dump_data", "output", TempFileName + ".txt"]).wait()
                title, pages = pdftkParse(TempFileName + ".txt", PageCount)
                if title and (len(FileList) == 1):
                    DocumentTitle = title
            except KeyboardInterrupt:
                raise
            except:
                pass
        else:
            # Image File
            pages = 1
            SetPageProp(PageCount + 1, '_title', os.path.split(name)[-1])

        # validity check
        if not pages:
            print >>sys.stderr, "Warning: The input file `%s' could not be analyzed." % name
            continue

        # add pages and files into PageProps and FileProps
        pagerange = list(range(PageCount + 1, PageCount + pages + 1))
        for page in pagerange:
            SetPageProp(page, '_file', name)
            if ispdf: SetPageProp(page, '_page', page - PageCount)
            title = GetFileProp(name, 'title')
            if title: SetPageProp(page, '_title', title)
        SetFileProp(name, 'pages', GetFileProp(name, 'pages', []) + pagerange)
        SetFileProp(name, 'offsets', GetFileProp(name, 'offsets', []) + [PageCount])
        if not GetFileProp(name, 'stat'): SetFileProp(name, 'stat', my_stat(name))
        if ispdf:
            SetFileProp(name, 'out', out)
            SetFileProp(name, 'res', res)
        PageCount += pages

    # no pages? strange ...
    if not PageCount:
        print >>sys.stderr, "The presentation doesn't have any pages, quitting."
        sys.exit(1)

    # if rendering is wanted, do it NOW
    if RenderToDirectory:
        sys.exit(DoRender())

    # load and execute info script
    if not InfoScriptPath:
        InfoScriptPath = FileName + ".info"
    LoadInfoScript()

    # initialize some derived variables
    BoxFadeDarknessBase = BoxFadeDarkness
    SpotRadiusBase = SpotRadius

    # get the initial page number
    if not InitialPage:
        InitialPage = GetNextPage(0, 1)
    Pcurrent = InitialPage
    if (Pcurrent <= 0) or (Pcurrent > PageCount):
        print >>sys.stderr, "Attempt to start the presentation at an invalid page (%d of %d), quitting." % (InitialPage, PageCount)
        sys.exit(1)

    # initialize graphics
    try:
        Platform.StartDisplay()
    except:
        print >>sys.stderr, "FATAL: failed to create rendering surface in the desired resolution (%dx%d)" % (ScreenWidth, ScreenHeight)
        sys.exit(1)
    pygame.key.set_repeat(500, 30)
    if Fullscreen:
        pygame.mouse.set_visible(False)
        CursorVisible = False
    if (Gamma <> 1.0) or (BlackLevel <> 0):
        SetGamma(force=True)

    # initialize OpenGL
    try:
        gl = Platform.LoadOpenGL()
        GLVendor = gl.GetString(gl.VENDOR)
        GLRenderer = gl.GetString(gl.RENDERER)
        GLVersion = gl.GetString(gl.VERSION)
        print >>sys.stderr, "OpenGL renderer:", GLRenderer

        # check if graphics are unaccelerated
        renderer = GLRenderer.lower().replace(' ', '').replace('(r)', '')
        if (renderer in ("mesaglxindirect", "gdigeneric")) \
        or renderer.startswith("software") \
        or ("llvmpipe" in renderer):
            print >>sys.stderr, "WARNING: Using an OpenGL software renderer. Impressive will work, but it will"
            print >>sys.stderr, "         very likely be too slow to be usable."

        # check for old hardware that can't deal with the blur shader
        for substr in ("i915", "intel915", "intel945", "intelq3", "intelg3", "inteligd", "gma900", "gma950", "gma3000", "gma3100", "gma3150"):
            if substr in renderer:
                UseBlurShader = False

        # check the OpenGL version (2.0 needed to ensure NPOT texture support)
        glver = gl.GetString(gl.VERSION)
        extensions = set(gl.GetString(gl.EXTENSIONS).split())
        if (glver < "2") and (not("GL_ARB_shader_objects" in extensions) or not("GL_ARB_texture_non_power_of_two" in extensions)):
            raise ImportError("OpenGL version %r is below 2.0 and the necessary extensions are unavailable" % glver)
    except ImportError, e:
        print >>sys.stderr, "FATAL:", e
        print >>sys.stderr, "This likely means that your graphics driver or hardware is too old."
        sys.exit(1)

    # some further OpenGL configuration
    if Verbose:
        GLShader.LOG_DEFAULT = GLShader.LOG_IF_NOT_EMPTY
    for shader in RequiredShaders:
        shader.get_instance()
    if UseBlurShader:
        try:
            BlurShader.get_instance()
        except GLShaderCompileError:
            UseBlurShader = False
    if Verbose:
        if UseBlurShader:
            print >>sys.stderr, "Using blur shader for highlight box and spotlight mode."
        else:
            print >>sys.stderr, "Using legacy multi-pass blur for highlight box and spotlight mode."
    gl.BlendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA)
    BoxIndexBuffer = HighlightIndexBuffer(4)

    # setup the OpenGL texture size
    TexWidth  = (ScreenWidth + 3) & (-4)
    TexHeight = (ScreenHeight + 3) & (-4)
    TexMaxS = float(ScreenWidth) / TexWidth
    TexMaxT = float(ScreenHeight) / TexHeight
    TexSize = TexWidth * TexHeight * 3

    # set up some variables
    PixelX = 1.0 / ScreenWidth
    PixelY = 1.0 / ScreenHeight
    ScreenAspect = float(ScreenWidth) / float(ScreenHeight)
    EdgeX = BoxEdgeSize * PixelX
    EdgeY = BoxEdgeSize * PixelY

    # prepare logo image
    LogoImage = Image.open(StringIO.StringIO(LOGO))
    LogoTexture = gl.make_texture(gl.TEXTURE_2D, filter=gl.NEAREST, img=LogoImage)
    DrawLogo()
    Platform.SwapBuffers()

    # initialize OSD font
    try:
        OSDFont = GLFont(FontTextureWidth, FontTextureHeight, FontList, FontSize, search_path=FontPath)
        DrawLogo()
        titles = []
        for key in ('title', '_title'):
            titles.extend([p[key] for p in PageProps.itervalues() if key in p])
        if titles:
            OSDFont.AddString("".join(titles))
    except ValueError:
        print >>sys.stderr, "The OSD font size is too large, the OSD will be rendered incompletely."
    except IOError:
        print >>sys.stderr, "Could not open OSD font file, disabling OSD."
    except (NameError, AttributeError, TypeError):
        print >>sys.stderr, "Your version of PIL is too old or incomplete, disabling OSD."

    # initialize mouse cursor
    if CursorImage:
        try:
            CursorImage = PrepareCustomCursor(Image.open(CursorImage))
        except:
            print >>sys.stderr, "Could not open the mouse cursor image, using standard cursor."
            CursorImage = False

    # set up page cache
    if CacheMode == PersistentCache:
        if not CacheFileName:
            CacheFileName = FileName + ".cache"
        InitPCache()
    if CacheMode == FileCache:
        CacheFile = tempfile.TemporaryFile(prefix="impressive-", suffix=".cache")

    # initialize overview metadata
    OverviewPageMap=[i for i in xrange(1, PageCount + 1) \
        if GetPageProp(i, ('overview', '_overview'), True) \
        and (i >= PageRangeStart) and (i <= PageRangeEnd)]
    OverviewPageCount = max(len(OverviewPageMap), 1)
    OverviewPageMapInv = {}
    for page in xrange(1, PageCount + 1):
        OverviewPageMapInv[page] = len(OverviewPageMap) - 1
        for i in xrange(len(OverviewPageMap)):
            if OverviewPageMap[i] >= page:
                OverviewPageMapInv[page] = i
                break

    # initialize overview page geometry
    OverviewGridSize = 1
    while OverviewPageCount > OverviewGridSize * OverviewGridSize:
        OverviewGridSize += 1
    if HalfScreen:
        # in half-screen mode, temporarily override ScreenWidth
        saved_screen_width = ScreenWidth
        ScreenWidth /= 2
    OverviewCellX = int(ScreenWidth  / OverviewGridSize)
    OverviewCellY = int(ScreenHeight / OverviewGridSize)
    OverviewOfsX = int((ScreenWidth  - OverviewCellX * OverviewGridSize)/2)
    OverviewOfsY = int((ScreenHeight - OverviewCellY * \
                   int((OverviewPageCount + OverviewGridSize - 1) / OverviewGridSize)) / 2)
    while OverviewBorder and (min(OverviewCellX - 2 * OverviewBorder, OverviewCellY - 2 * OverviewBorder) < 16):
        OverviewBorder -= 1
    OverviewImage = Image.new('RGB', (TexWidth, TexHeight))
    if HalfScreen:
        OverviewOfsX += ScreenWidth
        ScreenWidth = saved_screen_width

    # fill overlay "dummy" images
    dummy = LogoImage.copy()
    border = max(OverviewLogoBorder, 2 * OverviewBorder)
    maxsize = (OverviewCellX - border, OverviewCellY - border)
    if (dummy.size[0] > maxsize[0]) or (dummy.size[1] > maxsize[1]):
        dummy.thumbnail(ZoomToFit(dummy.size, maxsize), Image.ANTIALIAS)
    margX = int((OverviewCellX - dummy.size[0]) / 2)
    margY = int((OverviewCellY - dummy.size[1]) / 2)
    dummy = dummy.convert(mode='RGB')
    for page in range(OverviewPageCount):
        pos = OverviewPos(page)
        OverviewImage.paste(dummy, (pos[0] + margX, pos[1] + margY))
    del dummy

    # compute auto-advance timeout, if applicable
    if EstimatedDuration and AutoAutoAdvance:
        time_left = EstimatedDuration * 1000
        pages = 0
        p = InitialPage
        while p:
            override = GetPageProp(p, 'timeout')
            if override:
                time_left -= override
            else:
                pages += 1
            pnext = GetNextPage(p, 1)
            if pnext:
                time_left -= GetPageProp(p, 'transtime', TransitionDuration)
            p = pnext
        if pages and (time_left >= pages):
            AutoAdvance = time_left / pages
            print >>sys.stderr, "Setting auto-advance timeout to %.1f seconds." % (0.001 * AutoAdvance)
        else:
            print >>sys.stderr, "Warning: Could not determine auto-advance timeout automatically."

    # set up background rendering
    if not EnableBackgroundRendering:
        print >>sys.stderr, "Background rendering isn't available on this platform."
        BackgroundRendering = False

    # if caching is enabled, pre-render all pages
    if CacheMode and not(BackgroundRendering):
        DrawLogo()
        DrawProgress(0.0)
        Platform.SwapBuffers()
        for pdf in FileProps:
            if pdf.lower().endswith(".pdf"):
                ParsePDF(pdf)
        stop = False
        progress = 0.0
        for page in range(InitialPage, PageCount + 1) + range(1, InitialPage):
            event = pygame.event.poll()
            while event.type != NOEVENT:
                if event.type == KEYDOWN:
                    if (event.key == K_ESCAPE) or (event.unicode == u'q'):
                        Quit()
                    stop = True
                elif event.type == MOUSEBUTTONUP:
                    stop = True
                event = pygame.event.poll()
            if stop: break
            if (page >= PageRangeStart) and (page <= PageRangeEnd):
                PageImage(page)
            DrawLogo()
            progress += 1.0 / PageCount;
            DrawProgress(progress)
            Platform.SwapBuffers()

    # create buffer textures
    DrawLogo()
    Platform.SwapBuffers()
    Tcurrent, Tnext = [gl.make_texture(gl.TEXTURE_2D, gl.CLAMP_TO_EDGE, gl.LINEAR) for dummy in (1,2)]

    # prebuffer current and next page
    Pnext = 0
    RenderPage(Pcurrent, Tcurrent)
    PageEntered(update_time=False)
    PreloadNextPage(GetNextPage(Pcurrent, 1))

    # some other preparations
    PrepareTransitions()
    GenerateSpotMesh()
    if PollInterval:
        pygame.time.set_timer(USEREVENT_POLL_FILE, PollInterval * 1000)

    # start the background rendering thread
    if CacheMode and BackgroundRendering:
        RTrunning = True
        thread.start_new_thread(RenderThread, (Pcurrent, Pnext))

    # parse PDF file if caching is disabled
    if not CacheMode:
        for pdf in FileProps:
            if pdf.lower().endswith(".pdf"):
                SafeCall(ParsePDF, [pdf])

    # start output and enter main loop
    StartTime = pygame.time.get_ticks()
    pygame.time.set_timer(USEREVENT_TIMER_UPDATE, 100)
    if not(Fullscreen) and CursorImage:
        pygame.mouse.set_visible(False)
    if FadeInOut:
        LeaveFadeMode()
    else:
        DrawCurrentPage()
    UpdateCaption(Pcurrent)
    while True:
        HandleEvent(pygame.event.wait())


# wrapper around main() that ensures proper uninitialization
def run_main():
    global CacheFile
    try:
        try:
            main()
        except SystemExit:
            raise
        except KeyboardInterrupt:
            pass
        except:
            print >>sys.stderr
            print >>sys.stderr, 79 * "="
            print >>sys.stderr, "OOPS! Impressive crashed!"
            print >>sys.stderr, "This shouldn't happen. Please report this incident to the author, including the"
            print >>sys.stderr, "full output of the program, particularly the following lines. If possible,"
            print >>sys.stderr, "please also send the input files you used."
            print >>sys.stderr
            print >>sys.stderr, "Impressive version:", __version__
            print >>sys.stderr, "Python version:", sys.version
            print >>sys.stderr, "PyGame version:", pygame.__version__
            print >>sys.stderr, "PIL version:", Image.VERSION
            if GLVendor: print >>sys.stderr, "OpenGL vendor:", GLVendor
            if GLRenderer: print >>sys.stderr, "OpenGL renderer:", GLRenderer
            if GLVersion: print >>sys.stderr, "OpenGL version:", GLVersion
            if hasattr(os, 'uname'):
                uname = os.uname()
                print >>sys.stderr, "Operating system: %s %s (%s)" % (uname[0], uname[2], uname[4])
            else:
                print >>sys.stderr, "Python platform:", sys.platform
            if os.path.isfile("/usr/bin/lsb_release"):
                lsb_release = subprocess.Popen(["/usr/bin/lsb_release", "-sd"], stdout=subprocess.PIPE)
                print >>sys.stderr, "Linux distribution:", lsb_release.stdout.read().strip()
                lsb_release.wait()
            print >>sys.stderr, "Command line:", ' '.join(('"%s"'%arg if (' ' in arg) else arg) for arg in sys.argv)
            raise
    finally:
        StopMPlayer()
        # ensure that background rendering is halted
        Lrender.acquire()
        Lcache.acquire()
        # remove all temp files
        if 'CacheFile' in globals():
            del CacheFile
        for tmp in glob.glob(TempFileName + "*"):
            try:
                os.remove(tmp)
            except OSError:
                pass
        pygame.quit()

    # release all locks
    try:
        if Lrender.locked():
            Lrender.release()
    except:
        pass
    try:
        if Lcache.locked():
            Lcache.release()
    except:
        pass
    try:
        if Loverview.locked():
            Loverview.release()
    except:
        pass
