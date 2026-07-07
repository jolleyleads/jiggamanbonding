Copy-Item '.\backups\elite-ui-20260707-031606\public_site.html' '.\templates\public_site.html' -Force
Copy-Item '.\backups\elite-ui-20260707-031606\style.css' '.\static\css\style.css' -Force
git add .
git commit -m 'Rollback elite UI'
git push
