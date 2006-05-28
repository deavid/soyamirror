# Copyright 1999-2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

inherit distutils

MY_P=${P/soya/Soya}
MY_PN=${PN/soya/Soya}
DESCRIPTION="A high-level 3D engine for Python, designed with games in mind"
HOMEPAGE="http://home.gna.org/oomadness/en/soya/"
SRC_URI="http://download.gna.org/soya/${MY_P}.tar.bz2"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="x86 ppc"
IUSE=""

DEPEND=">=dev-lang/python-2.4
	virtual/opengl
	>=dev-python/pyrex-0.9.3
	media-libs/libsdl
	>=media-libs/cal3d-0.10
	>=media-libs/freetype-2
	media-fonts/freefonts
	dev-python/imaging
	media-libs/glew
	media-libs/openal
	>=dev-python/pyopenal-0.1.6
	dev-python/pysdl_mixer"

S=${WORKDIR}/${MY_P}
