# Maintainer: f643s <f643s@proton.me>
pkgname=evercland
pkgver=1.0.0
pkgrel=1
pkgdesc="Animated terminal postcard: a pond, mountains and forest through the seasons"
arch=('any')
url="https://github.com/f643s/evercland"
license=('GPL-3.0-or-later')
depends=('python')
source=("$pkgname-$pkgver.tar.gz::https://github.com/f643s/evercland/releases/download/v$pkgver/$pkgname-$pkgver.tar.gz")
sha256sums=('c201bfe8253e9bdbc4108a521f4d6eec6abdf69b0d16b09c8b30d21e67693807')

package() {
  cd "$pkgname-$pkgver"
  make DESTDIR="$pkgdir" PREFIX=/usr install
  install -Dm644 COPYING "$pkgdir/usr/share/licenses/$pkgname/COPYING"
}
