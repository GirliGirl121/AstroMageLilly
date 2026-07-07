#!/bin/bash
# MagiJournal Launcher — always running for Gigi ❤️
cd /home/ladylefey/AstroMage/MagiJournal

# Start MagiJournal in background
python3 main.py &

# Wait for MagiJournal to finish loading, then start KDE Connect
sleep 5
kdeconnectd
