pdoc3 --output-dir=.\docs --html --template-dir .\templates\ --force .\d2read\  
xcopy /s .\docs\d2read\* .\docs\ /y
git add .\docs\*
git commit -m "documentation update"
git push