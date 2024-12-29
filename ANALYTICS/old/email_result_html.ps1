import-module  -Name 'Microsoft.PowerShell.Security' -RequiredVersion 3.0.0.0

# Start logging
$logFilePath = Join-Path -Path $PSScriptRoot -ChildPath "log\log.txt"
# $logFilePath = "C:\Users\Matsuno\Dropbox (CBS)\00_website\my-website\ANALYTICS\log\log.txt"
# $RlogFilePath = "C:\Users\Matsuno\Dropbox (CBS)\00_website\my-website\ANALYTICS\log\Rlog.txt"
# $pylogFilePath = "C:\Users\Matsuno\Dropbox (CBS)\00_website\my-website\ANALYTICS\log\pythonlog.txt"
Start-Transcript -Path $logFilePath -Force

# # Run the python script to update `raw_data.csv`
# Write-Output "Running Python script to retrieve data"
# # $pythonScriptPath = Join-Path -Path $PSScriptRoot -ChildPath "analytics.py"
# $pythonScriptPath = "C:\Users\Matsuno\Dropbox (CBS)\00_website\my-website\ANALYTICS\analytics.py"
# $pythonRun = & python $pythonScriptPath 
# # $pythonRun *>&1 | Tee-Object -FilePath $PSScriptRoot\log\pythonlog.txt
# $pythonRun *>&1 | Tee-Object -FilePath $pylogFilePath

# Write-Output "Running R script to generate summary"
# # $RScriptPath = Join-Path -Path $PSScriptRoot -ChildPath "make-summary.R"
# $RScriptPath = "C:\Users\Matsuno\Dropbox (CBS)\00_website\my-website\ANALYTICS\make-summary.R"
# $RRun = & "C:\Program Files\R\R-4.3.3\bin\x64\Rscript.exe" $RScriptPath 
# # $RRun *>&1 | Tee-Object -FilePath $PSScriptRoot\log\Rlog.txt
# $RRun *>&1 | Tee-Object -FilePath $RlogFilePath

Write-Output "Generating Email HTML"
# $bodyhtml = Get-Content $PSScriptRoot\df_html.txt -Raw
$bodyhtml = Get-Content "C:\Users\Matsuno\Dropbox (CBS)\00_website\my-website\ANALYTICS\df_html.txt" -Raw

Write-Output "Sending Email"
$userName = 'matsuno.shunsuke@gmail.com'
$password = 'snsk1732'
$AppPass = 'zzrl oqbl vifh owzz'
[SecureString]$securepassword = $AppPass | ConvertTo-SecureString -AsPlainText -Force 
$credential = New-Object System.Management.Automation.PSCredential -ArgumentList $username, $securepassword

$To = 'SMatsuno26@gsb.columbia.edu'
Send-MailMessage -SmtpServer smtp.gmail.com -Port 587 -UseSsl -From matsuno.shunsuke@gmail.com -To $To -Subject 'Google Analytics Summary' -BodyAsHTML -Body "$bodyhtml" -Credential $credential

Write-Output "Completed!"

# Stop logging
Stop-Transcript