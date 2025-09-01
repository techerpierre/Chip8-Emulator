PYINSTALLER = pyinstaller
SRC = src/main.py
DIST = dist
BUILD = build
ASSETS = assets
APP_NAME = chip8-emu
DEV_ROM_PATH = assets/roms/test.ch8

ifeq ($(OS),Windows_NT)
	RM = rmdir /s /q
	COPY_DATA = "$(ASSETS);$(ASSETS)"
	ICON = assets/icon/C8-Logo.ico
else
	RM = rm -rf
	COPY_DATA = "$(ASSETS):$(ASSETS)"
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		ICON = assets/icon/C8-Logo-x1024.png
	endif
	ifeq ($(UNAME_S),Darwin)
		ICON =
	endif
endif

ifeq ($(ICON),)
		PY_CMD = $(PYINSTALLER) --name $(APP_NAME) --noconsole --add-data $(COPY_DATA) $(SRC)
	else
		PY_CMD = $(PYINSTALLER) --name $(APP_NAME) --noconsole --add-data $(COPY_DATA) --icon=$(ICON) $(SRC)
	endif

build: build_emu clean

build_emu:
	$(PY_CMD)
clean:
	$(RM) $(BUILD)

dev:
	python src/main.py $(DEV_ROM_PATH)

PROGRAM_SRC = /
PROGRAM_OUT = /

compile:
	python ./scripts/compiler.py $(PROGRAM_SRC) --outpath $(PROGRAM_OUT)