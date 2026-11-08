PREFIX ?= /usr/local

install:
	install -Dm755 evercland $(DESTDIR)$(PREFIX)/bin/evercland
	install -d $(DESTDIR)$(PREFIX)/lib/evercland
	cp -r src/evercland $(DESTDIR)$(PREFIX)/lib/evercland/
	find $(DESTDIR)$(PREFIX)/lib/evercland -name __pycache__ -prune -exec rm -rf {} +

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/evercland
	rm -rf $(DESTDIR)$(PREFIX)/lib/evercland

.PHONY: install uninstall
