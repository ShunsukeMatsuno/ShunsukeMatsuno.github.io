@ECHO OFF

python "C:\Users\Matsuno\Dropbox (CBS)\00_website\my-website\ANALYTICS\analytics.py"

Rscript "C:\Users\Matsuno\Dropbox (CBS)\00_website\my-website\ANALYTICS\make-summary.R"

PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& 'C:\Users\Matsuno\Dropbox (CBS)\00_website\my-website\ANALYTICS\email_result_html.ps1'"