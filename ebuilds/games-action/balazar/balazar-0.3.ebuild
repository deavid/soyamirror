# Copyright 1999-2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

inherit distutils

DESCRIPTION="Balazar is a 3D adventure and roleplaying game"
HOMEPAGE="http://home.gna.org/oomadness/en/balazar/"
SRC_URI="http://download.gna.org/balazar/Balazar-${PV}.tar.bz2"

LICENSE="GPL"
SLOT="0"
KEYWORDS="x86 ppc"
IUSE=""
S="${WORKDIR}/Balazar-${PV}"

DEPEND=">=dev-lang/python-2.3
	virtual/opengl
	media-libs/libsdl
	media-libs/glew
	media-libs/openal
	>=dev-python/pyopenal-0.1.6
	dev-python/pyogg
	dev-python/pyvorbis
	>=media-libs/cal3d-0.10
	dev-python/twisted
	media-libs/freetype
	
	dev-python/soya
	dev-python/tofu
	dev-python/cerealizer"
