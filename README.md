# Email Collector 

The idea of this module is to collect emails and do things with that information.

## INSTALLATION

The module needs Tesseract OCR to parse JPEG images from tickets so you should first install it in your computer, 
along with pytesseract from pip (already in `env_collector.yml` file). 

A short installation guide for Tesseract OCR can be found as follows:

1) Go to : https://github.com/UB-Mannheim/tesseract/wiki

2) Download and instll "Tesseract installer for Windows" according to your OS system version. 

3) Update System PATH (if necessary): If Tesseract's installation directory isn't automatically added to your system's PATH, you'll need to do it manually. To do this:

 · Right-click on `This PC` or `My Computer` on your desktop or File Explorer and select `Properties`.
 · Click on `Advanced system settings`.
 · In the System Properties window, go to the `Advanced` tab and click on `Environment Variables`.
 · Under `System variables`, scroll and find the `Path` variable, then click `Edit`.
 · Add the path to the Tesseract installation (e.g., `C:\Program Files\Tesseract-OCR`).
 · Click `OK` to close each window.

4) Test the Installation: You can test if Tesseract is correctly installed by running a Python script that imports pytesseract and prints its version.

```bash
import pytesseract
print(pytesseract.get_tesseract_version())
```

## Mercadona ticket expenses

The first idea is to collect all the tickets at email location and then generate expenses charts.