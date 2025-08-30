@echo off
set PATH=%PATH%;C:\Program Files\Git\bin;C:\Program Files\Git\cmd
echo Setting up Flutter Web...
flutter config --enable-web
echo Getting Flutter dependencies...
flutter pub get
echo Flutter setup complete!
pause
