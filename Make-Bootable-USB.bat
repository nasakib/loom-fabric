@echo off
title ClothOS Live Bootable Flashdrive Creator
color 0E
cls
echo ================================================================================
echo    CLOTHOS LIVE BOOTABLE FLASHDRIVE ^& INSTALLER CREATOR
echo    UEFI / BIOS Hybrid ^| x86_64 ^| RISC-V 64-bit ^| Multi-User Live Rootfs
echo ================================================================================
echo.
echo [*] Synthesizing ClothOS Live Bootable Image (clothos-live-usb.img ^& .iso)...
echo.

call "%~dp0\.venv\Scripts\python.exe" -m loom.clothos.usb_installer
echo.
echo ================================================================================
echo  HOW TO BURN AND BOOT ON YOUR COMPUTER:
echo ================================================================================
echo  1. Open Rufus (https://rufus.ie) or Balena Etcher.
echo  2. Select your USB Flashdrive.
echo  3. Select Boot File: "%~dp0deliverables\bootable_images\clothos-sovereign-live-installer.iso"
echo  4. Click "START" to flash.
echo  5. Plug the USB into your PC, reboot, and press F12 (or Del / F2) to boot!
echo ================================================================================
echo.
pause
