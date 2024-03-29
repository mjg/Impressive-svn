<?php include("menu.php"); ?>

<h1><span class="date">2023-11-04</span>A new maintenance release: 0.13.2</h1>
<p>Again, long time no update, but changes in libraries Impressive depends on again forced my hand here: This time, it's Pillow (the successor of the Python Imaging Library) that deprecated a few APIs for whatever reason, making Impressive 0.13.1 crash on newer Linux distributions that ship with this newer library version. 0.13.2 fixes this and a few other bugs as well. There are no functional changes.</p>

<h1><span class="date">2022-03-19</span>0.13.1 brings SDL 2 support</h1>
<p>There hasn't been an update for a long time, and you might wonder what happened to the &raquo;final&laquo; version of 0.13.0. I decided to skip it, because 0.13.1 introduces another important compatibility feature: suport for PyGame 2 and SDL 2. Other than that, it's mostly bug fixes and little enhancements here and there.</p>
<p>Unfortunately, there are some caveats with PyGame 2 support, which are out of my control; specifically, there's frequently trouble with PyGame 2.0 on Linux systems, but those seem to be fixed with PyGame 2.1. And if you're using a Raspberry Pi of generation 1 to 3, do yourself a favor and stay at the older <code>buster</code> version of Raspbian, &raquo;Raspbery Pi OS (Legacy)&laquo;. While Impressive has been adapted to work with the current <code>bullseye</code> version, that doesn't offer 3D acceleration on those older Pi models (yet?), and only shows a black screen if you force it. Raspberry Pi 4 users are not affected.</p>

<h1><span class="date">2020-05-31</span>Some maintenance in 0.13.0-beta2</h1>
<p>The second beta version brings the expected bugfixes (mainly crashes on Python 3 due to oversights during porting), but also a few minor new features: High-DPI scaling is now disabled on Windows, so that the display isn't as blurry as it used to be on affected systems. New <code>prev</code> and <code>next</code> PageProps have been introduced to change the playback order of pages. Finally, there's now a &raquo;pseudo-binary&laquo; file called <code>impressive</code> in the <code>.tar.gz</code> release archive that's more compact and with slightly quicker startup time than the standard source code file.</p>

