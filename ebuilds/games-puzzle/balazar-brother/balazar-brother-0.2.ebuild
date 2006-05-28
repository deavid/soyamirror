# Copyright 1999-2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

inherit distutils

DESCRIPTION="A 3D puzzle game feturing the Balazar Brothers"
HOMEPAGE="http://home.gna.org/oomadness/en/balazar_brother/"
SRC_URI="http://download.gna.org/soya/BalazarBrother-${PV}.tar.bz2"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="x86 ppc"
IUSE=""
S="${WORKDIR}/BalazarBrother-${PV}"

DEPEND=">=dev-lang/python-2.4
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
