NAME    := ndctl
SRC_EXT := gz
SOURCE   = https://github.com/pmem/$(NAME)/archive/v$(VERSION).tar.$(SRC_EXT)

include packaging/Makefile_packaging.mk
