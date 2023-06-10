$version = Invoke-Expression ('.\venv\Scripts\python.exe -c "from main import __version__;print(__version__)"')

New-Item -ErrorAction Ignore -ItemType Directory -Path release
Set-Location .\release
Invoke-Expression ("..\venv\Scripts\pyinstaller.exe ..\main.spec --upx-dir=H:\python\upx")

Write-Output  "build version: $version"

# crate release dir 
$releasedir = "eimg_server_" + $version +"_windows"
New-Item -ItemType Directory -Path ($releasedir + "\data")

# move config file
Copy-Item ..\config.example.ini .\$releasedir\config.ini

# rename main.exe
$newname = "eimg_server.exe"
Move-Item .\dist\main.exe .\$newname

# move exe to run
Copy-Item .\$newname ..\eimg_server.exe

# pack release dir
Move-Item .\$newname .\$releasedir
Compress-Archive -Force -Path .\$releasedir -DestinationPath .\$releasedir.zip

# clean up
Remove-Item -Recurse -Force .\$releasedir
Remove-Item -Recurse -Force .\dist