<h1><span class="date">2019-11-21</span>A Linux-specific hotfix in 0.13.0-beta1a</h1>
<p>While testing on various machines, a rather nasty bug has been found on Linux: If the PyGame library has been installed using pip (Python's own package manager) instead of a distribution package, it would simply crash hard. 0.13.0-beta1a explicitly fixes this. Windows is not affected at all, so there's no new Win32 package.</p>

<h1><span class="date">2019-11-20</span>Towards Python 3 with 0.13.0-beta1</h1>
<p>The next major version bump is immanent, but this time, it isn't much about features on the surface, but rather profound changes under the hood: With a lot of help from the Fedora project, Impressive has finally been made compatible with Python 3.x. This is important because Python 2.x is discontinued and will no longer be supported in 2020. The amount of changes needed to ensure this Python 3 compatibility is quite large though, and as the version string indicates, there may still be some issues lurking around, even though it proved stable in my testing so far.</p>
<p>Other than that, there aren't many changes: The Win32 package is now built with Python 3 too, and for 64-bit architectures. The page count for the <code>--page-progress</code> option can now be limited (to compensate for backup slides, for example), the overview animation time can be configured independently from the zoom animation time, and more than one progress bar can now be displayed at once.</p>

<h1><span class="date">2019-08-28</span>Some maintenance in 0.12.1</h1>
<p>After one and a half years, there is now a new release that fixes a few issues, mainly with new library versions. The only new feature is that automatic slideshows can now be paused temporarily by pressing the [A] key. Furthermore, Impressive should now run on Raspberry Pi 4, but (contrary to how it was for earlier RasPi generations) only inside an X11 session.</p>
<p>This is most likely the last version of Impressive that requires Python 2.7 to run; behind the curtains, preparations are made for a next version that will run on Python 3 as well.</p>

<h1><span class="date">2018-02-04</span>0.11.3 and 0.12.0, the unexpected feature release</h1>
<p>Sometimes things just don't work out as planned. 0.11.2 had a rather nasty bug that broke automatic presentations (the <code>-a</code>/<code>--auto</code> option), so 0.11.3 was planned as a bugfix release to take care of that and some other little issues that made hyperlinks not work properly in every situation, or even crash when clicking them in some PDFs.</p>
<p>But then a very avid user of Impressive informed me of some modifications he did and ideas for other features, and I just couldn't keep myself from implementing it all ... so here we have it: 0.12.0, a totally unplanned feature release! It mainly does two things:<br />
One, it greatly enhances zoom mode, with fractional zoom levels, mouse wheel zooming, and the so-called &raquo;box zoom&laquo; mode, where you can draw a box just like a highlight box, except that Impressive zooms in so the box fills the whole screen and darkens everything else.<br />
Two, it takes video a little more seriously: Video files can now be specified as input files, just like images and PDFs. The video player backends have been a little modernized (particularly on Windows), and video is now supported on the Raspberry Pi as well.</p>

<h1><span class="date">2017-12-19</span>0.11.2, a maintenance release</h1>
<p>This version doesn't add any major features, but it's more stable and compatible with newer software environments. The largest change is a new MuPDF backend with better performance than ever, and the possibility to use MuPDF for PDF parsing. As a result, pdftk is no longer a hard requirement to open newer PDF documents; the only feature that still depends on it is automatic extraction of page titles. Even hyperlinks work without it.</p>

<h1><span class="date">2015-11-12</span>Some small fixes in 0.11.1</h1>
<p>This update just adds a few small fixes regarding hyperlinks and, most importantly, a compatibility fix for newer versions of one of the libraries relies on. This caused Impressive to break for Arch Linux users a few days ago, and so I'd rather make a new release version before the new library version gets into the real mainstream distributions.</p>

<h1><span class="date">2015-01-08</span>... and now for the Windows users: 0.11.0b</h1>
<p>Linux wasn't the only system affected from some growing pains in 0.11.0. I got two bug reports that the Windows version wasn't working either on some specific graphics hardware / driver combinations. To fix this, the way OpenGL functions are loaded has been rewritten and the problem seems to be gone now.</p>

<h1><span class="date">2014-12-23</span>Just a minor patch: 0.11.0a</h1>
<p>Only a couple of hours after the release of 0.11.0, users informed me that there were problems with some recent Linux distributions, namely &raquo;could not load SDL library&laquo; errors and crashes because no OSD font has been found. 0.11.0a should fix these issues. It's a source-only release that affects POSIX systems only; on Windows, this version behaves in all regards identical to 0.11.0. That's why there's no new Win32 .zip file for 0.11.0, as it isn't needed.</p>

<h1><span class="date">2014-12-21</span>Early christmas present: 0.11.0 is out</h1>
<p>Almost one year ago, I promised some larger changes to Impressive and, in fact, already implemented them. They sat in SVN for quite a while, and so far it seems that the people who tried them are quite happy with them, so it's time for a new release.</p>
<p>In 0.11.0, major parts of the program have been rewritten. The graphics code is all-new and is now based on OpenGL (ES) 2.0 instead of the ancient OpenGL 1.1. The result: It now runs on Raspberry Pi, and transitions are smoother on this small computer than they ever were on high-end PCs with the previous versions. The other big thing is that Impressive finally got fully customizable keyboard and mouse controls. Also, the blazingly fast <a href="http://www.mupdf.com/">MuPDF</a> is now supported as a PDF rendering backend.</p>
<p>The changes also bring some incompatibilities though. The most important one is that the <code>transition</code> PageProp no longer affects the transition <em>after</em> the specified page, but the transition <strong>to</strong> (or <em>before</em>) the specified page. The <code>-e</code>/<code>--noext</code> and <code>-R</code>/<code>--meshres</code> command-line options are now gone because they don't have any place in the new OpenGL 2.0 world; the <code>-e</code> option has been reused for input customization. Finally, some (rarely used) transitions have disappeared and some new ones are now available.</p>

<h1><span class="date">2014-05-02</span>A major bug fixed in 0.10.5</h1>
<p>As it turned out, 0.10.4 didn't only fix a ton of bugs, it also introduced one particularly nasty one: The file list feature stopped working. Since many people were using it, 0.10.5 fixes this specific issue. Other than that, it doesn't contain anything new; all the exciting stuff won't appear until 0.11.0.</p>

<h1><span class="date">2013-12-29</span>Surprise! 0.10.4 is alive and kicking!</h1>
<p>Yes, it has been another really, really large gap between the previous release and this one &ndash; so large, in fact, that some people already think the project <a href="http://alternativeto.net/software/impressive/">has been discontinued</a>. The reports of Impressive's death are greatly exaggerated though. In fact, I'm planning to release a new major version soon(-ish), and 0.10.4 is an intermediate step before I start with the bigger (and compatibility-breaking) changes.</p>
<p>0.10.4 has the longest changelog of any version to date, but it's mostly smaller changes. There are some bugfixes and compatibility improvements, and a couple of options that can be useful in certain situations, like Ignite-style quick talks or LaTeX slides with built-in presenter screens.</p>

<h1><span class="date">2010-10-17</span>0.10.3 is out &mdash; finally a new release after a long time!</h1>
<p>It has been over one and a half years since the last regular Impressive release. Development slowed down considerably since, but it didn't halt: A few changes were made in the Subversion repository. Most of these are bugfixes, stability fixes and compatibility fixes to make Impressive work with newer versions of the tools it relies on. There are a few new features, though these are just minor ones.</p>

<h1><span class="date">2008-02-03</span>0.10.2 is out, containing a few new features</h1>
<p>This release contains some internal fixes and improvements, but also a few user-visible new features. First, there's support for URL hyperlinks like web links and e-mail addresses. Second, Impressive now understands list files: These are text files that contain the actual names of the files to show, which can be useful for image slideshows. Third, there's are new &raquo;automatic overview&laquo; mode that hides PDF pages from Impressive's overview page based on whether they have a title or not. This makes use of the fact that some LaTeX packages for presentation slide generation don't emit PDF titles for pages that are part of multi-step slides (those who are revealed one step after another).<br />
Finally, there are three new PageProps: Using <code>keys</code>, alphanumeric keys can be bound to user-provided Python functions now, <code>comment</code> permanently shows a line of text on a page and <code>video</code> is a <strong>highly experimental</strong>(!!!) feature that plays a fullscreen video when a page is entered.</p>

<h1><span class="date">2007-11-27</span>a little interim release</h1>
<p>Over the last few weeks, it came to my attention that most Linux distributions switched to an incompatible <code>pdftoppm</code> implementation that breaks Impressive's page rendering. Since I don't have the time to turn my TODO list into a new release, I just updated a few spots to make it work on newer Linux distributions again. Users of the Win32 package don't need to (and, in fact, can't) update.</p>

