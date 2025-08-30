# Add Git to PATH for this session
$env:PATH = $env:PATH + ";C:\Program Files\Git\bin;C:\Program Files\Git\cmd"

Write-Host "Setting up Flutter Web..." -ForegroundColor Green

# Enable web support
flutter config --enable-web

Write-Host "Getting Flutter dependencies..." -ForegroundColor Green

# Get dependencies
flutter pub get

Write-Host "Flutter setup complete!" -ForegroundColor Green
