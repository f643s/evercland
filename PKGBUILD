# Maintainer: you <you@example.com>
pkgname=evercland
pkgver=1.0.1
pkgrel=1
pkgdesc="Terminal landscape generator with day/night and four seasons"
arch=('any')
license=('GPLv3-or-later')   # change this to whatever you actually use
depends=('python')
source=()

# Run `makepkg -si` from the root of the repo, it packages the files next to it.
# makepkg reuses a package it already built, so after you change any files either
# bump pkgver/pkgrel above or run `makepkg -fsi` (-f forces a rebuild).
package() {
  cd "$startdir"
  make DESTDIR="$pkgdir" PREFIX=/usr install
}
