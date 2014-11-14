CFLAGS = -g -I$(topdir)/tests/unittest/include

tests = meminit

all: banner $(tests)
	for t in $(tests); do \
	./$$t \
	&& printf "      [+] $$t passed\n" \
	|| printf "      [-] $$t failed\n" ; \
	done
banner:
	printf "    Running memory subsystem unit tests...\n"

%: %.c
	$(CC) $(CFLAGS) -o $@ $<

meminit: meminit.c ../init.c
