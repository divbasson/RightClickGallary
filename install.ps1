# Define paths
$localAppData = [Environment]::GetFolderPath("LocalApplicationData")
$folderPath = Join-Path $localAppData "OpenImageGallery"
$pythonPath = [Environment]::GetEnvironmentVariable('PYTHONPATH')
$requirementsFile = Join-Path $folderPath "requirements.txt"

# Create folder if it doesn't exist
if (-not (Test-Path $folderPath)) {
    New-Item -Path $folderPath -ItemType Directory
}

# Copy other files to the folder
$filesToCopy = @("image_gallery.py", "icon.ico", "requirements.txt")
foreach ($file in $filesToCopy) {
    Copy-Item ".\$file" -Destination $folderPath -ErrorAction Stop
}

# Check environment variables
$pythonPath = [Environment]::GetEnvironmentVariable('PYTHONPATH')

# Get the full path of pythonw.exe
try {
    $pythonwPath = (Get-Command pythonw).Source
} catch {
    Write-Host "pythonw.exe not found in PATH"
    exit 1
}

# Check if Python is set
if ($pythonPath) {
    # Install requirements if requirements.txt exists
    if (Test-Path $requirementsFile) {
        try {
            python -m pip install --upgrade pip --user
            python -m pip install -r $requirementsFile -v --user
        } catch {
            Write-Host "Error during pip installation: $_"
            exit 1
        }
    } else {
        Write-Host "requirements.txt not found in $folderPath"
        exit 1
    }
}

# Get the full path for image_gallery.py
$imageGalleryPath = Join-Path $folderPath "image_gallery.py"

# Generate registry script content
$regContent = @"
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\directory\shell\OpenImageGallery]
@="Open Image Gallery"
"Icon"="$($folderPath -replace '\\', '\\\\')\\icon.ico"

[HKEY_CLASSES_ROOT\directory\shell\OpenImageGallery\command]
@="`\"$($pythonwPath -replace '\\', '\\\\')`\" `\"$($imageGalleryPath -replace '\\', '\\\\')`\" `\"%1`\""
"@

# Write and execute the registry script
try {
    $regFilePath = Join-Path $folderPath "Set-Context.reg"
    Set-Content -Path $regFilePath -Value $regContent
    Start-Process "regedit.exe" -ArgumentList "/s $regFilePath" -Wait
} catch {
    Write-Host "Error executing Set-Context.reg: $_"
    exit 1
}
