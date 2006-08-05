# Copyright 1999-2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

inherit distutils

DESCRIPTION="A 3D puzzle game feturing the Balazar Brothers"
HOMEPAGE="http://home.gna.org/oomadness/en/balazar_brother/"
SRC_URI="http://download.gna.org/balazar/BalazarBrothers-0.4rc1.tar.bz2"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="x86 ppc"
IUSE=""
S="${WORKDIR}/BalazarBrothers-0.4rc1"

DEPEND="media-libs/openal
	>=dev-python/pyopenal-0.1.6
	dev-python/pyogg
	dev-python/pyvorbis
	>=dev-python/soya-0.11.2
	>=dev-python/tofu-0.5
	>=dev-python/cerealizer-0.4"

src_compile() {
        sed  s/models/shapes/ setup.py > setup2.py
	mv setup2.py setup.py
	distutils_src_compile
}

