# Copyright 1999-2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

inherit distutils

DESCRIPTION="A 3D puzzle game feturing the Balazar Brothers"
HOMEPAGE="http://home.gna.org/oomadness/en/balazar_brother/"
SRC_URI="http://download.gna.org/balazar/BalazarBrothers-${PV}.tar.bz2"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="x86 ppc"
IUSE=""
S="${WORKDIR}/BalazarBrother-${PV}"

DEPEND="media-libs/openal
	>=dev-python/pyopenal-0.1.6
	dev-python/pyogg
	dev-python/pyvorbis
	dev-python/soya
	dev-python/tofu
	dev-python/cerealizer"
