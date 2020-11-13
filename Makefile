.PHONY: clean
dist/g1klogger.exe: g1klogger.py
	pyinstaller g1klogger.spec

clean:
	rm -rf dist build