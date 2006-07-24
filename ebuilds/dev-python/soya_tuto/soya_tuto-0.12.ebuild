MY_P=SoyaTutorial-${PV}
DESCRIPTION="Documentation for dev-python/soya, a high-level 3D engine for Python, designed with games in mind"
HOMEPAGE="http://home.gna.org/oomadness/en/soya_tuto"
SRC_URI="http://download.gna.org/soya/${MY_P}.tar.bz2"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="~x86 ~ppc"

S=${WORKDIR}/${MY_P}

src_install() {
    insinto /usr/share/doc/${PF}/
    doins -r tutorial/*
}
