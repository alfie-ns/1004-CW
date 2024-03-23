@echo off

REM Initialize a new repository

cd ..
git init
git remote add origin https://github.com/alfie-ns/dr.-fit-api
git add -A
git commit -m "Initial commit"
git branch -m master main
git push -u origin main


echo "# dr.-fit-api" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/alfie-ns/dr.-fit-api.git
git push -u origin main