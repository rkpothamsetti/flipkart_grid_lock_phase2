from PIL import Image, ImageEnhance, ImageStat

def check_image_degradation(image: Image.Image) -> dict:
    """
    Checks if the image has low-light degradation or noise/blur metrics.
    """
    # Convert to grayscale to evaluate brightness
    gray_img = image.convert('L')
    stat = ImageStat.Stat(gray_img)
    avg_brightness = stat.mean[0]
    
    # Simple contrast stat
    std_dev = stat.stddev[0]
    
    low_light = avg_brightness < 80.0
    blurry_or_noisy = std_dev < 30.0
    
    return {
        "avg_brightness": avg_brightness,
        "std_dev": std_dev,
        "needs_low_light_correction": low_light,
        "needs_deblur_denoise": blurry_or_noisy
    }

def enhance_image(image: Image.Image) -> tuple[Image.Image, dict]:
    """
    Simulates Zero-DCE and Restormer image restoration.
    """
    metrics = check_image_degradation(image)
    enhanced = image.copy()
    
    actions_taken = []
    
    if metrics["needs_low_light_correction"]:
        # Zero-DCE brightness enhancement simulation
        enhancer = ImageEnhance.Brightness(enhanced)
        enhanced = enhancer.enhance(1.6)
        # Re-enhance contrast slightly to keep it sharp
        contrast_enhancer = ImageEnhance.Contrast(enhanced)
        enhanced = contrast_enhancer.enhance(1.2)
        actions_taken.append("Zero-DCE Low-light Correction (+60% Brightness)")
        
    if metrics["needs_deblur_denoise"]:
        # Restormer sharpener / denoise simulation
        sharpener = ImageEnhance.Sharpness(enhanced)
        enhanced = sharpener.enhance(1.5)
        actions_taken.append("Restormer Deblurring & Denoising")
        
    if not actions_taken:
        actions_taken.append("No enhancement needed (optimal light and sharpness)")
        
    return enhanced, {
        "original_metrics": metrics,
        "actions": actions_taken
    }
