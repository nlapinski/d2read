python.exe .\py2md.py --sourcedir .\d2mem\ --docfile d2mem.md --projectname d2mem --codelinks
python -m doc2md -a -t 'd2mem' 'd2mem' > d2mem.alt.md
git add .\d2mem.alt.md
git add .\d2mem.md
git commit -m "documentation update"
git push