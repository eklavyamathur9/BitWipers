# BitWipers Website

A modern, responsive landing page for the BitWipers secure data wiping platform.

## Features

- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Modern UI**: Clean, professional design with smooth animations
- **GitHub Integration**: Multiple CTAs that redirect users to the GitHub repository
- **Interactive Elements**: Scroll animations, hover effects, and smooth navigation
- **Performance Optimized**: Lightweight with minimal dependencies

## Quick Start

### Option 1: Open Directly
Simply open the `index.html` file in your web browser:
```bash
# Navigate to the website directory
cd website

# Open in default browser (Windows)
start index.html

# Open in default browser (Mac)
open index.html

# Open in default browser (Linux)
xdg-open index.html
```

### Option 2: Serve with Python
For a better development experience with proper MIME types:
```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```
Then navigate to `http://localhost:8000` in your browser.

### Option 3: Use Live Server
If you're using VS Code, install the "Live Server" extension and right-click on `index.html` to select "Open with Live Server".

## Structure

```
website/
├── index.html      # Main HTML file
├── styles.css      # Styling and animations
├── script.js       # Interactive features
└── README.md       # This file
```

## Customization

### Update GitHub Links
The website currently uses placeholder GitHub URLs. Update all instances of `https://github.com/your-org/BitWipers` in `index.html` with your actual GitHub repository URL.

### Modify Content
- **Hero Section**: Update the main headline and description in the hero section
- **Features**: Add or modify features in the features grid
- **Stats**: Update the statistics with current data
- **Impact**: Customize the impact section with relevant information

### Styling Changes
All styles are contained in `styles.css`. Key CSS variables are defined at the top of the file:
```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #0f172a;
    --accent-color: #10b981;
    /* ... more variables ... */
}
```

## Deployment Options

### GitHub Pages
1. Push the website folder to your GitHub repository
2. Go to Settings → Pages
3. Select source branch and `/website` folder
4. Your site will be available at `https://[username].github.io/BitWipers/`

### Netlify
1. Drag and drop the website folder to [Netlify Drop](https://app.netlify.com/drop)
2. Get an instant URL for your site

### Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the website directory
3. Follow the prompts to deploy

### Traditional Hosting
Simply upload all files to your web server's public directory.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Dependencies

The website uses the following external resources via CDN:
- **Google Fonts**: Inter font family
- **Font Awesome**: Icons (v6.4.0)

No build process or npm installation required!

## Performance Tips

1. **Optimize Images**: If adding images, compress them using tools like TinyPNG
2. **Minify Files**: For production, consider minifying CSS and JS files
3. **Enable Caching**: Configure your server to cache static assets
4. **Use CDN**: Consider serving from a CDN for global availability

## License

This website is part of the BitWipers project and follows the same MIT License.

## Support

For issues or questions about the website, please open an issue on the [GitHub repository](https://github.com/your-org/BitWipers/issues).

---

Built with ❤️ for showcasing the BitWipers platform
