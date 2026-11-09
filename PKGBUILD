# Maintainer: you <you@example.com>
pkgname=evercland
pkgver=1.0.0
pkgrel=1
pkgdesc="Terminal landscape generator with day/night and four seasons"
arch=('any')
license=('GPLv3-or-later')   # change this to whatever you actually use
depends=('python')
source=()

# run `makepkg -si` from the root of the repo, it packages the files next to it
package() {
  cd "$startdir"
  make DESTDIR="$pkgdir" PREFIX=/usr install
}
