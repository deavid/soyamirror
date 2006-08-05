# Copyright 1999-2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

inherit distutils

DESCRIPTION="Balazar is a 3D adventure and roleplaying game"
HOMEPAGE="http://home.gna.org/oomadness/en/balazar/"
SRC_URI="http://download.gna.org/balazar/Balazar-0.3.3rc1.tar.bz2"

LICENSE="GPL"
SLOT="0"
KEYWORDS="x86 ppc"
IUSE=""
S="${WORKDIR}/Balazar-0.3.3rc1"

DEPEND="media-libs/openal
	>=dev-python/pyopenal-0.1.6
	dev-python/pyogg
	dev-python/pyvorbis
	dev-python/soya
	dev-python/tofu
	dev-python/cerealizer"
