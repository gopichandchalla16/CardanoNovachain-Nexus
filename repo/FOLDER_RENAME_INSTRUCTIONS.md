# Folder Rename Instructions

## Current Structure
```
C:\Users\gopic\repo\
├── crewai-masumi-quickstart-template/  ← OLD NAME
└── ... (other files)
```

## New Structure
```
C:\Users\gopic\repo\
├── CognitoSync-NovachainNexus/  ← NEW NAME
└── ... (other files)
```

## Steps to Rename the Folder

### Option 1: Using Windows File Explorer (Easiest)
1. Open File Explorer
2. Navigate to: `C:\Users\gopic\repo\`
3. Right-click on folder `crewai-masumi-quickstart-template`
4. Select "Rename"
5. Type the new name: `CognitoSync-NovachainNexus`
6. Press Enter

### Option 2: Using PowerShell (Command Line)
Open PowerShell and run:
```powershell
cd C:\Users\gopic\repo
Rename-Item -Path "crewai-masumi-quickstart-template" -NewName "CognitoSync-NovachainNexus"
Verify with: Get-ChildItem
```

### Option 3: Using Command Prompt
Open CMD and run:
```cmd
cd C:\Users\gopic\repo
ren crewai-masumi-quickstart-template CognitoSync-NovachainNexus
dir
```

## After Renaming

Update any references in your configuration:

### For Backend:
- Update terminal working directory to: `C:\Users\gopic\repo\CognitoSync-NovachainNexus`
- Start backend: `cd C:\Users\gopic\repo\CognitoSync-NovachainNexus && python -m uvicorn main_cognito_sync:app --reload --port 5000`

### For Frontend:
- Update to: `C:\Users\gopic\repo\CognitoSync-NovachainNexus\react-frontend`
- Start frontend: `cd C:\Users\gopic\repo\CognitoSync-NovachainNexus\react-frontend && npm start`

### For Article Server:
- Update to: `C:\Users\gopic\repo\CognitoSync-NovachainNexus`
- Start server: `python C:\Users\gopic\repo\CognitoSync-NovachainNexus\serve_article.py`

## Complete Startup Commands (After Rename)

**Terminal 1 - Backend (Port 5000):**
```powershell
cd C:\Users\gopic\repo\CognitoSync-NovachainNexus
python -m uvicorn main_cognito_sync:app --reload --port 5000
```

**Terminal 2 - Frontend (Port 3000):**
```powershell
cd C:\Users\gopic\repo\CognitoSync-NovachainNexus\react-frontend
npm start
```

**Terminal 3 - Article Server (Port 8888):**
```powershell
python C:\Users\gopic\repo\CognitoSync-NovachainNexus\serve_article.py
```

Then access:
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:5000
- Article Server: http://localhost:8888/example_article.html

## Verification Checklist

After renaming:
- [ ] Folder renamed successfully
- [ ] Backend starts without errors
- [ ] Frontend compiles without errors
- [ ] All APIs responding
- [ ] No import/path errors in console

---

**Note:** All functionality remains exactly the same - this is just a naming change for better project identification!
