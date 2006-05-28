# Copyright 1999-2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

inherit distutils

DESCRIPTION="A practical high-level network game engine"
HOMEPAGE="http://home.gna.org/oomadness/en/tofu/"
SRC_URI="http://download.gna.org/soya/Tofu-${PV}.tar.bz2"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="x86 ppc"
IUSE=""
S="${WORKDIR}/Tofu-${PV}"

DEPEND=">=dev-lang/python-2.3
	>=dev-python/twisted-1.3"
