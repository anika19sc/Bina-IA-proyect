$ErrorActionPreference = "Stop"

Write-Host "Renaming existing frontend directory..."
Move-Item -Path frontend -Destination frontend_config

Write-Host "Generating Angular application..."
# Using --skip-install to speed it up, assuming Docker will handle install
# Using --defaults to avoid prompts
npx -y @angular/cli@17 new bina-legal --directory ./frontend --style=scss --routing=true --skip-git --skip-install --defaults

Write-Host "Restoring configuration files..."
Copy-Item -Path frontend_config/* -Destination frontend/ -Recurse -Force

Write-Host "Cleaning up..."
Remove-Item -Path frontend_config -Recurse -Force

Write-Host "Frontend generation complete."
