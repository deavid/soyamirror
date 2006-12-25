inherit distutils

DESCRIPTION="A high-level 3D engine for Python, designed with games in mind"
HOMEPAGE="http://home.gna.org/oomadness/en/soya/"
SRC_URI="http://download.gna.org/soya/Soya-0.13rc1.tar.bz2"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="~x86 ~ppc"
IUSE="examples openal sdlmixer"

DEPEND=">=dev-lang/python-2.4
    virtual/opengl
    dev-games/ode 
    media-libs/libsdl
    >=media-libs/cal3d-0.10
    >=media-libs/freetype-2
    dev-python/imaging
    media-libs/glew
	media-fonts/freefonts
    openal? (media-libs/openal
            >=dev-python/pyopenal-0.1.6)
    sdlmixer? (dev-python/pysdl_mixer)
    examples? (dev-python/soya_tuto)"

S=${WORKDIR}/Soya-0.13rc1/
