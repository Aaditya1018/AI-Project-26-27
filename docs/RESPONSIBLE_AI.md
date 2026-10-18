# SafeStack AI — Responsible AI Safeguards & Labor Protection Architecture

## 1. Principles of Responsible Computer Vision

SafeStack AI was designed from inception to prevent equipment and process failure, **not to perform punitive employee surveillance**.

### Core Commitments
1. **Zero Biometric Identification**: The platform does not run face recognition, emotional state classification, or personal identity tracking.
2. **Data Minimisation at the Edge**: Video processing occurs at the edge (on local industrial PCs or NVIDIA Jetson units). Full-resolution facial data is anonymized immediately before any frame is recorded or displayed.
3. **Ergonomic Coaching vs Disciplinary Tracking**: SafeStack AI scores behaviors, not individuals. Incidents are aggregated into bay-level process health, equipment availability, and ergonomic risk metrics.
4. **Human-in-the-Loop Governance**: Automated AI alerts do not trigger automated penalties. Supervisors validate incidents, confirm whether damage was avoided, and record constructive coaching feedback.

---

## 2. Privacy Shield Architecture

The system provides three operational privacy modes selectable by authorized supervisors:

```
[ Camera Feed ] ---> [ Edge YOLO Detector ]
                             |
                             +---> [ Worker Detected ]
                                          |
                        +-----------------+-----------------+
                        |                                   |
                [ Mode: Face Blur ]             [ Mode: Silhouette Avatar ]
                Heavy Gaussian Blur             Worker masked with anonymous
                over head region                emerald green ergonomic silhouette
                        |                                   |
                        +-----------------+-----------------+
                                          |
                                          v
                         [ SafeStream to Supervisor HUD ]
```

- **Face Anonymizer (Default)**: Automatically applies a $(31 \times 31)$ Gaussian kernel blur across the top $28\%$ of every person bounding box.
- **Silhouette Avatar Mode**: Replaces the worker's visual form with a clean, anonymous silhouette avatar, preserving posture kinematics while eliminating all identifying features.
- **Role-Based Access Control (RBAC)**:
  - `Supervisor`: Review alerts, mark damage prevented, add coaching notes, query conversational assistant.
  - `Bay Lead`: View live bay status, receive real-time audio chimes, inspect coaching nudges.
  - `Auditor`: Export anonymized compliance and damage reduction summaries.
