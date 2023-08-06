# generate readme file

sudo apt install pandoc

pandoc -f markdown -t rst -o README.rst README.md
