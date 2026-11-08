# Maintainer: Noah <f643s@proton.me>
pkgname=evercland
pkgver=1.0.0
pkgrel=1
pkgdesc="a place in the dreams, in the terminal"
arch=('any')
url="https://github.com/f643s/evercland"
license=('GPL-3.0-or-later')
depends=('python')
source=("$pkgname-$pkgver.tar.gz::https://github.com/f643s/evercland/archive/v$pkgver.tar.gz")
# replace SKIP with the real checksum: updpkgsums
sha256sums=('SKIP')

package() {
  cd "$pkgname-$pkgver"
  make DESTDIR="$pkgdir" PREFIX=/usr install
  install -Dm644 COPYING "$pkgdir/usr/share/licenses/$pkgname/COPYING"
}
