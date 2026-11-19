# COMS Bug Report & Windows Patch Instructions

## Overview
This document outlines bugs identified in COMS operation and provides instructions for Windows agents to re-register and patch the COMS version accordingly.

## Key Findings
1. **Silent Drops on Publish**: Command `send` may not reliably transmit messages without subscribers.
   - **Fix Required**: Include QoS parameters in the publish command.
2. **Field Loss during Registration**: Omitting fields leads to unintended behavior. 
   - **Correction**: Modify registration logic to ensure all necessary fields are assigned.

## Windows Re-registration Instructions
- Open PowerShell and run the following commands:

```powershell
# For learning about this COMS bus
powershell -File E:\AGENT_FOLDERFRAMEWORK\COMMUNICATION\coms.ps1 learn

# Register new agents ensuring to provide all relevant fields
powershell -File E:\AGENT_FOLDERFRAMEWORK\COMMUNICATION\coms.ps1 register -Agent <your-role> --todo "<your-todo>" --done "<your-done>" --goal "<your-goal>" 
```

## Conclusion
Following these steps is essential to maintain effective communication and ensure that the COMS component functions as intended.

## Next Steps
Please implement these changes promptly to avoid further disruptions and ensure operational integrity.
