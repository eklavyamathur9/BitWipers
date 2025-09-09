# Adding Screenshots to BitWipers Website

## Quick Guide

### Step 1: Run the BitWipers GUI
```bash
python -m src.bitwipers.main --gui
```

### Step 2: Take Screenshots

#### Windows Screenshot Methods:
- **Win + Shift + S**: Opens Snipping Tool (recommended)
- **Alt + PrtScn**: Captures active window only
- **Win + PrtScn**: Captures full screen (saves to Pictures/Screenshots)

### Step 3: Save Screenshots

Save your screenshots in this folder (`website/images/`) with these exact filenames:

| Filename | Description | Recommended Size |
|----------|-------------|------------------|
| `main-interface.png` | Main dashboard/home screen | 1200x800px |
| `device-selection.png` | Device selection/detection screen | 600x400px |
| `wiping-progress.png` | Progress bar during wiping operation | 600x400px |
| `certificate-preview.png` | Certificate generation/preview screen | 600x400px |
| `settings.png` | Settings or configuration panel | 600x400px |

### Step 4: Optimize Images (Optional)

For better website performance, consider:
1. Resize images to recommended dimensions
2. Compress using tools like:
   - [TinyPNG](https://tinypng.com/)
   - [Squoosh](https://squoosh.app/)
   - Windows Photos app (Edit & Create → Resize)

### Step 5: Verify

1. Refresh the website in your browser
2. Check that all screenshots appear correctly
3. Ensure they're not too large (ideally < 500KB each)

## Tips for Good Screenshots

- ✅ **Clean Interface**: Close unnecessary windows/notifications
- ✅ **Consistent Theme**: Use the same Windows theme for all screenshots
- ✅ **Show Key Features**: Capture the most important UI elements
- ✅ **High Quality**: Use PNG format for sharp text
- ✅ **Proper Cropping**: Remove unnecessary whitespace

## Troubleshooting

If screenshots don't appear:
1. Check file names match exactly (case-sensitive)
2. Ensure files are in `.png` format
3. Clear browser cache (Ctrl + F5)
4. Check browser console for errors (F12)

## Alternative: Using Placeholder Images

If you can't take screenshots immediately, the website will show purple gradient placeholders with instructions.

---

Need help? Check the main README or open an issue on GitHub.