<h1><span class="date">2007-09-09</span>0.10.1 supports PDF hyperlinks</h1>
<p>Apart from bugfixes and internal improvements, there are three important new features in this release:<br />
First, Impressive now contains a simple PDF parser, which (in conjuction with <code>pdftk</code>) can extract PDF hyperlinks and make them usable. This means that the navigation controls put into the files, e.g. by the <code>latex-beamer</code>, can finally be used.<br />
Second, there is a more generic command-line parser: Impressive now accepts an arbitrary number of image files, PDF files or image directories as inputs and concatenates them automatically.<br />
The third feature is a new (optional) "persistent" cache mode, which can be useful for large and frequently held presentations. It works just like the normal disk cache that was introduced in 0.9.0, but the cache files won't be deleted and can be used to speed up initialization the next time the presentation is shown. Please note that some caching-specific command line options have been changed in this process; please refer to the help screen or manual for details.</p>

<h1><span class="date">2007-06-02</span>0.10.0 comes with a huge load of new features</h1>
<p>Up to now, I took the time to describe each release's new features in detail, but 0.10.0 has so much of them that I will use a more compact presentation this time :)</p><ul class="text">
<li>Most importantly, Impressive now uses Xpdf's <code>pdftoppm</code> as the default PDF rendering backend. This not only solves numerous GhostScript problems &ndash; it's also faster and cuts the Windows version's size down to a half.</li>
<li>New keyboard shortcuts: [Home]/[End] for first/last page, [L] to return to the most recently displayed page, [I] and [O] for interactive toggle of the skip and &raquo;visible on overview page&laquo; flags, [R] to reset the timer</li>
<li>Unused alphanumeric or function keys can now be used for shortcuts to quickly access specific pages.</li>
<li>Impressive finally accepts lists of image file names on the command line. This makes JPEG/PNG slideshows much easier.</li>
<li>Transitions can now be turned off completely, either globally or on a per-page basis.</li>
<li>The <code>PagePeel</code> transition is not longer part of the default set of transitions. This means that now all default (automatically assigned) transitions are of the non-intrusive Crossfade and Wipe kind. Note that any info scripts which do a <code>AvailableTransitions.remove(PagePeel)</code> will not work any longer!</li>
<li>On the other hand, two new families of (rather intrusive) transitions have been added: <code>Slide</code> and <code>Squeeze</code>. Both come in variants for all four main directions, <code>Left</code>, <code>Right</code>, <code>Up</code> and <code>Down</code>.</li>
<li>The OSD layout is now configurable on the command line.</li>
<li>New page properties: <code>transtime</code> to set the transition duration for a single slide, <code>progress</code> to suppress display of the duration/progress indicator bar, <code>reset</code> to reset the timer after a page has been shown</li>
<li>Added the possibility to execute any Python code before and after specific pages.</li>
<li>Of course, there's a bunch of minor extensions and also bugfixes, most importantly the one for the supersample mode. (Which, on the other hand, is somewhat obsolete now that Xpdf is used for rendering :)</li>
</ul>

