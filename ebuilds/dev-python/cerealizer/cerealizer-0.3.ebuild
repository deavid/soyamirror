# Copyright 1999-2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

inherit distutils

DESCRIPTION="A secure pickle-like module"
HOMEPAGE="http://home.gna.org/oomadness/en/cerealizer/"
SRC_URI="http://download.gna.org/soya/Cerealizer-${PV}.tar.bz2"

LICENSE="GPL"
SLOT="0"
KEYWORDS="x86 ppc"
IUSE=""
S="${WORKDIR}/Cerealizer-${PV}"

DEPEND=">=dev-lang/python-2.4"
