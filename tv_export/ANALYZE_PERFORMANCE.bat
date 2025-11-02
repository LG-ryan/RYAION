@echo off
chcp 65001 > nul
title RYAION v19.1 Deep Performance Analyzer

echo.
echo ================================================================
echo   RYAION v19.1 Deep Performance Analyzer
echo ================================================================
echo.
echo This program analyzes downloaded data in depth:
echo.
echo Analysis Modules:
echo   1. 4-Axis Score Decomposition (Trend/Momentum/Volatility/Context)
echo   2. Component Performance (FTD/TD/WVF actual accuracy)
echo   3. VIX Regime Effect Verification (HIGH/NORMAL/LOW)
echo   4. Stage Timing Analysis (Which stage is optimal?)
echo   5. False Signal Patterns (Why did it fail?)
echo   6. Optimal Pattern Discovery (ML-based pattern search)
echo   7. Threshold Optimization (Is 18 points optimal?)
echo   8. Comprehensive Improvement Recommendations (Weight adjustments, etc.)
echo.
echo Analysis Time: Approximately 1-3 minutes (depending on ticker count)
echo Browser Report: Opens automatically upon completion
echo.
echo ================================================================
pause

echo.
echo [1/1] Running deep analysis...
echo ================================================================
echo.
echo Please wait. Generating comprehensive insights...
echo.

python analyze_performance.py

if %errorlevel% neq 0 (
    echo.
    echo ================================================================
    echo ERROR: Analysis failed
    echo ================================================================
    echo.
    echo Solutions:
    echo   1. Run START_HERE.bat first to download data
    echo   2. Check if pandas and numpy are installed:
    echo      pip install pandas numpy
    echo   3. Verify Python 3.8+ is installed
    echo.
    pause
    exit
)

echo.
echo ================================================================
echo SUCCESS: Analysis complete
echo ================================================================
echo.
echo Report Location: reports folder
echo   - HTML report (visual dashboard)
echo   - JSON data (programmatic access)
echo.
echo Report Contents:
echo   - Actual contribution of each axis (Trend/Momentum/Volatility/Context)
echo   - FTD/TD/WVF accuracy verification
echo   - VIX regime threshold adjustment effects
echo   - Optimal entry points by Stage
echo   - Common patterns in losing trades
echo   - High win-rate optimal combinations
echo   - Data-driven improvement recommendations
echo.
pause