<h1><span class="date">2007-03-19</span>A bunch of new features in 0.9.4</h1>
<p>Besides numerous smaller bugfixes, the current release adds some new interesting features: If the target duration of the presentation is known, Impressive can display a progress bar at the lower edge of the screen. Luke Campagnola contributed code to adjust the gamma curve and the black level of the presentation. Impressive may now use a transparent PNG file as the mouse cursor image instead of the default one. And finally, the middle mouse button comes to life again: it toggles the overview mode now.</p>

<h1><span class="date">2007-02-26</span>Time for 0.9.3</h1>
<p>Today's new version fixes some annoying bugs and implements some minor under-the-hood polishing. But there's a new feature, too: The [T] key now shows a little time display in the upper-right corner of the screen. If [T] is pressed while the first page of the presentation is still shown, it will enable a special logging mode. In this mode, Impressive will dump a trace of all visited pages with some timing information to standard output (which can, of course, be redirected). This is a great tool for preparing presentations.</p>

<h1><span class="date">2007-02-17</span>How about some text? Go and get 0.9.2!</h1>
<p>The 0.9.2 release adds an on-screen text display for the overview window, indicating the page number and page title, if available. Furthermore, the page cache and overview screen can now be constrained to a user-defined range of consecutive pages. A third new feature is the the &raquo;poll&laquo; option: With this, Impressive periodically checks if the input file(s) have changed and reloads them if necessary. Finally, there's a fix for a bug that prevented the <code>-m</code> option from working.</p>

<h1><span class="date">2007-01-24</span>0.9.1 fixes some bugs</h1>
<p>Nothing special, just three more-or-less nasty bugs introduced in 0.9.0 were fixed: First, the 'whitening' mode didn't work on all graphics cards, clicking a mouse button in fade mode crashed the program and there were occasionally temp files left behind after exiting Impressive.</p>

<h1><span class="date">2007-01-07</span>0.9.0, the next big update</h1>
<p>One of the most frequently requested features is now finally implemented: Background rendering. This means that there's no longer need for watching that pesky progress bar on startup, as Impressive now starts much quicker and pre-renders all the pages calmly in the background. Also, the cache images are now by default stored on disk, which eliminates the memory problems of earlier versions.<br />
A few minor bugfixes and features have also been added. Most notably, the [B] and [W] keys now fade the screen to black and white, which is useful if you are going to use a blackboard or whiteboard in parallel to a Impressive presentation. A new page property in the info scripts can be used to make Impressive <code>skip</code> a page when going through the presentation. Finally, on Win32, the default fullscreen resolution is now taken from the current desktop resolution.</p>

<h1><span class="date">2006-09-28</span>A few new features in 0.8.3</h1>
<p>After a long time, I added some new features to Impressive again. The most useful one is that pages can now be removed from the overview screen via the new <code>overview</code> PageProps item. This comes in handy for presentations that contain slides that build up over multiple pages (i.e. the points are appearing one after another).<br />
The new aspect ratio option helps if the display aspect ratio differs from the selected screen resolution. A new (optional) transition has been contributed by Ronan Le Hy. Another change &raquo;behind the scenes&laquo; is OpenGL extension support to load textures with non-power-of-two dimensions. This helps saving graphics memory, but in case it causes trouble, it can be deactivated with the <code>-e</code> option.</p>

