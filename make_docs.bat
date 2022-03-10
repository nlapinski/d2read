pdoc3 --output-dir=.\docs\ --html --template-dir .\templates\ --force .\d2mem\  
git add .\docs\*
git commit -m "documentation update"
git push