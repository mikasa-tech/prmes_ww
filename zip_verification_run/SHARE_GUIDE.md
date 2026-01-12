# Sharing Your Project via WhatsApp

This guide explains how to package your project files and send them to someone through WhatsApp.

## 1. How to Zip Your Files (Windows)

Zipping compresses your files into a single `.zip` file, making it easier to send many files at once.

### Option A: Manual (Mouse)
1.  Open your project folder in **File Explorer**.
2.  Press `Ctrl + A` to select all files (or select the specific files you want).
3.  **Right-click** on any selected file.
4.  Select **Compress to ZIP file** (Windows 11) or **Send to > Compressed (zipped) folder** (Windows 10).
5.  A new file (e.g., `required.zip`) will appear. You can rename it.

### Option B: Automated (Command Prompt or PowerShell)
If you are using **Command Prompt (CMD)**, use this command:
```cmd
powershell -Command "Compress-Archive -Path * -DestinationPath project_backup.zip -Force"
```

If you are using **PowerShell**, use this command:
```powershell
Compress-Archive -Path * -DestinationPath project_backup.zip -Force
```

---

## 2. How to Send via WhatsApp

### Using WhatsApp Web or Desktop
1.  Open [WhatsApp Web](https://web.whatsapp.com/) or the WhatsApp Desktop app.
2.  Open the chat for the person you want to send the files to.
3.  Click the **+** (plus) icon or the **Paperclip** icon next to the message box.
4.  Select **Document**.
5.  Navigate to your project folder and select the `.zip` file you created (or individual files like your PPTX reports in the `exports` folder).
6.  Click **Open** and then **Send**.

---

## 3. Important Files to Share
If you don't want to send the whole project, these are usually the most important:
-   **Reports:** `required/exports/PMES_Presentation.pptx`
-   **Data:** `required/Class_data1.xlsx` or `required/app.db` (the database)
-   **Source Code:** `required/app.py` and `required/README.md`

---

## Troubleshooting: "Cloud operation was not completed before time-out period"

If you see this error, it's because **OneDrive** hasn't actually downloaded the files to your computer yet (they are "online only"). 

### How to Fix:
1.  **Right-Click** your project folder (`prmes_ww`).
2.  Select **Always keep on this device**.
3.  Wait for the green checkmarks to appear on all files, then try zipping again.

### Quick Workaround (Recommended - Small & Safe):
The previous zip file was too large (~400MB) because it included technical environment files. This command creates a tiny zip with **only** your project code and reports.

Copy and paste this entire line:
```cmd
powershell -Command "$projDir = 'c:\Users\asus\OneDrive\Documents\prmes_w\prmes_ww'; $tempDir = 'C:\prmes_temp'; New-Item -ItemType Directory -Path $tempDir -Force; Copy-Item -Path \"$projDir\required\" -Destination $tempDir -Recurse -Force; Copy-Item -Path \"$projDir\SHARE_GUIDE.md\" -Destination $tempDir -Force; $desktop = [Environment]::GetFolderPath('Desktop'); Compress-Archive -Path \"$tempDir\*\" -DestinationPath \"$desktop\project_ready.zip\" -Force; Remove-Item -Path $tempDir -Recurse -Force"
```
This will result in a much smaller file on your **Desktop** that Windows won't block.

---

## What to do if Windows still says "Access Denied"?
Sometimes Windows blocks zip files created by scripts for security.
1.  **Right-click** the `project_ready.zip` file on your Desktop.
2.  Select **Properties**.
3.  In the **General** tab, look for a section called **Security** at the bottom.
4.  Check the box that says **Unblock**.
5.  Click **OK**.

---

## Professional "Clean" Share (Recommended)
If you want to send a professional version of your project that **only includes essential files** (no technical debug files or backups), use this command:

```cmd
powershell -Command "$projDir = 'c:\Users\asus\OneDrive\Documents\prmes_w\prmes_ww\required'; $tempDir = 'C:\temp_clean'; New-Item -ItemType Directory -Path $tempDir -Force; $files = @('app.py', 'models.py', 'review_config.py', 'upload_helpers.py', 'pdf_template.py', 'comprehensive_pdf_template.py', 'utils.py', 'requirements.txt', 'app.db', 'college_logo.png', 'README.md'); foreach ($f in $files) { if (Test-Path \"$projDir\$f\") { Copy-Item -Path \"$projDir\$f\" -Destination $tempDir -Force } }; $folders = @('templates', 'exports'); foreach ($fol in $folders) { if (Test-Path \"$projDir\$fol\") { Copy-Item -Path \"$projDir\$fol\" -Destination $tempDir -Recurse -Force } }; $desktop = [Environment]::GetFolderPath('Desktop'); Compress-Archive -Path \"$tempDir\*\" -DestinationPath \"$desktop\project_pro.zip\" -Force; Remove-Item -Path $tempDir -Recurse -Force"
```
This will create a very clean **`project_pro.zip`** on your Desktop. This is the best version to share!

---

## 4. How to Run (for the Receiver)
> [!IMPORTANT]
> **DO NOT** double-click `app.py` inside the zip file. You **MUST** extract the folder first. 
> - If you get **"ModuleNotFoundError"**: It means you didn't extract.
> - If you get **"TemplateNotFound"**: It means you didn't extract the `templates` folder.

### Step-by-Step:
1.  **Extract**: Right-click `project_pro.zip` -> **Extract All...** -> Click **Extract**.
2.  **Open Folder**: Open the new folder named `project_pro`.
3.  **Run**: Inside that folder (where you see `app.py`), run `python app.py`.
