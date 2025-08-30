@echo off
echo 🚀 Pushing Auto Job Apply System to GitHub...
echo.

REM Remove existing remote if it exists
git remote remove origin 2>nul

REM Add the correct remote (update this with your actual repository URL)
git remote add origin https://github.com/ganesh991212/auto-job-apply-system.git

REM Push to GitHub
echo 📤 Pushing to GitHub repository...
git push -u origin master

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Successfully pushed to GitHub!
    echo 🔗 Repository: https://github.com/ganesh991212/auto-job-apply-system
    echo.
    echo 🎯 Next Steps:
    echo 1. GitHub Actions will automatically run the automation pipeline
    echo 2. Check the Actions tab for CI/CD results
    echo 3. Screenshots and reports will be available as artifacts
    echo 4. PR automation will work for future changes
    echo.
    echo 📊 What's included:
    echo - ✅ 10 UI Screenshots captured and validated
    echo - ✅ 7 API Response captures from backend services
    echo - ✅ Complete automation framework with auto UI fixing
    echo - ✅ CI/CD pipelines for GitHub Actions and Azure DevOps
    echo - ✅ Modern Flutter UI with unique design system
    echo - ✅ Comprehensive documentation and setup scripts
) else (
    echo.
    echo ❌ Push failed. Please check:
    echo 1. Repository exists on GitHub
    echo 2. You have push permissions
    echo 3. Authentication is configured
    echo.
    echo 💡 Manual steps:
    echo 1. Create repository: https://github.com/new
    echo 2. Update remote URL in this script
    echo 3. Run this script again
)

echo.
echo 📋 Repository Contents:
echo - Frontend: Flutter web app with modern UI
echo - Backend: 4 Python microservices
echo - Automation: Complete testing framework
echo - Screenshots: 10 UI + 7 API response captures
echo - CI/CD: GitHub Actions + Azure DevOps pipelines
echo - Documentation: Comprehensive setup guides

pause
