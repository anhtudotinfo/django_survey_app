# QR Code Feature Guide

## Overview
The survey system now includes QR code generation functionality, allowing users to easily share and access surveys by scanning QR codes.

## Features

### 1. QR Code Generation
- Each survey automatically has a unique QR code linked to its URL
- QR codes are dynamically generated using the `qrcode` library
- High-quality PNG format with error correction

### 2. Access Methods

#### Via Survey Card
On the homepage, each survey card displays action buttons including:
- **Purple button**: Create new response
- **Indigo button (NEW)**: View QR code
- **Blue button** (staff only): Edit survey
- **Green button** (staff only): View summary
- **Red button** (staff only): Delete survey

#### Via Direct URL
Access QR code page directly:
```
/surveys/qr/<survey-slug>/
```

### 3. QR Code Page Features

The QR code page (`qr_code.html`) includes:

#### Display
- Large, scannable QR code image
- Survey name and description
- Full survey URL

#### Actions
1. **Copy URL**: Click the copy button to copy survey link to clipboard
2. **Download QR Code**: Download QR code as PNG file
3. **View Survey**: Go directly to survey details
4. **Back to List**: Return to survey list

#### Instructions
- Step-by-step guide for scanning QR codes
- Mobile-friendly interface
- Print-ready QR code

## Technical Implementation

### Model Methods (Survey)

```python
def get_absolute_url(self):
    """Get the full URL for this survey."""
    return reverse('djf_surveys:survey_detail', kwargs={'slug': self.slug})

def generate_qr_code(self, request=None):
    """Generate QR code for survey URL. Returns base64 encoded image."""
    # Generates QR code with proper error correction
    # Returns data URI for direct embedding in HTML

def get_qr_download_url(self):
    """Get URL to download QR code."""
    return reverse('djf_surveys:survey_qr_download', kwargs={'slug': self.slug})
```

### Views

#### `survey_qr_code(request, slug)`
- Displays QR code page with embedded image
- Provides full survey URL
- Shows download and navigation options

#### `survey_qr_download(request, slug)`
- Generates downloadable PNG file
- Filename format: `survey_<slug>_qr.png`
- Optimized for printing (300 DPI equivalent)

### URLs
```python
path('qr/<str:slug>/', views.survey_qr_code, name='survey_qr_code'),
path('qr/<str:slug>/download/', views.survey_qr_download, name='survey_qr_download'),
```

## Usage Examples

### 1. Share Survey via QR Code
1. Navigate to survey list
2. Click the QR code button (indigo) on any survey card
3. Share the displayed QR code via:
   - Screenshot
   - Download PNG file
   - Print physical copy
   - Display on screen for scanning

### 2. Download QR Code for Printing
1. Open QR code page
2. Click "Download QR Code" button
3. Open downloaded PNG file
4. Print on paper or materials
5. Distribute to target audience

### 3. Embed in Presentations
1. Download QR code PNG
2. Insert image into PowerPoint/Google Slides
3. Present during meetings/conferences
4. Attendees can scan to access survey instantly

## QR Code Specifications

### Technical Details
- **Format**: PNG
- **Error Correction**: Level L (7% recovery)
- **Box Size**: 10 pixels per module
- **Border**: 4 modules (quiet zone)
- **Colors**: Black on white background

### Size Recommendations
- **Digital Display**: Original size (typically 290x290px)
- **Print (A4 paper)**: 5-10 cm width
- **Poster/Banner**: 15-30 cm width
- **Business Card**: 2-3 cm width

### Scanning Distance
- Small (2cm): 10-20cm away
- Medium (5cm): 25-50cm away
- Large (10cm): 50-100cm away
- Poster (20cm+): 100-200cm away

## Best Practices

### Design
1. Ensure adequate white space around QR code
2. Maintain high contrast (black on white recommended)
3. Test scanning before mass distribution
4. Include text URL as fallback

### Distribution
1. **Physical**: Print on quality paper, avoid glossy surfaces
2. **Digital**: Use PNG format, avoid compression
3. **Display**: Ensure good lighting, no glare
4. **Mobile**: Test on various devices before deployment

### Accessibility
1. Always provide alternative text URL
2. Include instructions for first-time users
3. Test with multiple QR code reader apps
4. Consider audience's technical proficiency

## Troubleshooting

### QR Code Won't Scan
- **Issue**: Poor lighting or screen glare
  - **Solution**: Adjust angle, increase brightness
  
- **Issue**: Code too small
  - **Solution**: Download and zoom in, or print larger
  
- **Issue**: Damaged or distorted image
  - **Solution**: Re-download QR code
  
- **Issue**: Camera focus problems
  - **Solution**: Hold steady, move closer/farther

### Download Issues
- **Issue**: PNG file not downloading
  - **Solution**: Check browser settings, allow downloads
  
- **Issue**: Incorrect filename
  - **Solution**: Rename after download using format: `survey_<name>_qr.png`

## Homepage Redesign

### New Features

#### Hero Section
- Gradient background (purple theme)
- Clear call-to-action for staff users
- Responsive typography

#### Stats Dashboard (Staff Only)
- Total surveys count
- Active users indicator
- Response statistics
- Color-coded cards with gradients

#### Feature Highlights (Public Users)
- QR Code Access feature
- Easy to Use interface
- Security & Privacy assurance
- Icon-based visual design

#### Survey Grid
- 3-column layout on desktop
- Card hover effects with elevation
- Improved spacing and typography
- Better visual hierarchy

### Styling Enhancements
- Custom gradient backgrounds
- Smooth transitions and animations
- Consistent color palette
- Modern card designs
- Responsive layout for all devices

## Security Considerations

### QR Code Safety
- QR codes link directly to survey pages
- No sensitive data encoded in QR code
- Same permission checks as direct URL access
- Secure HTTPS URLs (in production)

### Privacy
- Survey responses remain private according to settings
- QR codes are publicly accessible but don't expose data
- Staff-only features require authentication

## Future Enhancements

### Potential Features
1. Custom QR code colors/branding
2. Logo embedding in QR center
3. Batch QR code generation
4. Analytics: scan tracking
5. Dynamic QR codes with expiration
6. Short URL integration

## Support

For issues or questions:
1. Check this documentation
2. Review Django admin logs
3. Test in development environment
4. Contact system administrator

## Dependencies

- `qrcode[pil]==8.2`: QR code generation library
- `Pillow==10.2.0`: Image processing (already installed)
- Django URL routing
- Base64 encoding for inline images

## Version History

- **v1.0** (2025-01-02): Initial QR code implementation
  - Basic QR generation
  - Download functionality
  - QR code page template
  - Homepage redesign
  - Survey card integration