<h1><span class="date">2006-07-13</span>0.8.2, another minor update</h1>
<p>Again, there's a little bugfix release that fixes a crash on strangely sized pages. There are some new features, though: Keyboard navigation is now available in overview mode, and a new &raquo;rotate&laquo; option allows users with broken LaTeXes or GhostScripts to display presentations in correct orientation (try <code>-r 1</code> or <code>-r 3</code>). Please note that the &raquo;render&laquo; (<code>-r</code>) option had to be renamed to &raquo;output&laquo; (<code>-o</code>) due to the name collision.</p>

<h1><span class="date">2006-02-04</span>just a minor update: 0.8.1</h1>
<p>0.8.1 only adds features that will only help in certain situations: First, OpenGL error reporting is now a little bit more concise. And second, there's a &raquo;render&laquo; option that renders the presentation from PDF into a bunch of PNG files instead of displaying it. This feature was implemented due to an urgent request of a good friend. He's going to give a presentation on some college-supplied PC soon. Unfortunately, this PC does only have an ancient version of GhostScript, so he needed to render the files at home to circumvent the display flaws this old GS version produces.</p>

<h1><span class="date">2005-11-23</span>0.8.0: a lot of fixes and a brand-new zoom mode</h1>
<p>Recently, one specific feature was requested quite often: A zoom mode. The problem is that really nice zoom is very hard, if not impossible, to implement in a sane manner. 0.8.0 adds a somewhat experimental 2x zoom option that can be activated with the [Z] key. It is not fast, it is not very elegant, and it eats memory and CPU cycles as hell, but well ... it's there.<br />
For those who do not want to zoom into the pages, 0.8.0 has some additional features to offer as well: The command line option parser was severly broken, as was the image display mode and support for portrait-format pages. Some uncommon command line options now have capital letters as shortcuts, so if you have any scripts calling Impressive, don't forget to fix them. A new option has also been added to select which transition(s) to use if no other transition is specified in the page properties.</p>

<h1><span class="date">2005-10-24</span>Some quick additions again ...</h1>
<p>In the brand-new 0.7.2 release, there are some critical fixes for regression bugs found in 0.7.1. (Changing most of the event handling tends to break things ...) In addition, there are two new command-line options, <code>&ndash;a</code> and <code>&ndash;w</code>, that come in handy if you intend to use Impressive as an automatic slideshow tool.</p>

<h1><span class="date">2005-10-22</span>Usability improvements in 0.7.1</h1>
<p>Today, I implemented two suggestions from users. The first one affects highlight box handling: Boxes are no longer created and destroyed with the middle mouse button, but intuitively with the left button (drag to create a box) and the right button (delete a box). This is how I should have done that in the first place, I think :)<br />
The other suggestion was to add an option to specify the page that is shown right after initialization (start page, initial page, ... you name it). Now it's there: Try <code>&ndash;i</code> and note how even the pre-rendering process is adopted to reflect your wish.</p>

<h1><span class="date">2005-09-29</span>Impressive 0.7.0 &ndash; let there be sound!</h1>
<p>schrd, the guy who had most of the cool ideas that sum up to the Impressive experience, reported a bug yesterday, so I fixed it: If the user clicked at some areas in the overview page, Impressive would crash. Oops.<br />
However, this is not the reason for the leap in the version number. The 0.7 is due to two additional features that have been requested by schrd, too: First, a timeout PageProp can be used to create semi-automatic presentations, and second, there's <b>experimental</b> sound support!</p>

<h1><span class="date">2005-09-07</span>Bugfix No. 2: 0.6.3</h1>
<p>Yesterday night, a friend of mine informed me about another bug in 0.6.2: Some PDF files produced with &raquo;uncommon&laquo; pdfLaTeX packages had negative(!) object counts in them. This confused my oh-so-simple PDF page count parser, so that Impressive wouldn't play those files at all. This is (of course) fixed in the new release.</p>

<h1><span class="date">2005-09-06</span>0.6.2, the first bugfix release</h1>
<p>The worls seems to spin really fast these days. Only a couple of hours after releasing 0.6.1, some guy found the first (really annoying) bug: On Win32, filenames containing spaces didn't work. This is fixed in 0.6.2, and now I wait for the next bugs to come :)</p>

<h1><span class="date">2005-09-05</span>Initial official release: 0.6.1</h1>
<p>It's been more than a month that the nearly-done package and webpage waited for finally being released. Now I finally found some time to add another feature (the supersampling option) to 0.6, lifting it to 0.6.1. The activation of the sourceforge project was done in less then 24 hours, so here we go ...</p>

</div></body></html>
