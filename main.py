#!/usr/bin/env python3
"""
CLI Task Tracker - Main Entry Point

A productivity tracker that helps you organize activities, track progress, 
and reflect on how much time you dedicate to urgent vs. non-urgent tasks.
"""

from src.cli.cli_interface import CLI

if __name__ == "__main__":
    CLI().run()